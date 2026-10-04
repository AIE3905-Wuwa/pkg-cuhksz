---
name: bb-track
owner: bb-track
consumes: [bb-track, trust, log]
description: "认知档案：读/建/更 wiki/bb/<term>/<course>/user.md 学习状态（认知读数+证据流+目标层），差距现算；采集通道（讲解答疑 bb-teach / 出题自测 bb-quiz）用法挂载于此。Triggers on: 认知档案, 学习状态, 我学得怎么样, user.md, bb-track."
---

# bb-track：认知档案

bb 域认知枢纽——每课 user.md 是「用户对该课各知识点的认知状态」唯一档案（读数收敛覆写 + 证据流只增 + 目标层），建档懒惰式、学期即边界。本命令管档案的读 / 建 / 更与差距分析；两个采集通道（bb-teach 讲解答疑、bb-quiz 出题自测）的用法投影挂载于本命令注入区——教与考的产物落 bb 侧素材层（notes/），认知结论经确认回写本档案。

## Scope

写：wiki/bb/<term>/<course>/user.md（读数收敛 + 证据流追加，经用户确认）、log（写后一行）
读：registry（`.meta/protocol/registry.yaml`，字段锚点）、courseware（知识点全集，差距现算）、assessments（复盘/成绩信号）、notes/（人的笔记属性 + ai 笔记弱证据 + testing/ 考卷判分）、profile（域认知登记，在场时）

## Steps

1. **定位与读档**：定位课程 `<term>/<course>`，读 user.md 认知读数、证据流、目标层——细则见注入区 bb-track 块
2. **差距分析**：courseware 知识点全集减已锚点集，现算；错题点自 assessments 复盘
3. **建档或更新**：建档懒惰式；证据追加与读数收敛按注入区 bb-track 块纪律，均经用户确认
4. **写后**：verify 加 log 行

## Prohibitions

- 证据流条目不改写不删除；读数每条须可溯证据；笔记 stage 属人不代标
- 不写 bb/ 拉取物与 notes/（素材层归采集通道）；未经确认不写 user.md
- 隐私：认知内容属实例数据，不入框架仓库与 test-repo

## Language

中文为主，知识点锚点与专名保留原形。

## Parameters

- 课程（可省 = 现役学期全部或指定课）
- 动作（读档 / 差距分析 / 建档 / 更新读数，可省 = 读档 + 差距概览）

## Injected Section (plugin usage blocks)

> 本区为 wiki_plugin_kernel 投影：consumes 拉取与源侧路由 usage_routes 合流，披露序 = owner 在前、路由居中、拉取殿后（inject / all 重建）；手写内容不进此区，改写侧契约改 PLUGIN.yaml。

<!-- cmd-inject:start -->
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

<!-- usage:bb-teach -->
- 定位：问题→提取关键词→query 分层检索（hot→index→grep→读页）→ bb-map courseware sm-N 锚点与 `## 专有名词` 对照表收窄；跨页跨点皆列
- 读态：读 user.md 认知读数（锚点→状态词）+ 证据流 + 目标层；stale 核对、差距现算（courseware 全集 − 已锚点集）、错题点级结论——纪律见注入区 bb-track 块
- 二维伸缩（熟练度×难度）：未锚点/生疏→完整讲透（硬核概念加类比+数字例子+前置链补全）；熟悉→重点怎么用+易错点；熟练→为什么+易错点+跨点联系+开放问题；掌握→反问/挑战题/引导自查（不灌输）
- 术语门槛：允许出现的术语 = 用户已锚点集（非「本课前面出现」）；超出者当场解释、绝不假定已知
- 目标与错题注入：短期优先（带时效）命中者篇幅 +1 档标「近期重点」、过期降级；命中 assessments 复盘错题点易错点 +1 档并点出
- 输出：行内加粗标签骨架（直觉/是什么/为什么/怎么用/类比/易错点/前置）按矩阵伸缩，每条回链 courseware sm-N
- 三层反馈闭环：单轮反馈（懂了/追问/答错）只调当轮讲法、不落盘；显著答疑（结构化沉淀价值或用户明示「记下来」）落 notes/ ai 笔记——一篇一问（问题+讲解骨架+易错点+锚点回链），origin: ai / form: text，命名 <日期>-<主题>.md，只增不覆写；仅显著信号（跨会话稳定/主动正确应用/machine 验证）才提议收敛 user.md——写回委托 bb-track 写契约、经用户确认；单轮「懂了」不写、单轮「没懂」不判生疏
- 档案姿态：user.md stale 先核对（未核对前按保守档讲），缺席（冷启动）全场按未锚点档讲透——不因无档案拒绝讲解
- log 纪律：讲解对话不写 log（不采集行为信号）；显著答疑落 notes/ 后写一行（other --domain bb）；认知收敛走 bb-track 写后管道（log profile --domain bb + verify）
<!-- /usage:bb-teach -->

<!-- usage:trust -->
- 写页随手写 `generated`（块式：`by: agent/<当前模型>` / `at: 今日`）
- 复核动作发生时追加 `verified` 事件（单行 `by: <actor>, at: <日期>`），不为凑水位伪造
- 复核由用户发起（人指令触发），agent 不自发追加 verified 事件
<!-- /usage:trust -->

<!-- usage:log -->
- 写行（机械自动）：`python .meta/scripts/pipeline.py log <类型> "<一句话>" [--domain 域]`（类型值集见 AGENTS 注入区 log 块；域标 = 域件名如 bb/lark/vault，域内事务必带、框架与原生事务缺省）；滚动窗口与归档由脚本执行
<!-- /usage:log -->
<!-- cmd-inject:end -->
