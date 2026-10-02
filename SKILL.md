---
name: bb-map
owner: bb-map
consumes: [bb, bb-map, trust, index, hot, log]
description: "把 bb/ 拉取物与成绩册快照映射为 wiki/bb/<term>/<course>/ 规范形四桶页：拉取核对 → info/courseware/assessments/attachments 落位 → 对账 → 写后管道。Triggers on: bb-map, 映射课程, bb 落位, 落位这门课, map bb course."
---

# bb-map：课程域映射

把 `bb/` 拉取物与成绩册快照映射为 `wiki/bb/<term>/<course>/` 规范形四桶页——映射与理解解耦，登记 + courseware 知识点摘要（粗粒度蒸馏）+ 对账动作（四桶契约与对账字段见注入区 bb-map 块）。数据拉取经 bbcli skill（`connectors/bb-cli/SKILL.md`——会话纪律与命令速查）；深度讲解不属本命令（高价值复盘走 save 进 notes，回链属地页）。

## Scope

写：bb-map（info / courseware / assessments / attachments 四桶页，机械区覆写）、log、hot、index
读：registry（`.meta/protocol/registry.yaml`，字段与值集锚点）、bb/ 拉取物、bbcli（courses / tree / files / dues / assignments / grades / submission）、`wiki/bb/inbox.md`（域配置）

## Steps

1. **锚点（一次读取）**：读 registry 与 `wiki/bb/inbox.md`（`terms` 块映射——现役学期与冻结标记）；**inbox 缺席即建**（terms 自 `bb-cli terms`/`courses` 现查登记 + 首刷速写与公告分拣，流程见注入区 bb 块）
2. 会话核对：`bb-cli status`（未登录按 bbcli skill 登录纪律处理）；定位目标课（目录名 = 课程代码，如 AIE3005；新课先建属地目录与身份页字段）
3. 拉取物核对：`bb/<term>/<course>/` 源树在位（缺则经 bbcli skill `fetch` 落位，默认带媒体过滤——策略见注入区 bb 块）；assessments 机械区数据自 `grades` / `submission` 快照现拉
4. 按注入区契约逐桶落位：info（身份 bb 块映射 term_id/course_id/term_status + `## 基本信息` 课程政策类要点蒸馏 `info-N` 锚点）→ courseware（读源识别知识点 → `## 知识点摘要`（sm-N 锚点 + 一行概括 + 章节提示）+ `## 知识点联系` + `## 专有名词` + `## 单元文件`）→ assessments（汇总列排除；`## 要求`/`## 参考` 有源蒸馏 `req-N`/`ref-N` 锚点 + `## 提交`/`## 结果` 机械快照，due 缺省不告警）→ attachments（1:1 代理）；机械区对账覆写，沉淀区不触碰
5. **呈落位预览**（新增 / 变更 / 废弃清单），等用户确认
6. **写后管道**（确定性，机械自动不询问）：按注入区序执行各插件写入调用（index/tags/hot/log 派生层重建在前），毕即 `python .meta/scripts/pipeline.py verify` 收尾（写后自证，未过即回修）；随即按提交纪律入库（`映射: <term>/<course>`，词表见 `.meta/protocol/actions.md`）
7. 回报：课程 / 四桶新增·变更·废弃计数 / stale 清单（stale 项经 bbcli 现拉刷新后消除）

## Prohibitions

- 不写 `bb/` 源侧任何文件（拉取物只增，删改自由属于人）；不复制原文全文
- 沉淀区（info `## 备注` / assessments `## 复盘`）只增不改，重建不得触碰
- 不拉 roster；成绩只进 assessments 机械区（隐私红线：课程 / 成绩 / 提交数据属实例数据，不入框架仓库）
- 凭据会话只存本机；提交作业等写操作不属本命令（永远须用户明示并另行设计）

## Language

生成内容中文为主，英文专名与路径保留原形。

## Parameters

- 课程（课程代码 / 属地目录名，如 `AIE3005`；可省 = 现役学期全部课）
- 桶（`info` / `courseware` / `assessments` / `attachments`；可省 = 全部——单桶重跑用）

## Injected Section (plugin usage blocks)

> 本区为 wiki_plugin_kernel 自各插件 manifest usage 列表按本命令 consumes 序投影（inject / all 重建）；手写内容不进此区，改写侧契约改 PLUGIN.yaml。

