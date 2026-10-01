# bb-map：bb 域映射法则

bb 域的映射法则（mapping 之于 vault；bb 域内插件，契约见 bb 插件）。**规范化投影**：`bb/` 保源形（对账前提），属地 `wiki/bb/<term>/<course>/` 统一规范形四桶——不论源目录如何存储。映射与理解解耦：代理是「bb 资产在 md 世界的代表」，登记 + 简要介绍起步，深度摘要为可选增强。桶名 v0.4 终裁：`courseware`（原 lec&tut）/ `assessments`（原 work）/ `attachments`（2026-10-01 裁定）。

## Structure

- `info.md`——课程信息页兼身份页（一课一锚点）：frontmatter `bb` 块映射（term_id / course_id，身份证明归 bb 插件）+ 正文机械蒸馏节（教学大纲 / 师资 / TA / 分组 / 评分构成 / 考试时间）+ `## 备注`（沉淀区只增）。边界：info 存「何时有何事」（日程视角），被评分事务全要素归 assessments 页
- `courseware/<单元名>.md`——知识点页：每个内容单元一份（内容单元 = bb/ 中的目录「讲义 + 附属文件合一」或扁平单文件）；简要介绍 + 单元文件清单 + `raw_path` 指针（可指文件或目录）；纯代理，整页可再生
- `assessments/`——学业事务聚合页：每作业 / 考试 / quiz 一页（文件名 = 作业名原形清洗），四要素归一——要求 / 参考（可选）/ 提交 / 结果
- `attachments/`——附件 1:1 代理（每附件一页，平铺；细分结构等真实内容浮现再说）
- 落位判据：**有成绩册列或提交动作 → assessments/**；老师发布的非讲义资产 → attachments/；讲义课件（内容单元）→ courseware/；结构事实（大纲 / 师资 / TA / 分组 / 评分构成 / 考试时间）入 info.md 正文，不作附件

## Invariants

- 两形分区（lark 档案页先例）：info（机械蒸馏节 + 备注沉淀）与 assessments（机械区 + `## 复盘` 沉淀）分区制——机械区可再生覆写、沉淀区只增，重建不得触碰；courseware / attachments 为纯代理（整页可再生，珍贵内容蒸馏入 notes，不留在代理页）
- 对账三字段分家：courseware `raw_path`（可指单元目录，路径即出身证明）；attachments `raw_file` / `raw_sha256`（文件级 1:1，词形语义同 mapping，指向 bb/）；assessments `raw` 块映射（角色→bb/ 路径，多源）+ `assessment` 块映射（due / submitted_at / score / possible / status / column_id / attempt_id——API 快照）
- 映射不改 `bb/` 源侧，删改自由属于人；不复制原文全文；源侧消失标 `status: deprecated` 不删
- 命名：原名保留（忠实），仅清洗文件系统非法字符；同桶重名尾缀 column_id 短形（lark-im 先例）
- 信任：机械区含 API 快照的（assessments 结果、info 基本信息）挂 `stale_after` = 拉取日 + TTL（继承 bb 域）；纯本地对账代理无 TTL——物化后即终态资产
- 页面 type 复用 `bb`（lark 域内插件共用 type: lark 先例），不扩注册表 type 值集
- 骨架是规约非预建空目录：桶随内容自然成形；`bb/` 拉取物为实例数据，gitignore 忽略（仅留 `.gitkeep` 种子）

## Changelog

- 0.7（2026-10-01）单元清单两态（本地在位 / 未物化指针条目——配套 bb v0.2 媒体指针化）；命令锚点 inbox 缺席即建
- 0.6（2026-10-01）命令 bb-map 立设：自本插件契约蒸馏（map / lark-map 同构——拉取核对 → 四桶落位 → 对账 → 写后管道），consumes [bb, bb-map, trust, index, hot, log]；实验前先行（用户裁定）
- 0.5（2026-10-01）courseware 回归纯代理：撤 `## 笔记` 沉淀节——笔记是人的造物，落点单独设计、不进本契约；两形分区收窄回 info / assessments
- 0.4（2026-10-01）桶名终裁与笔记落点：lec&tut → courseware、work → assessments（字段 work → assessment）；courseware 知识点页补 `## 笔记` 沉淀节，两形分区统一（attachments 仍纯代理）
- 0.3（2026-10-01）四桶并流：并入 bb-map-local 分支（info + lec&tut 内容单元制、raw_path、gitignore bb/、bb 注入行去「后议」）；考试边界句与判据句入册；lec&tut 纯代理形态、笔记缺口后补
- 0.2（2026-10-01）前两桶格式落地（bb-map-local 分支）：info.md + lec&tut/，raw_path 指针，内容单元映射（用户裁定）
- 0.1（2026-10-01）四桶骨架立设：work / attachments 细则、判据句、两形分区与对账字段（讨论收敛）；桶名沿团队现名
