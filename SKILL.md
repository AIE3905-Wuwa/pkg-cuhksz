---
name: bb-quiz
owner: bb-quiz
consumes: [bb-quiz, bb-map, bb-track, trust, log]
description: "出题自测：读 bb-track 认知档案与 courseware 知识点，生成英文试题 + 中文解析（落 notes/testing/），作答后判分回流认知档案。Triggers on: 出题, 自测, quiz, 生成习题, 考我, quiz me."
---

# bb-quiz：出题自测

用户指定范围（+ 可选样例），读 bb-track 认知档案知道「哪些点生疏该测、哪些点掌握可挑战」，按 courseware 知识点生成英文试题 + 中文解析——题型/难度对齐样例、知识点不越界、解析回链课件位置。考卷落 bb 侧素材层（`notes/testing/`，过程素材非档案）；作答后判分，经确认回流 user.md（machine 证据）。定位 = 检验，与 bb-teach（教学）正交。

## Scope

写：bb/<term>/<course>/notes/testing/（`<名>-试题.md` + `-答案.md` + `## 判分` 追记，origin: ai，只增）、log（写后一行）；user.md 判分回写（经 bb-track 写契约、用户确认后）
读：registry（`.meta/protocol/registry.yaml`，字段锚点）、courseware（sm-N + 专有名词）、assessments（已知作业）、user.md（bb-track 认知档案）、notes/ ai 笔记（best-effort）

## Steps

1. **解析输入**：范围（章节/单元/sm-N 列表）+ 样例（可选）+ 课程定位（`<term>/<course>`，现役学期可缺省）
2. **读知识点全集**：courseware sm-N + `## 专有名词` 对照表，取范围内子集
3. **读用户认知**：user.md 熟练度/目标层；stale 保守档、冷启动按未锚点
4. **定题型与难度中值**：样例 → 已知作业 → 用户习惯（细则见注入区）
5. **[best-effort] 读教学纪要**：notes/ origin: ai 笔记——缺席或无笔记静默跳过
6. **出题落盘**：`notes/testing/<名>-试题.md` + `-答案.md`（quiz 块映射 + origin: ai；试题页不含答案）+ log 行 + verify
7. **[作答后] 判分回流**：逐题判定 → 答案页追记 `## 判分`（日期+逐题对错+得分）→ 经用户确认回写 user.md 证据流（machine 自测）→ verify

## Prohibitions

- 不越界（范围内知识点，除非用户明示）；不写 bb/ 拉取物；考卷只增不覆写；判分未经确认不写 user.md
- 试题页不写答案/解析；答案页不写题干全文
- 隐私：考卷与判分内容属实例数据，不入框架仓库与 test-repo

## Language

题目英文（术语对齐 courseware 专有名词表）；解析与判分中文；路径与专名保留原形。

## Parameters

- 范围（章节/单元/知识点，可省 = 现役学期近窗知识点）
- 样例（习题/试卷，可选）
- 题量（可选，缺省适中）

## Injected Section (plugin usage blocks)

> 本区为 wiki_plugin_kernel 投影：consumes 拉取与源侧路由 usage_routes 合流，披露序 = owner 在前、路由居中、拉取殿后（inject / all 重建）；手写内容不进此区，改写侧契约改 PLUGIN.yaml。

<!-- cmd-inject:start -->
<!-- usage:bb-quiz -->
- 解析输入：范围（章节/单元/sm-N 列表）+ 样例（可选）；课程定位经 bb 目录结构（<term>/<course>，现役学期可缺省）
- 读知识点全集：courseware sm-N + `## 专有名词` 对照表，取范围内子集
- 读用户认知：user.md 熟练度/目标层/证据流，stale 先核对（未核对前保守档）、冷启动按未锚点（纪律见注入区 bb-track 块）
- 定题型与难度中值：样例 → assessments 已知作业 → 用户习惯；难度 = 认知层级 1-5（记忆/理解/应用/分析/综合），中值 M = 样例各题层级中位数（LLM 语义判断，软约束——粗保证 = 生疏偏易打底、掌握偏难挑战）
- 读教学纪要（best-effort）：notes/ ai 笔记（origin: ai）近期教了什么/卡在哪，避免重复或重点测刚教；缺席或无笔记静默跳过
- 选题：范围内知识点按 生疏/未锚点/错题/短期优先 排序覆盖
- 出题：英文题干、术语对齐 courseware 专有名词表、题型对齐样例、难度围绕 M
- 写解析：中文、每题标知识点 + sm-N wikilink
- 落盘：notes/testing/<名>-试题.md + -答案.md（quiz 块映射 + origin: ai + generated；试题页不含答案）；旧卷不删不覆写
- 判分（用户作答后）：对照答案页逐题判定 → 答案页追记 `## 判分`（日期 + 逐题对错 + 得分）；错题点与总体表现经用户确认回写 user.md 证据流（出处 machine 自测）——显著者按收敛纪律改读数；考卷本体是素材，档案只收结论
- 不越界：术语/知识点只取自范围内 courseware sm-N，越界弃题重出（除非用户明示；语义约束出题侧自检）
- 写后：log 行（类型 other --domain bb）+ pipeline.py verify
<!-- /usage:bb-quiz -->

