# cuhksz：CUHK-SZ 学校域

## 设计概要

- **为什么存在**：学子在一所学校的完整图景 = 学籍身份（sis）+ 课业运行（bb）+ 制度规则（registry），三者共享同一身份源（学号）与同一统一认证（STS ADFS，bb-cli/sis-cli 实测共用）。域的使命是"一类外源的完整适配"，学校即这一类——bb 与 sis 是域内子系统而非平行域，对齐 lark 先例（企业基座 + docs/im/calendar 子域族）。本件是域基座：只立契约六问答案与身份证明，不持内容
- **关键裁定**：
  - 2026-10-05 所有者裁定：bb 由独立域**降为域内插件族**——迁移成本在单学期数据时点最低；伞域挂靠（域挂域）被否，语义分裂
  - bb 族五件**保留原名不冠前缀**（bb、bb-map……）——全链改名（manifest/命令/skill/changelog）零收益；"结构由插件各自规范"，命名惯例非强制
  - 域根只持身份页与子系统导航，速写归各子域（bb inbox / sis inbox）——避免双层维护
  - 个人官方 PDF（在读证明/非官方成绩单）是个人资产：走 vault 物化 + 域内 wikilink，不入 registry（制度文件区）
- **弃案**：cuhksz 与 sis 二名之争——域取 cuhksz（学校域，源不止 SIS）；bb 伞域挂靠——域挂域语义怪；bb 族冠前缀更名——改名爆炸

## Structure

- 数据区 `cuhksz/`（root 容器）：`bb/`（课程运行工作区，bb 域件辖）+ `registry/`（教务制度物化区，registry 域件辖）。sis 无数据区——查询即答不物化
- 属地 `wiki/cuhksz/`：`identity.md`（域声明页）+ `bb/` + `sis/` + `registry/`（各域件辖）
- 身份证明：identity.md 的 `sis` 块映射（student_id/college/school/major/admitted/status）与连接器身份一比一；数据源 sis-cli transcript

## Invariants

- 契约六问：外领地 cuhk.edu.cn 学校系统族；落地 = 双侧目录（数据区 + 属地）；身份证明 = identity.md sis 块映射；属地 wiki/cuhksz/；写模型归各子系统（bb 过程容器 / sis 只读查询 / registry 只增物化）；信任模型归各子系统，身份页 machine-confirmed
- 域内互引免桥：子系统插件相互读写（sis 成绩 → bb-track 证据流）是域内直引，不经准则 11 桥；跨域派生（todo/calendar/notes/认知桥）仍走桥
- 域可发现性：identity.md 即声明页（type: cuhksz）
- 隐私红线：学籍身份信息属实例数据不入框架仓库；identity.md 在实例库建档

## Changelog

- 0.1（2026-10-05）立设：域基座，bb 族五件挂靠迁入（wiki/bb/ → wiki/cuhksz/bb/，bb/ → cuhksz/bb/），sis/registry 子域首立
