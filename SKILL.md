---
name: agent-status-monitor-builder
description: This skill should be used when building, replicating or auditing a lightweight local "Agent status monitor" system: collecting Agent runtime events, serving a single-file dashboard over local HTTP, driving status lights / OLED hardware feedback, and keeping the whole thing maintainable with assertion-driven verification and one-command health checks. Trigger on requests such as 搭建 Agent 状态监控、状态灯、信息看板、hooks 事件采集、复刻这套监控系统、帮我搭一个智能体状态看板, or when designing a single-source-of-truth directory layout, truth/mirror sync, size budgets, version chronicles, verification baselines, a network-switch wizard, four-dimension heatmaps, or diagnosing offline-board, lost-preference, false-green assertions, compressed-function regex failures and near-budget page changes in such a system.
agent_created: true
---

# Agent 状态监控小系统 · 搭建指南

## 目的与边界

把「Agent 此刻在干什么」变成一套本地可看、可控制、可验证的小系统：运行时事件 → 采集/哨兵 → 本地 HTTP 服务与单文件看板 → 状态灯与 OLED 实物反馈 → 断言驱动的运维体检。参考实现为一套已落地的同类系统，现役 **W29**（W0–W29，2026-11-16；软件 W29 定稿、固件 `vX.Y.Z-info-wXX` 已烧录、运维负责人在场 12 项验收全 PASS 销项）。

本技能提供**方法论 + 目录骨架 + 契约范例 + 排坑手册 + 脚手架脚本**，不承诺一键生成完整可运行的业务代码。完整实现要么按手册自写，要么用 `--from` 从已有真源复制后脱敏改造。所有现役数值均为参考实现史实，复刻时按自身环境重算，不照抄。

## 何时使用

- 需要从零搭一套同类系统，或把已有原型收敛成可交付、可日常托管的结构。
- 需要设计：唯一真源目录、真源/运行时镜像同步、单点网络配置、体积护栏与近预算压缩、验证基线与一键体检、版本编年史与勘误留痕。
- 需要实现或审计：连接状态单一出口、换网向导（同网判定 / 救援 AP / 固件无网页配网声明）、热力图多维度（真实逐条 csv、真实覆盖天数、不画推测数据）、设置项状态反馈、按钮与定时器计数契约。
- 需要排查：板端离线误判、偏好刷新丢失、SW 缓存不更新、来源归属恒为 0、清单偏差误报、假绿断言、压缩后函数体正则失效、调用错函数被误判成竞态、launchd/TCC 导致服务起不来。
- 需要向第三方讲清「这套系统是怎么长出来的」以及哪些坑不要重踩。

## 参考架构（五层）

```
[ Agent hooks / 适配器 ] → 事件 jsonl / 状态文件
        ↓
[ 采集 · 哨兵 · 门户 8420 ] → 板端 HTTP /cmd
        ↓                         ↓
[ 8080 自包含服务 + 单文件 SPA ]  [ ESP32-S3 三色灯 + OLED / NVS / AP 应急页 ]
   · /net + /api 真值 → 换网向导（同网判定，纯前端）    · 固件无网页配网，SSID 写死 config.h
   · /stats 自带逐条 csv → 四维度热力图（不造推测数据）
        ↓
[ 公网静态连接向导：只指路，无后端、不造假数据 ]
```

分层职责、目录骨架、端点契约、W29 新增能力、前端计数契约、现役真值表、固件要点与脱敏清单见 `references/02-参考架构与接口契约.md`。

## 从零搭建流程

按顺序执行，每步的验收点见 `references/05-从零搭建操作手册.md`。

| 步 | 动作 | 要点 |
|---|---|---|
| 0 | 划边界 | 真实数据源、本地入口、诚实降级口径；先写清排除项与体积硬上限 |
| 1 | 建骨架 | 运行 `scripts/scaffold.py --target <dir>`；有参考实现时加 `--from <真源>` |
| 2 | 配置脱敏 | 只改 `network.json` / `paths.json`；逐项替换凭据、IP、sharecode、应用卡片、固件 `config.h` |
| 3 | 最小闭环 | hooks → 状态文件 → 哨兵 → 板；断哨兵须灭灯（失效保护） |
| 4 | 8080 服务与 SPA | 端点契约、三档轮询 + 退避、计数契约、SW/manifest、体积护栏；近预算时先落地后压缩 |
| 5 | 8420 门户与下发 | 访问码 POST 配对、`/ctl` 同源代理、成败以回读为准 |
| 6 | 固件 | 编译 → 整片备份 → 只写 `0x10000` → 读回 md5 → `/api ver` 回读 |
| 7 | 单一同步通道 | `--check` / `--apply` / `--rollback` / `--sync-links`；`INVENTORY.json` 自动生成 |
| 8 | 验证体系 | 基线 + 专项（`bl=False`）+ 真契约断言（校验真实 DOM）+ 真浏览器往返 + 一键体检 |
| 9 | 运维与留痕 | 先诊断后重建；一次全量复验；编年史追加决策；**手工同步 README 现役真值表** |

## 必须遵守的纪律（摘要）

