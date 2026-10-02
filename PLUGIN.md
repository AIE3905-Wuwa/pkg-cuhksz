# bb-track：BB 课程认知档案

组会裁定（2026-10-02）：笔记与认知的价值不在教会 agent 知识（预训练已备，训练集外可经 bb-map 检索原文），而在告知 agent **用户的认知状态**——知道什么、熟练度如何、未来要掌握什么。本插件管两件事：wiki 侧认知档案 user.md 的契约，与外域笔记区（bb v0.4）的只读消费契约。不建笔记（人的造物）、不教知识（teaching 类消费侧的事）、不落统计（派生现算）。

## Structure

- 认知档案 `wiki/bb/<term>/<course>/user.md`：每课一份，课程根落位（不入四桶——桶归代理页），属地**域内原生页**（wiki v0.7 两形首例：真身在此、无外源可对账）
- 建档懒惰式：首个显著信号或用户明示时建，不随新课强制立页（缺席 = 尚无认知数据，消费侧降级处理不报错）
- 两区制正文：`## 认知读数`（收敛覆写——新值取代旧值）+ `## 证据流`（只增不改写）
- 学期即边界：term 在路径中，学期冻结随 term_status；新学期新档，旧档只读可作初始参考
- 笔记消费契约：`bb/<term>/<course>/notes/` 只读（bb v0.4 机器写边界），可选 frontmatter 三属性（见 manifest fields）——stage 标记属人（agent 只读不写）

## Invariants

- 读数锚定：条目锚 courseware 知识点（sm-N 锚点 wikilink），粗粒度自陈合法（混合粒度共存）；状态词开放（生疏/熟悉/熟练/掌握等，不立封闭词表）
- 证据可溯：读数每条可溯证据——证据流行必带日期 + 出处 + 回链（assessments 页 / notes 文件 / session 页）
- 信号权重：human（用户原话、human 笔记、人复核）> machine（grades/submission 快照）> ai（origin: ai 笔记——弱证据，人复核方升权）
- 应知不存：课程要求在 info.md、知识点全集在 courseware——user.md 只存已知/熟练/目标，差距消费时现算
- 目标层入读数：课程目标 + 短期优先（带时效，过期即失效）
- 错题分层：题级事实归 assessments 复盘区（可选行约定带知识点 wikilink 供反向索引）；点级结论入读数；统计现算不落盘
- 更新双轨：agent 识别显著信号自发（成绩刷新后、笔记 stage 变更后）+ 用户明示（自述即认知输入）；显著纪律——记显著不记日常
- trust 复用：generated 随手写；读数天花板 machine-confirmed，证据流含 human 事件则 human-reviewed；stale_after 默认 14 天（页面可覆写）——stale 时消费前先核对近窗证据或询问用户
- 不打 tags（单课路径直读，同 user-profile 先例）
- v0.1 非目标：行为信号（查阅频次）不采集；桥（user-profile 全局件扩展点注册）延后批；课表时间触发悬置（课表源缺口：SIS / ics 归 calendar 源适配器，挂缺见 log）
- 隐私：认知内容属实例数据，不入框架仓库与 test-repo

## Changelog

- 0.1（2026-10-02）立设（组会裁定 + 两轮详谈收敛）：认知档案两区制、笔记只读消费契约三属性、属地原生页首例（携 wiki v0.7 属地两形、bb-map v0.12 四桶豁免）
