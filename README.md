# bb-cli — CUHK-SZ Blackboard 只读 CLI 连接器

`bb.cuhk.edu.cn`（Blackboard Learn Classic 3900.39）的命令行连接器：**纯只读数据面，无 agent 逻辑、无 MCP、无监控**——给上层（wiki 域插件 / 人工 / 脚本）当事实接口用。技术路线承 bbwatch 的实证（curl_cffi 指纹 + ADFS OAuth2 + 官方 REST API），登录细节按 2026-09-29 实地逆向重写。

## 安装

```bash
cd connectors/bb-cli
python -m venv .venv
.venv/Scripts/pip install -e .   # Windows；*nix 为 .venv/bin/pip
.venv/Scripts/bb-cli --help
```

依赖仅 `curl_cffi`（Chrome TLS 指纹——站点拒绝普通 OpenSSL 握手）与 `beautifulsoup4`。

## 认证

- `bb-cli login`：交互录入学号与密码（密码不回显）。学号自动补 `cuhksz\` 域前缀（对齐登录页定制 JS）；已含 `@` 或 `\` 的输入不改写。
- 凭据与会话只存本机用户目录 `~/.bb-cli/`（`BB_CLI_HOME` 可覆写）：`config.json`（凭据，权限 0600）+ `session.json`（cookie jar）。**绝不写入任何仓库。**
- 免落盘：`--password-env VAR`（或环境变量 `BB_CLI_PASSWORD`）+ `--no-store`。
- 会话过期自动重登一次并重放（401 触发，凭据来自配置/环境）。
- `bb-cli logout` 登出并清本地会话。

## 命令（全只读，JSON 默认，`--format text` 人读）

| 命令 | 用途 |
|---|---|
| `whoami` / `status` / `terms` | 身份、会话状态、学期表 |
| `courses [--term 子串]` | 我的课程（`--format text` 一行一课） |
| `tree <课程> [--depth N] [--no-attachments]` | 内容树（folder/lesson/assignment，叶带附件名） |
| `files <课程> [--match 正则]` | 课件清单（全路径 + 附件 id/文件名/mime；`--match` 作用路径与文件名） |
| `fetch <课程> [--match 正则] [--since YYYY-MM-DD] [-o 目录] [--dry-run]` | 下载课件，保留 `课程/目录树` 结构；`--match` 作用路径与文件名；已存在跳过；同名附件尾缀附件 id |
| `announcements [--course 子串\|all] [--limit N] [--html]` | 公告（默认扫全部课程，正文转纯文本） |
| `dues [--from D] [--to D] [--course C]` | 跨课程截止（日历端点，一份拿全） |
| `assignments <课程>` | 作业清单：截止 × 满分 × 我的提交状态（NeedsGrading/Graded/None） |
| `grades [课程] [--due-only]` | 成绩册列 × 我的状态（默认全部课程） |
| `roster <课程>` | 课程成员（含 lastAccessed，注意隐私） |
| `raw GET <路径> [--q k=v]...` | 任意 REST GET 透传——新需求先走这里，验证后再封命令 |

课程参数接受：课程 id（`_18030_1`）、课程代码或名称子串（`AIE3005`）；歧义时报候选清单。

**Git Bash 注意**：以 `/` 开头的 raw 路径会被 MSYS 改写，用 `MSYS_NO_PATHCONV=1` 前缀或去掉首斜杠（相对路径）。

## 已知边界（2026-09-29 实测）

- 学生会话下 404：`gradebook/attempts`、`discussion/forums`、`users/me/memberships`、`tasks`、`gradebook/grades`——讨论板与作业提交若要做须走 DOM 路线（参考 bb-mcp），v1 不含。
- 仅 Classic（JSP）课程；Ultra 课程未验证。
- 写操作（提交作业/发公告）刻意不提供——上层如需，须用户明示并另行设计。
- 登录失败页的错误文案常驻 HTML 模板，判定只能靠状态推进；若学校改版登录页，带 `BB_CLI_DEBUG=<目录>` 重跑可留现场。

## 致谢

- [jsyzlbw/bbwatch](https://github.com/jsyzlbw/bbwatch)：curl_cffi 指纹路线与 REST 端点实证。
- [changshenhan/bb-mcp](https://github.com/changshenhan/bb-mcp)：端点与站点行为参考。