1. 只在一个根目录编辑；其它位置一律称镜像 / 注册点 / 归档。
2. 配置单点化，页面常量由脚本生成，运行时展示值优先问 `/net`。
3. 同步只有一条通道；清单自动生成，禁止手改；`--sync-links` 必须显式开启。
4. 体检只读诊断（默认即 quick，**无 `--quick` 参数**，只有 `--full` / `--act` / `--strict`），`--apply` 才重建；实板下发必须 `--act` 且需人工在场。
5. 改功能必补专项断言；老基线全绿不代表新功能已验；基准哈希失配须留痕重算。
6. 断言必须校验真实对象：状态 elId 要逐个比对 DOM id 集合，只查源码字面量属「假绿」。
7. 体积护栏与 `min_headroom` 不放宽；按实测安全压缩上限报价，压缩用带字面量保护的脚本且 `--apply` 才写盘。
8. 压缩后函数结束形如 `}function …`，按 `\n}\n` 提取函数体的断言必须改成按下一个 `function` 锚定。
9. 现役真值表不会被同步脚本自动回写，每次真值变动须手工同步 README 与编年史。
10. 环境态（板端断电 / 断网 / CDP 未就绪 / 瞬时竞态）记 WARN，代码与契约失败才记 FAIL。
11. 取不到数据就显示未知 / 0，不用演示值；真实覆盖天数诚实标注；人工目视项脚本不代签。

完整条目与验证分层见 `references/03-工程纪律与验证体系.md`。

## 高频故障速查

按现象查 `references/04-踩坑清单与排查手册.md`：偏好刷新丢失（合并语义 + 真浏览器往返）、静态断言假绿、悬空状态 elId、调用错函数被当成竞态、压缩后函数体正则失效、近预算改动按理论空白量报价、手机拿不到新页（SW 缓存名）、来源恒 0（`_derive_event()` 写死 src）、板端离线误判、macOS TCC / launchd、固件无网页配网、烧录失败（数据线）、中文 OLED 截断、清单偏差。

W29 全过程复盘（P0 / P1 / A4、预算数字链、假绿断言根因、勿重犯清单）见 `references/01-全流程复盘与学习经验.md` 第六节。

## 资源索引

| 文件 | 何时读 |
|---|---|
| `references/01-全流程复盘与学习经验.md` | 理解设计动机、阶段划分、可迁移经验与反模式；第六节为 W29 现役复盘与预算数字链 |
| `references/02-参考架构与接口契约.md` | 设计分层、目录、端点、W29 新增能力、前端计数契约、**现役真值表**、固件参数、脱敏替换表 |
| `references/03-工程纪律与验证体系.md` | 建立验证体系、写体检脚本、定分级口径、走标准改动流程 |
| `references/04-踩坑清单与排查手册.md` | 出现故障时按现象定位，或做改动前的风险自查 |
| `references/05-从零搭建操作手册.md` | 实际动手，逐步命令与验收点、macOS 注意、上线前清单 |
| `scripts/scaffold.py` | 生成目录骨架；`--from` 复制参考实现代码层 |
| `assets/paths.json.template`、`assets/network.json.template` | 脚手架使用的脱敏配置模板 |

大文件按需检索：在 references 中用关键词 `CANON_BASELINE`、`NVS`、`SW 缓存`、`renderLinkState`、`heat-dim`、`--act`、`TCC`、`ovSaveTag` 直接定位，不要整篇灌入上下文。

## 验收清单（收尾前逐条确认）

- [ ] 唯一真源、单点配置、单一同步通道已落地；`--check` 偏差 0
- [ ] `--full` 体检无 FAIL，WARN 均可解释
- [ ] 新功能有独立专项断言，且跑过真浏览器往返
- [ ] 所有配置/状态类 elId 在真实 DOM 中存在；无只查源码字面量的假绿断言
- [ ] 页面在体积硬上限内，SW 缓存名与 `budget_revision` 已同步 bump
- [ ] 压缩后全套 `verify_*.py` 复跑通过（含函数体提取类断言）
- [ ] 断网 / 服务停 / 板端断电三种场景显示诚实降级态
- [ ] 凭据全部脱敏，令牌权限 0600，固件 `config.h` 未带出原 WiFi 密码
- [ ] `VERSION.md` 已追加决策留痕，基准哈希变化有前后值记录；README 现役真值表已手工同步
- [ ] 「需人工在场项」单列且未伪报 PASS

## 诚实边界

系统自包含 ≠ 零系统注册：launchd plist、hooks 软链、令牌、应用卡片、线上托管站、运行时事件流水与烧在板上的固件都在目录之外。纯软件无法替代烧录、按键手感、OLED 目视与断电重启验收；固件无网页配网，换 WiFi 必须改 `config.h` 重编译烧录，前端向导只做同网判定与指路。参考实现现役：8080 已于 18:35 正规化为 launchd 常驻（KeepAlive 实测通过、临时 keepalive 脚本 已退出）、线上分享链接 18:43 已同步 W29 前端；剩余工作为 P2′ 月/季聚合（事件按月归档前置，已报价获运维负责人拍板、另开会话立为 W30）、P3′ 视频号后期与本 skill 的真实复刻试用，以及逐行就地状态位（受页面余量限制另案）。分发给他人时先执行脱敏清单，并提醒对方按自身环境重算所有计数与基准值。
