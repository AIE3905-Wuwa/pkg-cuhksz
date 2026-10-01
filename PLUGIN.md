# bb-map：bb 域映射法则

bb 域的映射法则（mapping 之于 vault；bb 域内插件，契约见 bb 插件）。**规范化投影**：`bb/` 保源形（对账前提），属地 `wiki/bb/<term>/<course>/` 统一规范形四桶——无论源侧目录长什么样。桶名 v0.1 沿用团队现名（`lec&tut` / `work` / `attachments`），改名后置（2026-10-01 裁定）。

## Structure

- `info.md`——课程身份页兼总览（一课一锚点）：frontmatter `bb` 块映射（term_id / course_id，身份证明归 bb 插件）+ `## 基本信息`（师资 / TA / 分组 / 评分构成——机械蒸馏节，可再生）+ `## 备注`（沉淀区只增）
- `lec&tut/`——课件桶：1:1 代理（每文件一页，两形分区——机械区 raw 链接、沉淀区听课笔记只增）；默认姿态，细则待组员后补
- `work/`——学业事务聚合页：每作业 / 考试 / quiz 一页（文件名 = 作业名原形清洗），四要素归一——要求 / 参考（可选）/ 提交 / 结果
- `attachments/`——附件 1:1 代理（每附件一页，平铺；细分结构等真实内容浮现再说）
- 落位判据：**有成绩册列或提交动作 → work/**；老师发布的非讲义资产 → attachments/；讲义课件 → lec&tut/；结构事实（TA / 分组 / 评分构成）入 info.md 正文，不作附件

## Invariants

- 两形分区制（lark 档案页先例）：属地内容页一律机械区（frontmatter + 可再生节，对账覆写）+ 沉淀区（`## 备注` / `## 复盘` / 课件页笔记，只增）；重建不得触碰沉淀区
- 对账：1:1 页 `raw_file` / `raw_sha256` ↔ `bb/` 文件一比一（词形语义同 mapping，指向 bb/）；work 聚合页 `raw` 块映射（角色→bb/ 路径，多源）；源侧消失标 `status: deprecated` 不删
- work 机械区：`work` 块映射（due / submitted_at / score / possible / status / column_id / attempt_id——API 快照字段）
- 命名：原名保留（忠实），仅清洗文件系统非法字符；同桶重名尾缀 column_id 短形（lark-im 先例）
- 信任：机械区含 API 快照的（work 结果、info 基本信息）挂 `stale_after` = 拉取日 + TTL（继承 bb 域）；纯本地对账代理（lec&tut / attachments）无 TTL——物化后即终态资产
- 页面 type 复用 `bb`（lark 域内插件共用 type: lark 先例），不扩注册表 type 值集
- 骨架是规约非预建空目录：桶随内容自然成形，index 对空子树自有可见性规则

## Changelog

- 0.1（2026-10-01）立设：基石续篇，契约活 manifest 无命令（命令随后出）；四桶命名沿团队现名、work / attachments / info 细则落地、lec&tut 默认 1:1 待组员细则；判据句与两形分区经讨论收敛
