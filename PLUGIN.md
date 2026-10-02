# bb-map：bb 域映射法则

bb 域的映射法则（mapping 之于 vault；bb 域内插件，契约见 bb 插件）。**规范化投影**：`bb/` 保源形（对账前提），属地 `wiki/bb/<term>/<course>/` 统一规范形四桶——不论源目录如何存储。映射与理解解耦：代理是「bb 资产在 md 世界的代表」，courseware 标配「知识点摘要（分点 `<a id="sm-N">` 锚点）+ 专有名词」，深度讲解为可选增强。桶名 v0.4 终裁：`courseware`（原 lec&tut）/ `assessments`（原 work）/ `attachments`（2026-10-01 裁定）。

## Structure

- `info.md`——课程信息页兼身份页（一课一锚点）：frontmatter `bb` 块映射（term_id / course_id / term_status——现役|冻结，学期状态随页走、不依赖 inbox）+ 正文机械蒸馏节（大纲课程政策类要点开放词表：评分构成 / 考核 / 师资 / TA / 分组 / 教学语言 / AI 政策，分点 `<a id="info-N">` 锚点，缺项如实标「未提供」）+ `## 备注`（沉淀区只增）。边界：info 存「何时有何事」（日程视角），被评分事务全要素归 assessments 页
- `courseware/<单元名>.md`——知识点页：每内容单元一份（内容单元 = bb/ 目录「讲义 + 附属文件合一」或扁平单文件；平行同类文件的目录合为一页——如 Reading 系列，判断即「同源侧目录下平行同类」）；frontmatter 对账字段 `raw_path`（可指文件或目录；完全未下载单元可缺省——清单逐条标注未下载即构成记录）+ `## 知识点摘要`（分点 `<a id="sm-N">` 锚点 + 一行概括 + 源侧章节级提示，锚点即定位指针；页码级不做——教材改版会漂移）+ `## 知识点联系`（点间互链）+ `## 专有名词`（英中对照表）+ `## 单元文件`（两态对账清单；扁平多附件单元与源侧不对应时，清单即对应关系）；纯代理，整页可再生（摘要与术语表皆自源蒸馏）
- `assessments/`——学业事务聚合页：每作业 / 考试 / quiz 一页（文件名 = 作业名原形清洗；汇总列不建页——名为 Weighted Total / Total 直接排除，辅以无提交记录佐证），四要素归一——要求 / 参考（有源则自源蒸馏，分点 `<a id="req-N">` / `<a id="ref-N">` 锚点）/ 提交 / 结果（机械快照）；due 缺省时预留说明位置、不告警；无提交记录用独立话术列三种可能（未布置 / 未提交 / 未收录），不复用纸面提交模板
- `attachments/`——附件 1:1 代理（每附件一页，平铺；细分结构等真实内容浮现再说）
- 落位判据：**有成绩册列或提交动作 → assessments/**（汇总列与分节登记列除外——后者为非知识考核的分节/出勤登记，2026-10-02 所有者裁定不建页）（汇总列 Weighted Total / Total 除外）；老师发布的非讲义资产 → attachments/；讲义课件（内容单元）→ courseware/；结构事实入 info.md 正文，不作附件；讲义与附件边界——随周次推进的课程内容归 courseware，支撑性资源（GPU 指南、软件安装等）归 attachments

## Invariants

- 两形分区（lark 档案页先例）：info（机械蒸馏节 + 备注沉淀）与 assessments（机械区 + `## 复盘` 沉淀）分区制——机械区可再生覆写、沉淀区只增，重建不得触碰（info 蒸馏节 / assessments 要求·参考·提交·结果皆机械区，蒸馏进机械区不增设沉淀区）；courseware / attachments 为纯代理（整页可再生，珍贵内容蒸馏入 notes，不留在代理页）——courseware 代理密度为「知识点摘要 + 专有名词」（自源蒸馏、可再生，非人的沉淀），不设沉淀区
- 对账三字段分家：courseware `raw_path`（可指单元目录，路径即出身证明）；attachments `raw_file` / `raw_sha256`（文件级 1:1，词形语义同 mapping，指向 bb/）；assessments `raw` 块映射（角色→bb/ 路径，多源；允许多页引用同一文件——一份作业总纲 PDF 被多页共同引用为正常形态）+ `assessment` 块映射（due / submitted_at / score / possible / status / column_id / attempt_id——API 快照）
- 映射不改 `bb/` 源侧，删改自由属于人；不复制原文全文；源侧消失标 `status: deprecated` 不删
- 命名：原名保留（忠实），清洗文件系统非法字符后合并相邻空白（`Test 1: SV` → `Test 1_SV`）；同桶重名尾缀 column_id 短形（lark-im 先例）
- 信任：机械区含 API 快照的（assessments 结果、info 基本信息）挂 `stale_after` = 拉取日 + TTL（继承 bb 域）；纯本地对账代理无 TTL——物化后即终态资产
- 页面 type 复用 `bb`（lark 域内插件共用 type: lark 先例），不扩注册表 type 值集
- 骨架是规约非预建空目录：桶随内容自然成形；`bb/` 拉取物为实例数据，gitignore 忽略（仅留 `.gitkeep` 种子）

## Changelog

- 0.11（2026-10-02）补录所有者裁定：分节登记列（如 Tutorial Section）不建页——判据句与建页规则补例外条款
- 0.10（2026-10-02）规则批 M1-M12 + D2：汇总列排除（Weighted Total/Total）、共享要求文件成文（多页引同一文件）、未下载单元 raw_path 缺省、清单即对应关系、合集切分规则、讲义/附件边界判据、命名合并空白、无提交独立话术、due 缺省不告警、info 类别制蒸馏、知识点章节级提示、写后管道校验置后；info 页 bb 块映射增 term_status（D2）
- 0.9（2026-10-02）info 蒸馏完备化六项（`<a id="info-N">` 锚点）+ assessments 要求/参考蒸馏（`req-N`/`ref-N` 锚点）；attachments 不变（用户裁定）。
- 0.8（2026-10-02）courseware 代理升级：简要介绍 → 知识点摘要（`<a id="sm-N">` 锚点 + 一行概括）+ 知识点联系 + 专有名词对照表；仍纯代理整页可再生（用户裁定）。
- 0.7（2026-10-01）单元清单两态（本地在位 / 未物化指针条目——配套 bb v0.2 媒体指针化）；命令锚点 inbox 缺席即建
- 0.6（2026-10-01）命令 bb-map 立设：自本插件契约蒸馏（map / lark-map 同构——拉取核对 → 四桶落位 → 对账 → 写后管道），consumes [bb, bb-map, trust, index, hot, log]；实验前先行（用户裁定）
- 0.5（2026-10-01）courseware 回归纯代理：撤 `## 笔记` 沉淀节——笔记是人的造物，落点单独设计、不进本契约；两形分区收窄回 info / assessments
- 0.4（2026-10-01）桶名终裁与笔记落点：lec&tut → courseware、work → assessments（字段 work → assessment）；courseware 知识点页补 `## 笔记` 沉淀节，两形分区统一（attachments 仍纯代理）
- 0.3（2026-10-01）四桶并流：并入 bb-map-local 分支（info + lec&tut 内容单元制、raw_path、gitignore bb/、bb 注入行去「后议」）；考试边界句与判据句入册；lec&tut 纯代理形态、笔记缺口后补
- 0.2（2026-10-01）前两桶格式落地（bb-map-local 分支）：info.md + lec&tut/，raw_path 指针，内容单元映射（用户裁定）
- 0.1（2026-10-01）四桶骨架立设：work / attachments 细则、判据句、两形分区与对账字段（讨论收敛）；桶名沿团队现名