<!-- cmd-inject:start -->
<!-- usage:bb -->
- 进域先读 wiki/bb/inbox.md（速写与域配置一体；缺席即建——bb-map 命令锚点触发或 agent 自发）；刷新流程 = 现拉公告+dues → 蒸馏重写速写（未交提醒双源：assignments 无提交 ∪ grades 有 due 无 attempt）→ 公告分拣派生 → log 行（类型 other）；stale 同此（agent 即同步器）
- 拉取落位：课件 → bb/<term>/<course>/（保留源侧目录树）；提交件 → bb/<term>/<course>/submissions/；拉取物只增不覆写，同名变更件 --refresh 重拉、内容哈希尾缀落新件（旧件保留=修订史）
- 新学期/新课 = 建属地目录 + 身份页（bb 块映射 term_id/course_id）；bbcli 解析直接用目录名（--term 学期名、课程代码子串）
- 物化分层：文档类全量；媒体类（video/audio）默认指针化不落 bb/——fetch 过滤参数（--exclude-mime/--exclude-ext/--max-size）见 bbcli skill，单元页清单登记未物化条目，按需 --match 单取
- 公告拆信：不存档不立页（真相在 BB 现拉即得）；作业变更→assessments 机械区、考试/调课→info 基本信息（+calendar 派生）、政策/师资/分组→info 基本信息、行动项→todo、资源发布→触发 fetch 即弃、高价值长文→notes 涌现回链
- 单向派生（只出不回）：行动项 → todo；课业日程 → calendar；高价值结论 → notes（回链属地页）
- 隐私与边界：成绩按需现拉呈现即止、不默认投影；roster 不拉；提交作业等写操作不入本域
<!-- /usage:bb -->

<!-- usage:bb-map -->
- 课程信息页：每课建 info.md（type: bb + bb 块映射 term_id/course_id/term_status（现役|冻结）+ generated/stale_after），正文 `## 基本信息` 课程政策类要点蒸馏（评分/考核/师资/TA/分组/教学语言/AI 政策，分点 `<a id="info-N">` 锚点，读 bb/ 大纲与 assessment 文件，缺项标「未提供」）；「何时有何事」记此处，被评分事务全要素归 assessments 页
- 知识点页：bb/ 每个内容单元（目录 = 讲义+附属文件合一，或扁平单文件；平行同类目录合为一页）→ courseware/<单元名>.md（type: bb + raw_path 指向该单元，完全未下载单元可缺省 + generated）；读源识别知识点 → `## 知识点摘要` 分点 `<a id="sm-N">` 锚点 + 一行概括 + 源侧章节级提示 → `## 知识点联系` 点间互链 → `## 专有名词` 英中对照 → `## 单元文件` 两态对账清单（本地在位 / 未物化指针条目——媒体默认指针化，见 bb 块；扁平多附件单元清单即对应关系）；整页可再生，珍贵内容蒸馏入 notes
- assessments 页维护：成绩册列驱动建页（文件名 = 作业名原形清洗；汇总列 Weighted Total/Total 排除不建页）；`## 要求`/`## 参考` 有源则蒸馏（分点 `<a id="req-N">`/`<a id="ref-N">` 锚点，无源标「无单独要求文件」）；raw 块映射登记要求/参考/提交文件（提交件在 bb/<term>/<course>/submissions/；允许多页引用同一文件）；`## 提交`/`## 结果` 自 grades/submission 快照刷新机械区（due 缺省预留说明位不告警；无提交记录用独立话术列三种可能）；毕写 log 行（类型 map）
- attachments 代理：老师发布的非讲义资产每件一页（raw_file/raw_sha256），平铺；TA/分组等结构事实不作附件页
- 落位判据（见注入行）
- 重建纪律：机械区对账覆写；沉淀区（info 备注 / assessments 复盘）只增，重建不得触碰；attachments 代理整页可再生
- stale 处置：assessments 结果与 info 基本信息挂 stale_after，stale 经 bbcli 现拉刷新（agent 即同步器）；courseware/attachments 纯本地对账无 TTL
- 写后管道（机械自动）：python .meta/scripts/pipeline.py index + tags + hot + log + verify（先重建派生层再校验——校验置后收尾，避免先校验误报派生区漂移）
- 派生只出不回：行动项→todo、高价值复盘→notes（回链 assessments 页）
<!-- /usage:bb-map -->

<!-- usage:trust -->
- 写页随手写 `generated`（块式：`by: agent/<当前模型>` / `at: 今日`）
- 复核动作发生时追加 `verified` 事件（单行 `by: <actor>, at: <日期>`），不为凑水位伪造
- 复核由用户发起（人指令触发），agent 不自发追加 verified 事件
<!-- /usage:trust -->

<!-- usage:index -->
- 写后重建（机械自动）：`python .meta/scripts/pipeline.py index`（索引——溢出减负制，含并回后多余旧索引删除）与同脚本 `tags`（tag 反向索引）；LLM 不手写索引
<!-- /usage:index -->

<!-- usage:hot -->
- 写条目（机械自动）：`python .meta/scripts/pipeline.py hot <类型> "<wikilink + 一句话核心>"`（类型值集同 log，见 AGENTS 注入区 log 块）；窗口淘汰与截短由脚本执行
<!-- /usage:hot -->

<!-- usage:log -->
- 写行（机械自动）：`python .meta/scripts/pipeline.py log <类型> "<一句话>"`（类型值集见 AGENTS 注入区 log 块）；滚动窗口与归档由脚本执行
<!-- /usage:log -->
<!-- cmd-inject:end -->
