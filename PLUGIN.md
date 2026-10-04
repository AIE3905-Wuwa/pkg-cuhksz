# bb-quiz：出题自测（testing 消费侧）

bb-track 管「用户的认知状态是什么」，bb-teach 管「教」（teaching 消费侧），本插件管「考」（testing 消费侧）——用户指定范围 + 可选样例，生成英文试题 + 中文解析帮用户自测；作答后判分回流认知档案（machine 证据）。考卷不是课程原有物，是认知采集所需的过程素材——落 bb 侧素材层（bb v0.7 notes/testing/ 子区，term/course 双维随域），不立 wiki 页、不立根容器。

## Structure

- 零自有领地（除考卷子区）：考卷落 `bb/<term>/<course>/notes/testing/`，每测一组两份——`<名>-试题.md`（英文题目）+ `<名>-答案.md`（中文解析 + `## 判分` 追记区）；ai 产物只增，重测出新卷、旧卷留档（复盘价值）
- 工作流：解析输入 → 读知识点全集 → 读用户认知 → 定题型与难度中值 → 读教学纪要（best-effort）→ 选题 → 出题 → 写解析 → 落盘 → 判分（作答后）→ 回写

## Invariants

- 题型参照样例（单选/多选/填空/简答/计算/证明…，不枚举）；难度 = 认知层级 1-5（记忆/理解/应用/分析/综合），中值 M 对齐样例（fallback：已知作业 → 用户习惯）——M 为 LLM 语义判断、三层近似叠合的软约束，实际保证粒度 = 生疏偏易打底、掌握偏难挑战
- 题目英文、术语对齐 courseware `## 专有名词` 英中对照；解析中文
- 不越界：知识点全集 = courseware sm-N ∩ 用户范围；越界弃题重出（除非用户明示）——语义约束，出题侧自检 + 附检 warning 级
- 解析标注知识点 + sm-N wikilink（位置即出身）
- 参照 bb-track：熟练度决定选题与难度分布；stale 未核对前保守档；冷启动（无档案）全场未锚点、均匀出题
- **判分回流（v0.2 立设）**：作答后逐题判定，答案页追记 `## 判分`（日期 + 逐题对错 + 得分）；错题点与总体表现经用户确认回写 user.md 证据流（出处 machine 自测）——machine 证据，显著者按收敛纪律改读数；考卷本体是素材不是档案，档案只收结论
- 教学纪要 best-effort：读 notes/ ai 笔记（origin: ai，teach 沉淀）避免重复、重点测刚教；缺席或无笔记静默跳过（teach 默认产物即笔记，断链不存在）
- 写边界：不写 bb/ 拉取物；不碰 notes/ 中人的笔记与其他 ai 笔记（考卷子区只增）；user.md 回写经 bb-track 契约、经用户确认
- 隐私：考卷与判分内容属实例数据，不入框架仓库与 test-repo（notes/testing/ 随 bb/ 数据区语义忽略）

## Changelog

- 0.2（2026-10-04）改造（自 bb-exam v0.1 更名重构）：exams/ 根容器废除，考卷落 bb/<term>/<course>/notes/testing/（bb v0.7 素材层，term 维度恢复）；更名 quiz——informal 自测，与 bb-map assessments 管的 formal exam 划界；判分回流立设（machine 证据经确认入 user.md，闭环补全）；越界与字段检查降 warning；教学纪要改读 notes/ ai 笔记（best-effort）
- 0.1（2026-10-04，bb-exam 名下）立设：testing 消费侧插件 + 命令 + exams/ 容器，五要求落地（题型/难度对齐、术语一致、不越界、解析回链、参照认知档案）
