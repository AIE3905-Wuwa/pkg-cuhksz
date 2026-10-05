"""配置与路径：一切可变项集中于此。

凭据/会话只存用户目录（默认 ~/.sis-cli，SIS_CLI_HOME 可覆写），
绝不写入当前工作目录或任何仓库。环境变量优先于配置文件。
"""

from __future__ import annotations

import json
import os
import stat
from pathlib import Path

SIS_HOST = "https://sis.cuhk.edu.cn"
ADFS_CLIENT_ID = "3f09a73c-33cf-49b8-8f0c-b79ea2f3e83b"
ADFS_REDIRECT_URI = SIS_HOST + "/sso/dologin.html"
ADFS_AUTHORIZE_URL = (
    "https://sts.cuhk.edu.cn/adfs/oauth2/authorize"
    "?response_type=code"
    f"&client_id={ADFS_CLIENT_ID}"
    f"&redirect_uri={ADFS_REDIRECT_URI}"
)
# PeopleSoft 会话仅分钟级（PS_TOKENEXPIRE 实测 ~5 分钟）：跨进程复用 jar 不可靠，
# 命令内轻登录为主、jar 复用为辅。
SESSION_SOFT_TTL = 240  # 秒；超过即视为过期，直接重登
IMPERSONATE = "chrome124"
REQUEST_TIMEOUT = 40

# PeopleSoft 壳页 JS 以 PS_DEVICEFEATURES cookie 判别浏览器环境；
# 缺失则 psc 直击永远只回 bootstrap 壳。格式 = JSON 剥 {}/引号、逗号换空格
# （见 /csprd/signin.js 的 ptDeviceFeatures），值为典型桌面 Chrome 特征。
PS_DEVICEFEATURES = (
    "width:1920 height:1080 pixelratio:1 touch:0 geolocation:1 websockets:1 "
    "webworkers:1 datepicker:1 dtpicker:1 timepicker:1 dnd:1 sessionstorage:1 "
    "localstorage:1 history:1 canvas:1 svg:1 postmessage:1 hc:0"
)

# 学生角色可用组件（2026-10-05 双实证：浏览器菜单导航 + HTTP psc+PTCNAV 直击）。
# PTCNAV 是权限判定的导航上下文——缺它即报 not authorized。
COMPONENTS = {
    # 直出组件（GET 即内容）
    "schedule": ("SA_LEARNER_SERVICES.SSR_SSENRL_SCHD_W.GBL", "HC_SSR_SSENRL_SCHD_W_GBL"),
    "center": ("SA_LEARNER_SERVICES.SSS_STUDENT_CENTER.GBL", "HC_SSS_STUDENT_CENTER"),
    "history": ("SA_LEARNER_SERVICES_2.SSS_MY_CRSEHIST.GBL", "HC_SSS_MY_CRSEHIST_GBL2"),
    # term 交互组件（GET 搜索页 → POST 学期 radio + Continue）
    "grades": ("SA_LEARNER_SERVICES.SSR_SSENRL_GRADE.GBL", "HC_SSR_SSENRL_GRADE_GBL"),
    "appt": ("SA_LEARNER_SERVICES.SSR_SSENRL_APPT.GBL", "HC_SSR_SSENRL_APPT"),
    "exam": ("SA_LEARNER_SERVICES.SSR_SSENRL_EXAM_L.GBL", "HC_SSR_SSENRL_EXAM_L_GBL"),
    "list_schedule": ("SA_LEARNER_SERVICES.SSR_SSENRL_LIST.GBL", "HC_SSR_SSENRL_LIST_GBL"),
    # 按作业查成绩（View My Assignments）——实证常显 "no information"，留观察
    "assignments": ("SA_LEARNER_SERVICES.SS_LAM_STD_GR_LST.GBL", "HC_SS_LAM_STD_GR_LST_GBL1"),
}
# 需要选学期再 Continue 的组件（统一交互：radio SSR_DUMMY_RECV1$sels$0 + DERIVED_SSS_SCT_SSR_PB_GO）
TERM_COMPONENTS = {"grades", "appt", "exam", "list_schedule"}

ENV_HOME = "SIS_CLI_HOME"
ENV_USERNAME = "SIS_CLI_USERNAME"
ENV_PASSWORD = "SIS_CLI_PASSWORD"
ENV_PROXY = "SIS_CLI_PROXY"
ENV_DEBUG = "SIS_CLI_DEBUG"  # 设为目录路径则落调试 HTML


def sis_home() -> Path:
    root = os.environ.get(ENV_HOME)
    home = Path(root).expanduser() if root else Path.home() / ".sis-cli"
    home.mkdir(parents=True, exist_ok=True)
    return home


def config_path() -> Path:
    return sis_home() / "config.json"


def session_path() -> Path:
    return sis_home() / "session.json"


def _restrict(path: Path) -> None:
    """best-effort 收紧权限（POSIX 0600；Windows 仅继承用户目录 ACL）。"""
    try:
        path.chmod(stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass


def load_config() -> dict:
    p = config_path()
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_config(cfg: dict) -> None:
    p = config_path()
    p.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    _restrict(p)


def resolve_credentials(cfg: dict, cli_user: str | None, password_env: str | None) -> tuple[str, str]:
    """凭据解析优先级：命令行/环境变量 > 配置文件。密码永不在日志中回显。"""
    username = cli_user or os.environ.get(ENV_USERNAME) or cfg.get("username")
    password = None
    if password_env:
        password = os.environ.get(password_env)
    elif os.environ.get(ENV_PASSWORD):
        password = os.environ.get(ENV_PASSWORD)
    else:
        password = cfg.get("password")
    if not username or not password:
        raise SystemExit(
            "缺少凭据：用 `sis-cli login` 交互录入，或设 "
            f"{ENV_USERNAME}/{ENV_PASSWORD}，或 --password-env 指定变量名"
        )
    return username, password


def proxy() -> str | None:
    return os.environ.get(ENV_PROXY) or None


def debug_dir() -> Path | None:
    d = os.environ.get(ENV_DEBUG)
    if not d:
        return None
    p = Path(d).expanduser()
    p.mkdir(parents=True, exist_ok=True)
    return p
