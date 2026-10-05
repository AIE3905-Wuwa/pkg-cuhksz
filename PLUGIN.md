# sis：学籍制度子域

## 设计概要

- **为什么存在**：学籍信息（成绩/历史/注册/考试/身份）是学子的制度性事实，源在 SIS（PeopleSoft CS），查询即答、全可再生。与 bb（课程运行）同属学校域、互补成图景：bb 管过程，sis 管制度事实
- **族内位置**：cuhksz 域内子系统，与 bb 族平级；身份数据反哺域根 identity.md；成绩作为 machine 证据域内直引 bb-track（免跨域桥——合一收益首例）
- **关键裁定**：
  - **查询即答不默认投影**（2026-10-05）：SIS 连接器在场、term 交互已通，wiki 侧只留速写页——不预立 grades.md 等枚举页，详情页涌现制（对齐"架构不枚举"）
  - 课表源补缺：log 挂缺的"课表源与课后触发"由本域补上——sis schedule → calendar 派生
  - 官方文件分治：非官方成绩单 PDF 可拉（View Report 纯查询）但属个人资产走 vault；官方成绩单申请是写操作，永不入域
- **弃案**：逐学期成绩落档页——数据全量可再生（连接器随时重拉），落档徒增维护；本地 sis 数据区——无物化需求

## Structure

- 属地 `wiki/cuhksz/sis/`：inbox.md 速写页（近窗：课表概要/注册窗口/holds/成绩快照；行标学期；整页可再生短 TTL，缺席即建）
- 无数据区：不物化（区别于 bb 的课程工作区）
- 连接器 sis-cli（connectors/sis-cli/）：ADFS OAuth2 同源 + PeopleSoft PIA 适配（PS_DEVICEFEATURES 破壳、psc+PTCNAV 组件直击、term radio POST），全只读

## Invariants

- 只读红线：选课/退课/换课/提交/官方申请类写操作永不入域（真实学籍后果）；唯一 POST 是 term 选择的 Continue 查询
- trust 天花板 machine-confirmed；stale_after = 拉取日 + TTL（默认 1 天速写；日期粒度）；agent 即同步器
- 单向派生只出不回：注册窗口临期 → todo；课表/考试安排 → calendar；学期成绩 → bb-track 证据流（域内直引，经用户确认）；高价值结论 → notes 回链
- 隐私红线：成绩与学籍数据属实例数据不入框架仓库；CLI 输出只在终端与对话
- 凭据纪律：~/.sis-cli/ 本机存放，绝不入库

## Changelog

- 0.1（2026-10-05）立设：随 cuhksz 域首立；sis-cli v0.2 连接器先行在场
