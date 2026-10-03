---
name: bb-teach
owner: bb-teach
consumes: [bb-teach, bb-track]
description: "提问即解惑：定位 courseware 知识点 → 读 bb-track 认知档案 → 按熟练度×难度二维伸缩讲解。Triggers on: 讲解, 答疑, 我不懂, 为什么, 这个知识点, 帮我理一理, explain, bb-teach."
---

# bb-teach：提问即解惑

用户提问时，先读 bb-track 认知档案知道「这个用户对相关知识点到底生疏还是熟练」，再按「用户熟练度 × 概念难度」二维伸缩讲解——已知的略讲/反问，未知的讲透，并主动对齐用户的短期目标与历史错题。定位、读态、写回均委托既有插件，本命令只持「教学决策 + 输出格式 + 闭环提议」三件独有职责。

## Scope

写：默认无（纯对话输出）；可选 session 纪要（经 save）、user.md 认知收敛（经 bb-track 写契约、用户确认后）
读：registry（`.meta/protocol/registry.yaml`，字段锚点）、query 检索（hot/index/tags/grep）、courseware / assessments（bb-map 页，sm-N/req-N 锚点）、user.md（bb-track 认知档案）

## Steps

1. **定位知识点**：问题 → 提取关键词 → query 分层检索（hot→index→grep→读页）→ courseware `sm-N` 锚点与 `## 专有名词` 对照表收窄；命中可能横跨多个 sm-N / 多个课程，皆列
2. **读用户认知**：读 user.md 认知读数（锚点→状态词）+ 证据流 + 目标层；`stale_after` 过期先核对近窗证据或询问（不拿旧态误判）；差距 = courseware 全集 − 已锚点集现算；错题点级结论自 assessments 复盘
3. **按二维矩阵讲解**：按注入区 bb-teach 块的伸缩规则输出（术语门槛 + 错题/目标注入 + 锚点回链）
4. **[可选] 三层反馈闭环**：单轮反馈只调当轮讲法不落盘；显著答疑可经 save 落 session 纪要；仅显著信号（跨会话稳定/主动应用/machine 验证）才提议收敛 user.md，确认后走 bb-track 写契约 + pipeline

## Prohibitions

- 不写 `bb/` 源侧；不改 courseware / assessments 纯代理页；不改 `notes/`（人的领地，只读 origin/form/stage 作信号）
- 单轮「懂了」不写 user.md；未经用户确认不写 user.md；讲解过程不写 log
- 隐私：认知 / 讲解内容属实例数据，不入框架仓库与 test-repo

## Language

生成内容中文为主，英文专名与路径保留原形。

## Parameters

- 问题（自然语言，可含课程代码 / 知识点名 / 术语；可省 = 由 agent 定位现役学期相关课程）

## Injected Section (plugin usage blocks)

> 本区为 wiki_plugin_kernel 自各插件 manifest usage 列表按本命令 consumes 序投影（inject / all 重建）；手写内容不进此区，改写侧契约改 PLUGIN.yaml。

<!-- cmd-inject:start -->
<!-- usage:bb-teach -->
- 定位：问题→提取关键词→query 分层检索（hot→index→grep→读页）→ bb-map courseware sm-N 锚点与 `## 专有名词` 对照表收窄；跨页跨点皆列
- 读态：读 user.md 认知读数（锚点→状态词）+ 证据流 + 目标层；stale 核对、差距现算（courseware 全集 − 已锚点集）、错题点级结论——纪律见注入区 bb-track 块
- 二维伸缩（熟练度×难度）：未锚点/生疏→完整讲透（硬核概念加类比+数字例子+前置链补全）；熟悉→重点怎么用+易错点；熟练→为什么+易错点+跨点联系+开放问题；掌握→反问/挑战题/引导自查（不灌输）
- 术语门槛：允许出现的术语 = 用户已锚点集（非「本课前面出现」）；超出者当场解释、绝不假定已知
- 目标与错题注入：短期优先（带时效）命中者篇幅 +1 档标「近期重点」、过期降级；命中 assessments 复盘错题点易错点 +1 档并点出
- 输出：行内加粗标签骨架（直觉/是什么/为什么/怎么用/类比/易错点/前置）按矩阵伸缩，每条回链 courseware sm-N
- 三层反馈闭环：单轮反馈（懂了/追问/答错）只调当轮讲法、不落盘；显著答疑可经 save 落 session 纪要（事实非断言）；仅显著信号（跨会话稳定/主动正确应用/machine 验证）才提议收敛 user.md——写回委托 bb-track 写契约、经用户确认；单轮「懂了」不写、单轮「没懂」不判生疏
- log 纪律：讲解动作不写 log（不采集行为信号）；仅认知收敛走 bb-track 写后管道（log profile --domain bb + verify）
<!-- /usage:bb-teach -->

<!-- usage:bb-track -->
- 建档：首个显著信号或用户明示时建 user.md（type: bb + generated/updated/stale_after）；缺席即无认知数据，消费侧降级处理不报错
- 追加证据：`- MM-DD 出处（human 对话|machine grades|human 笔记|ai 笔记|human 复核）：断言 → [[回链]]`；出处开放词表
- 收敛读数：新证据到 → 读数行改写（新值取代旧值，行内留最近证据摘要与日期）；证据流不动
- 消费纪律：teaching/testing/复盘类输出前先读 user.md；stale 先核对近窗证据或询问；差距分析 = courseware 知识点全集 − 已锚点集，现算
- 笔记消费：读 notes/ 概览与 stage/origin 属性作信号；不改不删不代标 stage；ai 笔记仅弱证据
- 写后管道：verify；log 行（类型 profile，--domain bb）
- 认知桥注册（user-profile 按需桥）：建档时若画像页在场，维护其 `## 域认知` 节一行 `- bb：wiki/bb/<term>/<course>/user.md`（路径形通配多课多档）；画像缺席跳过不代建（按需桥缺席容错）
<!-- /usage:bb-track -->
<!-- cmd-inject:end -->