<!-- usage:bb-map -->
- 课程信息页：每课建 info.md（type: bb + bb 块映射 term_id/course_id/term_status（现役|冻结）+ generated/stale_after），正文 `## 基本信息` 课程政策类要点蒸馏（评分/考核/师资/TA/分组/教学语言/AI 政策，分点 `<a id="info-N">` 锚点，读 bb/ 大纲与 assessment 文件，缺项标「未提供」）；「何时有何事」记此处，被评分事务全要素归 assessments 页
- 知识点页：bb/ 每个内容单元（目录 = 讲义+附属文件合一，或扁平单文件；平行同类目录合为一页）→ courseware/<单元名>.md（type: bb + raw_path 指向该单元，完全未下载单元可缺省 + generated）；读源识别知识点 → `## 知识点摘要` 分点 `<a id="sm-N">` 锚点 + 一行概括 + 源侧章节级提示 → `## 知识点联系` 点间互链 → `## 专有名词` 英中对照 → `## 单元文件` 两态对账清单（本地在位 / 未物化指针条目——媒体默认指针化，见 bb 块；扁平多附件单元清单即对应关系）；整页可再生，珍贵内容蒸馏入 notes
- assessments 页维护：成绩册列驱动建页（文件名 = 作业名原形清洗；汇总列 Weighted Total/Total 与分节登记列——非知识考核的分节/出勤登记如 Tutorial Section——排除不建页）；`## 要求`/`## 参考` 有源则蒸馏（分点 `<a id="req-N">`/`<a id="ref-N">` 锚点，无源标「无单独要求文件」）；raw 块映射登记要求/参考/提交文件（提交件在 bb/<term>/<course>/submissions/；允许多页引用同一文件）；`## 提交`/`## 结果` 自 grades/submission 快照刷新机械区（due 缺省预留说明位不告警；无提交记录用独立话术列三种可能）；毕写 log 行（类型 map）
- attachments 代理：老师发布的非讲义资产每件一页（raw_file/raw_sha256），平铺；TA/分组等结构事实不作附件页
- 落位判据（见注入行）
- 重建纪律：机械区对账覆写；沉淀区（info 备注 / assessments 复盘）只增，重建不得触碰；attachments 代理整页可再生
- stale 处置：assessments 结果与 info 基本信息挂 stale_after，stale 经 bbcli 现拉刷新（agent 即同步器）；courseware/attachments 纯本地对账无 TTL
- 写后管道（机械自动）：python .meta/scripts/pipeline.py index + tags + hot + log + verify（先重建派生层再校验——校验置后收尾，避免先校验误报派生区漂移）
- 派生只出不回：行动项→todo、高价值复盘→notes（回链 assessments 页）——todo/notes 桥
<!-- /usage:bb-map -->

<!-- usage:bb-track -->
- 建档：首个显著信号或用户明示时建 user.md（type: bb + generated/updated/stale_after）；缺席即无认知数据，消费侧降级处理不报错
- 追加证据：`- MM-DD 出处（human 对话|machine grades|human 笔记|ai 笔记|human 复核）：断言 → [[回链]]`；出处开放词表
- 收敛读数：新证据到 → 读数行改写（新值取代旧值，行内留最近证据摘要与日期）；证据流不动
- 消费纪律：teaching/testing/复盘类输出前先读 user.md；stale 先核对近窗证据或询问，未核对前按保守档消费（状态降半档）；差距分析 = courseware 知识点全集 − 已锚点集，现算
- 笔记消费：读 notes/ 概览与 stage/origin 属性作信号；不改不删不代标 stage；ai 笔记仅弱证据
- 采集通道（bb-teach / bb-quiz，用法投影挂 bb-track 命令注入区）：讲解沉淀 = notes/ ai 笔记（origin: ai，弱证据）；自测判分 = notes/testing/ 考卷（machine 证据，出处标 machine 自测）——两者经用户确认入证据流、按收敛纪律改读数
- 写后管道：verify；log 行（类型 profile，--domain bb）
- 认知桥注册（user-profile 按需桥）：建档时若画像页在场，维护其 `## 域认知` 节一行 `- bb：wiki/bb/<term>/<course>/user.md`（路径形通配多课多档）；画像缺席跳过不代建（按需桥缺席容错）
<!-- /usage:bb-track -->

<!-- usage:trust -->
- 写页随手写 `generated`（块式：`by: agent/<当前模型>` / `at: 今日`）
- 复核动作发生时追加 `verified` 事件（单行 `by: <actor>, at: <日期>`），不为凑水位伪造
- 复核由用户发起（人指令触发），agent 不自发追加 verified 事件
<!-- /usage:trust -->

<!-- usage:log -->
- 写行（机械自动）：`python .meta/scripts/pipeline.py log <类型> "<一句话>" [--domain 域]`（类型值集见 AGENTS 注入区 log 块；域标 = 域件名如 bb/lark/vault，域内事务必带、框架与原生事务缺省）；滚动窗口与归档由脚本执行
<!-- /usage:log -->
<!-- cmd-inject:end -->
