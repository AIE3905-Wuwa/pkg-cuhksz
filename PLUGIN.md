# bb：BB 课程域

外域实例之一：把 LMS（Blackboard，首例 CUHK-SZ）接为 wiki 外信息源。本插件是**基石声明**——只立领地、结构、身份证明、写模型与信任模型；课件投影细则（代理页 / 清单密度）归后续 bb_map（团队待议），bbcli 用法与位置归 bbcli skill，本插件不固化。真相在 BB 服务器，本地 `bb/` 容器是拉取物仓储：全量物化放行（2026-10-01 裁定——BB 上的文件基本都会用上，存储是唯一成本）；wiki 侧属地取蒸馏密度，不逐文件立页。

## Structure

- 双侧同构 `<term>/<course>/`：外 `bb/<term>/<course>/`（课件保留源侧目录树、提交件 `submissions/`），内 `wiki/bb/<term>/<course>/`
- 目录名人类可读：term 名（如 `2610UG`）+ 课程代码（如 `AIE3005`）——恰为 bbcli 查询参数形态，人机两用；machine id（term_id / course_id）落属地身份页 frontmatter；同期同代码尾缀 course_id 消歧；停用课标 status: deprecated 不删
- 域根速写页 `wiki/bb/inbox.md`：近窗公告蒸馏 + 临近截止 + 未交提醒（行标课程），整页可再生、短 TTL；frontmatter 兼域配置（`terms` 块映射：现役学期与冻结标记）——不另立声明页（2026-10-01 裁定）
- 属地页面形态 v0.1 最小集：课程身份页（每课必有，身份证明载体）；公告 / 作业等内容页形态留待真实使用浮现

## Invariants

- 契约六问：外领地 = bb.cuhk.edu.cn（连接器 bb-cli 可达）；落地 = 自立容器 `bb/`（双判据：课件只增 vs 信息页可再生的写模型分叉 + term/course 层级由源规定的结构刚性）；身份证明 = 身份页 `bb` 块映射 term_id / course_id ↔ 属地目录一比一；属地 = `wiki/bb/`；写模型 = 外侧只增、删改自由属于人，内侧机械区可再生覆写 + 沉淀区只增；信任 = 天花板 machine-confirmed，速写与快照挂 stale_after = 拉取日 + TTL（默认 1 天，速写页可覆写），agent 即同步器
- 课件物化后即本地终态资产：豁免 TTL（vault 式不可变），失配以哈希对账
- 只读纪律：连接器纯只读数据面，提交作业等写动作不入本域
- 凭据纪律：会话与凭据只存本机（`~/.bb-cli/`，BB_CLI_HOME 可覆写），绝不入库
- 隐私红线：课程、成绩与提交数据属实例数据，不入框架仓库与 test-repo；roster 不拉（他人隐私，非本域对象）
- 单向派生只出不回：行动项→todo、课业日程→calendar、高价值结论→notes（回链属地页）

## Changelog

- 0.1（2026-10-01）立设：基石声明（email 形——契约活 manifest，无命令无脚本）；速写页兼域配置、全量物化放行均用户裁定；投影细则归 bb_map 后议
