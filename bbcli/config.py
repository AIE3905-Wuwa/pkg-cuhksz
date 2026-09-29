"""配置与路径：一切可变项集中于此。

凭据/会话只存用户目录（默认 ~/.bb-cli，BB_CLI_HOME 可覆写），
绝不写入当前工作目录或任何仓库。环境变量优先于配置文件。
"""

from __future__ import annotations

import json
import os
import stat
from pathlib import Path

BB_HOST = "https://bb.cuhk.edu.cn"
ADFS_CLIENT_ID = "4b71b947-7b0d-4611-b47e-0ec37aabfd5e"
ADFS_REDIRECT_URI = BB_HOST + "/webapps/bb-SSOIntegrationOAuth2-BBLEARN/authValidate/getCode"
ADFS_AUTHORIZE_URL = (
    "https://sts.cuhk.edu.cn/adfs/oauth2/authorize"
    "?response_type=code"
    f"&client_id={ADFS_CLIENT_ID}"
    f"&redirect_uri={ADFS_REDIRECT_URI}"
)
IMPERSONATE = "chrome124"  # 站点做 TLS 客户端指纹检测，普通 OpenSSL 握手会被拒
REQUEST_TIMEOUT = 30

ENV_HOME = "BB_CLI_HOME"
ENV_USERNAME = "BB_CLI_USERNAME"
ENV_PASSWORD = "BB_CLI_PASSWORD"
ENV_PROXY = "BB_CLI_PROXY"
ENV_DEBUG = "BB_CLI_DEBUG"  # 设为目录路径则落调试 HTML


def bb_home() -> Path:
    root = os.environ.get(ENV_HOME)
    home = Path(root).expanduser() if root else Path.home() / ".bb-cli"
    home.mkdir(parents=True, exist_ok=True)
    return home


def config_path() -> Path:
    return bb_home() / "config.json"


def session_path() -> Path:
    return bb_home() / "session.json"


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
            "缺少凭据：用 `bb-cli login` 交互录入，或设 "
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
