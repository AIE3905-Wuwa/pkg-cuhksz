# registry：教务制度子域

## 设计概要

- **为什么存在**：培养方案、GE/体育/国情修读规则等制度文件决定"该修什么、怎样算达标"——学业的制度性框架。源在教务处官网（registry.cuhk.edu.cn），无 API 无连接器，人工下载物化 + 指针导航是当前唯一通路
- **族内位置**：cuhksz 域内子系统，与 bb/sis 平级；制度对照双源之一（制度源）——动态源是 sis-cli 的学位进度报告（DPR）
- **关键裁定**：
  - **指针优先、物化按需**（投影密度随翻译成本）：全校 40+ 专业 × 多年级批次 PDF 全量物化不值——索引页给全量指针（URL），仅用户相关方案物化落区
  - 制度文件区隔个人资产：官网公开 PDF（培养方案）住 cuhksz/registry/；个人官方文件（在读证明/成绩单）走 vault——分界线是"公开制度 vs 个人证件"
  - trust 用 human-reviewed + 版本锚（公文/Senate 编号）而非 TTL：制度变更靠对版节奏（学期初 + 公文日）不靠过期
  - PDF 域名纪律：registry.cuhk.edu.cn 托管（www.cuhk.edu.cn 同路径 403）——索引与下载均用 registry 域
- **弃案**：全量物化——翻译成本为零的用指针即可；爬官网自动化——无稳定 API，人工对版足够

## Structure

- 物化区 `cuhksz/registry/`：官网 PDF 原名平铺，只增；版本批次进位（2025-26 版与 2026-27 版并存）
- 属地 `wiki/cuhksz/registry/`：schemes.md 索引页（学院→专业→方案页 URL；建页源 /page/20 与 /page/22 族，含双主修/联合课程/副修）+ 代理页（registry 块映射 + 蒸馏 + 对版记录）

## Invariants

- 官网结构（2026-10-05 实测）：总门户 /page/19（学术课程总表，按入学年级 5 批）+ /page/20（专业清单）+ /page/21（GE）+ /page/22（手册索引）；每专业独立 /page/{id}（内含按年级 PDF 下载区）；PDF 在 sites/default/files/ 路径
- 只增不覆写：新版批次进位，旧版保留（历史年级仍适用）
- 对版节奏：学期初 + Senate 公文日；页面无日期，以 PDF Last-Modified 抽查
- trust human-reviewed + edition 版本锚；无 stale_after
- 对照双源：本区制度条文（权威）+ DPR 动态现算（实时）——结论经确认入 notes 回链

## Changelog

- 0.1（2026-10-05）立设：随 cuhksz 域首立；全校 9 学院 + 双主修/联合/副修指针清单已完成官网实测搜集（42 专业页逐一验证）
