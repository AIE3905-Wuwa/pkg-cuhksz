# bb-track：认知档案

## 设计概要

- **为什么存在**：组会裁定，2026-10-02——笔记与认知的价值不在教会 agent 知识，预训练已备，原文可经 bb-map 检索；而在告知 agent **用户的认知状态**：知道什么、熟练度如何、接下来要掌握什么。本件是 bb 族的**认知枢纽**：wiki 侧 user.md 档案契约，加素材层只读消费契约。teach 教与 quiz 考两条采集通道围绕它成环；用法经源侧路由挂 bb-track 命令，见 mechanics 第 4 节
- **关键裁定**：
  - 属地**域内原生页**首例，wiki v0.7 两形：真身在 wiki，无外源可对账——认知档案不是任何外源的投影，是 wiki 自己的写作物
  - 两区制：读数收敛覆写，证据流只增——结论可变、证据不可变，每条读数可溯
  - 应知不存、差距现算：知识点全集在 courseware，课程要求在 info；user.md 只存已知与目标，差集消费时现算，不立双份事实源
  - 信号权重 human 大于 machine，machine 大于 ai 笔记：ai 产物是弱证据，人复核方升权，防 LLM 自我强化
  - 建档懒惰式，学期即边界：缺席不报错，消费侧降级处理；term_status 冻结随学期
- **非目标**，立设时裁定：不建笔记，人的造物；不教知识，teach 的事；不落统计，派生现算；不采集行为信号如查阅频次。课表触发悬置，课表源缺口

## Structure

- 认知档案 `wiki/bb/<term>/<course>/user.md`：每课一份，课程根落位，不入四桶——桶归代理页；属地**域内原生页**，wiki v0.7 两形首例：真身在此，无外源可对账
- 建档懒惰式：首个显著信号或用户明示时建，不随新课强制立页；缺席 = 尚无认知数据，消费侧降级处理不报错
- 两区制正文：`## 认知读数` 收敛覆写，新值取代旧值；`## 证据流` 只增不改写
- 学期即边界：term 在路径中，学期冻结随 term_status；新学期新档，旧档只读可作初始参考
- 笔记消费契约：`bb/<term>/<course>/notes/` 只读——bb v0.7 共居区，收人的笔记、ai 笔记、testing/ 考卷；可选 frontmatter 三属性见 manifest fields；stage 标记属人，agent 只读不写

## Invariants

- 读数锚定：条目锚 courseware 知识点，sm-N 锚点 wikilink；粗粒度自陈合法，混合粒度共存；状态词开放——生疏、熟悉、熟练、掌握等，不立封闭词表
- 证据可溯：读数每条可溯证据；证据流行必带日期、出处、回链——assessments 页、notes 文件、session 页
- 信号权重：human 最高——用户原话、human 笔记、人复核；machine 次之——grades 与 submission 快照；ai 最低——origin: ai 笔记，弱证据，人复核方升权
- 应知不存：课程要求在 info.md，知识点全集在 courseware；user.md 只存已知、熟练、目标；差距消费时现算
- 目标层入读数：课程目标，加短期优先——带时效，过期即失效
- 错题分层：题级事实归 assessments 复盘区，可选行约定带知识点 wikilink 供反向索引；点级结论入读数；统计现算不落盘
- 更新双轨：agent 识别显著信号自发——成绩刷新后、笔记 stage 变更后；加用户明示——自述即认知输入。显著纪律：记显著不记日常
- 采集通道，v0.3 起，素材层 = bb v0.7 共居区：bb-teach 讲解落 notes/ ai 笔记，弱证据；bb-quiz 自测落 notes/testing/ 判分，machine 证据。两者是认知数据的主动采集面；产物落 bb 侧素材层，证据入流经用户确认；用法经源侧路由挂 bb-track 命令，装卸自动同步
- trust 复用：generated 随手写；读数天花板 machine-confirmed，证据流含 human 事件则 human-reviewed；stale_after 默认 14 天，页面可覆写；stale 时消费前先核对近窗证据或询问用户
- 不打 tags：单课路径直读，同 user-profile 先例
- 认知桥注册，v0.2 起，宪法准则 11：建档时若 user-profile 画像在场，维护其 `## 域认知` 节一行——bb 加 user.md 路径形；画像缺席跳过不代建，按需桥缺席容错
- 隐私：认知内容属实例数据，不入框架仓库与 test-repo

## Changelog

- 0.4 2026-10-04：命令接线升源侧路由——teach 与 quiz 的用法经其 manifest usage_routes 落入本枢纽命令，consumes 只余自属与工具；命令 Steps 收敛为骨架，细则归 usage 块
- 0.3 2026-10-04：采集通道披露与命令立设，teach/quiz 改造配套。notes/ 消费扩为共居区——ai 笔记弱证据，testing/ 考卷判分 machine 证据；stale 未核对前保守档消费；bb-track 命令立设为认知枢纽，teach 与 quiz 用法经 cmd-inject 挂载其注入区，装卸自动同步
- 0.2 2026-10-02：全局域批三——挂 user-profile 认知桥注册行，建档时维护画像 `## 域认知` 节，缺席容错；log 行带域标 --domain bb
- 0.1 2026-10-02：立设，组会裁定加两轮详谈收敛——认知档案两区制、笔记只读消费契约三属性、属地原生页首例；携 wiki v0.7 属地两形、bb-map v0.12 四桶豁免
