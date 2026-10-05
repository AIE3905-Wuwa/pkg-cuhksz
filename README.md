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
| `schedule [--days]` | 我的每周课程表：本周事件 + 学期课程总表；`--days` 附学生中心页的**星期归属课表**（Mo/Tu/We…） |
| `grades [--term 子串]` | 查看我的成绩：按学期课程行（课号/学分/评分制/等级/绩点），缺省取最新学期 |
| `history` | 课程历史全量：课号/课名/学期/等级/学分（页面直出，无需交互） |
| `appt [--term 子串]` | 注册日期：选课窗口（起止时刻）+ 学分上下限 |
| `exam [--term 子串]` | 考试安排（当前学期未发布时为空） |
| `transcript [--lang eng\|chi\|ge-edu] [-o F]` | 下载非官方成绩单官方 PDF（View Report → FILEDB_XMLP PDF，AES 空密码） |
| `identity` | 学籍身份结构化：姓名/学号/邮箱/holds（prsnldata 页）+ 学院/专业/入学/学制（transcript PDF，需 pypdf） |
| `dpr` | 学位进度报告（当前需 Request Audit 生成，如实输出页面现状） |
| `center` / `assignments` | 学生中心页 / 按作业查成绩（文本摘要，assignments 常无数据） |
| `raw <url> [--post --action IC名 --set k=v] [--file F]` | GET/POST 透传——POST 导航原语（issue #6 ①）：下拉跳转、View Report 类页面经 ICAction POST 可达，探针不再止步于 GET |

**term 交互机制**（grades/appt/exam）：GET 搜索页 → 解析学期 radio（`SSR_DUMMY_RECV1$sels$0`，页面倒序最新在前）→ POST `win0` 表单（ICAction=Continue 按钮 `DERIVED_SSS_SCT_SSR_PB_GO`）→ 结果页。此 POST 是查询动作（等同网页上点"继续"），不改变任何数据。

## 已知边界（2026-10-05 实测）

- `exam` 考试安排：机制与 grades 同款（term POST），当前学期未发布时结果为空——发布后自然出数据。
- `assignments`（按作业查成绩）直击显示 "There is no information"，留观察；按学期成绩走 `grades`。
- 学费账单（Finances 类）与购物车只读视图未登记（菜单可见，`raw --post` 可先行探路）。
- `dpr` 报告当前显示 "not available"——需 Request Audit（提交报表任务）生成后方可查看；该按钮属提交类动作，v0.3 不自动执行，待裁定。
- `identity` 的 PDF 侧字段依赖 pypdf（可选依赖，缺失时该组字段标 unavailable）。
- 页面正文含学生真实姓名等隐私——CLI 输出仅落终端/本机，**绝不入仓库**。
- 学校升级 PIA 或改登录页会断链：带 `SIS_CLI_DEBUG=<目录>` 重跑可留现场。
- **写操作（选课/退课/换课/提交）刻意不提供**——误操作有真实学籍后果；如确需，须用户明示并另行设计。

## Git Bash 注意

以 `/` 开头的 raw 路径会被 MSYS 改写，用 `MSYS_NO_PATHCONV=1` 前缀或去掉首斜杠（相对路径）。
