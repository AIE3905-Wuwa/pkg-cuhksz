# sis-cli — CUHK-SZ SIS 只读 CLI 连接器

`sis.cuhk.edu.cn`（Oracle PeopleSoft Campus Solutions）的命令行连接器：**纯只读数据面，无 agent 逻辑、无 MCP、无监控**——给上层（wiki 域插件 / 人工 / 脚本）当事实接口用。技术路线与登录实证承 bb-cli（同一 ADFS `sts.cuhk.edu.cn`、`cuhksz\` 域前缀规则同源）；PeopleSoft 侧登录与组件访问按 2026-10-05 实地逆向编写。

## 安装

```bash
cd connectors/sis-cli
python -m venv .venv
.venv/Scripts/pip install -e .   # Windows；*nix 为 .venv/bin/pip
.venv/Scripts/sis-cli --help
```

依赖仅 `curl_cffi`（Chrome TLS 指纹）与 `beautifulsoup4`。

## 认证（ADFS OAuth2 → PeopleSoft 会话）

流程（全部 HTTP 可复刻，无浏览器）：

1. `sts.cuhk.edu.cn/adfs/oauth2/authorize`（client_id 注册于 SIS）→ ADFS 表单登录（与 bb-cli 同源：单次 POST，学号自动补 `cuhksz\` 前缀）；
2. 回调 `sis.cuhk.edu.cn/sso/dologin.html?code=…` 静态页——照抄其 JS 表单，POST `/psp/csprd/?cmd=login&languageCd=…&code=…`（固定服务账号 `CUSZ_SSO_LOGIN` + 随机密码；POST 前先 GET 该地址预热 `PSJSESSIONID`）；
3. PeopleSoft 后端以 code 换会话，`PS_TOKEN` 落地即成功。

凭据与会话只存本机 `~/.sis-cli/`（`SIS_CLI_HOME` 可覆写）：`config.json`（凭据，权限 0600）+ `session.json`（cookie jar）。**绝不写入任何仓库。** 免落盘：环境变量 `SIS_CLI_USERNAME` / `SIS_CLI_PASSWORD` 或 `sis-cli login --no-store`。

**会话短寿**：实测 `PS_TOKEN` 约 5 分钟过期，且 `PORTAL-PSJSESSIONID` 随响应滚动换发。CLI 策略：每次请求后写穿 session.json；组件访问遇登录壳自动重登一次并重放（ADFS 会话常驻，重登成本 ≈ 两次请求）。

## PeopleSoft 访问要点（2026-10-05 实证）

- **PS_DEVICEFEATURES cookie**：壳页 JS 以它判别浏览器环境，缺失则 psc 直击永远只回 bootstrap 壳。格式 = JSON 剥 `{}`/引号、逗号换空格（见 `/csprd/signin.js`）。CLI 在会话上恒种一个典型桌面 Chrome 值。
- **psc/psp 乒乓**：直击 `/psc/…/c/组件` 先回壳（`self.location` 指向 psp 版 URL），跟随后可达真身或门户框架页（`ptifrmtgtframe` TargetContent iframe，取其 src 再 GET）。
- **PORTALPARAM_PTCNAV**：学生角色的权限判定带导航上下文——psc 直击必须带 `?PORTALPARAM_PTCNAV=<HC_…>`，缺它报 not authorized（实证：SSR_STUDENT_SCHEDULE 无 PTCNAV 被拒；SSR_SSENRL_SCHD_W 带则通）。FolderPath/EOPP 长参数可全省。
- 组件无公开 REST：数据在 PIA HTML 内，逐组件写解析。

## 命令（全只读，`--format text|json`）

| 命令 | 用途 |
|---|---|
| `status` | 会话状态与可用组件清单 |
| `login` / `logout` | 交互登录（`--no-store` 免落盘）/ 登出清本地 |
| `schedule` | 我的每周课程表：本周事件（编号/类型/时段/教室）+ 学期课程总表（**全解析**） |
| `grades` | 查看作业与成绩（v0.1 文本摘要；组件需 term 交互，结构化解析 v0.2） |
| `center` / `history` / `appt` | 学生中心 / 课程历史 / 注册日期（v0.1 文本摘要） |
| `raw <url> [--file F]` | 任意 GET 透传——新需求先走这里验证，再封命令 |

## 已知边界（2026-10-05 实测）

- `schedule` 的星期网格归属未做（PeopleSoft 周视图 DOM 无列锚点，v0.2 议）；事件清单已按四元组去重。
- `grades`（SS_LAM_STD_GR_LST）当前直接访问显示 "There is no information"——需 term 查询交互（POST ICSID 表单），v0.2 补。
- 学费账单、考试计划、购物车等组件未登记（菜单可见，`raw` 可先行探路）。
- 页面正文含学生真实姓名等隐私——CLI 输出仅落终端/本机，**绝不入仓库**。
- 学校升级 PIA 或改登录页会断链：带 `SIS_CLI_DEBUG=<目录>` 重跑可留现场。
- **写操作（选课/退课/换课/提交）刻意不提供**——误操作有真实学籍后果；如确需，须用户明示并另行设计。

## Git Bash 注意

以 `/` 开头的 raw 路径会被 MSYS 改写，用 `MSYS_NO_PATHCONV=1` 前缀或去掉首斜杠（相对路径）。
