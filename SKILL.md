---
name: agent-status-monitor-builder
description: This skill should be used when building, replicating or auditing a lightweight local "Agent status monitor" system: collecting Agent runtime events, serving a single-file dashboard over local HTTP, driving status lights / OLED hardware feedback, and keeping the whole thing maintainable with assertion-driven verification and one-command health checks. Trigger on requests such as 搭建 Agent 状态监控、状态灯、信息看板、hooks 事件采集、复刻这套监控系统、帮我搭一个智能体状态看板, or when designing a single-source-of-truth directory layout, truth/mirror sync, size budgets, version chronicles, verification baselines, or diagnosing offline-board and lost-preference failures in such a system.
agent_created: true
---

# Agent 状态监控小系统 · 搭建指南

## 目的与边界

把「Agent 此刻在干什么」变成一套本地可看、可控制、可验证的小系统：运行时事件 → 采集/哨兵 → 本地 HTTP 服务与单文件看板 → 状态灯与 OLED 实物反馈 → 断言驱动的运维体检。参考实现来自一套已落地的同类小系统（W0–W28 全流程，软件已定稿、固件已烧录）。

本技能提供**方法论 + 目录骨架 + 契约范例 + 排坑手册 + 脚手架脚本**，不承诺一键生成完整可运行的业务代码。完整实现要么按手册自写，要么用 `--from` 从已有真源复制后脱敏改造。

## 何时使用

- 需要从零搭一套同类系统，或把已有原型收敛成可交付、可日常托管的结构。
- 需要设计：唯一真源目录、真源/运行时镜像同步、单点网络配置、体积护栏、验证基线与一键体检、版本编年史与勘误留痕。
- 需要排查：板端离线误判、偏好刷新丢失、SW 缓存不更新、来源归属恒为 0、清单偏差误报、launchd/TCC 导致服务起不来。
- 需要向第三方讲清「这套系统是怎么长出来的」以及哪些坑不要重踩。

## 参考架构（五层）

```
[ Agent hooks / 适配器 ] → 事件 jsonl / 状态文件
        ↓
[ 采集 · 哨兵 · 门户 8420 ] → 板端 HTTP /cmd
        ↓                         ↓
[ 8080 自包含服务 + 单文件 SPA ]  [ ESP32-S3 三色灯 + OLED / NVS / AP 应急页 ]
        ↓
[ 公网静态连接向导：只指路，无后端、不造假数据 ]
```

分层职责、目录骨架、端点契约、前端计数契约、固件要点与脱敏清单见 `references/02-参考架构与接口契约.md`。

## 从零搭建流程

按顺序执行，每步的验收点见 `references/05-从零搭建操作手册.md`。

| 步 | 动作 | 要点 |
|---|---|---|
| 0 | 划边界 | 真实数据源、本地入口、诚实降级口径；先写清排除项 |
| 1 | 建骨架 | 运行 `scripts/scaffold.py --target <dir>`；有参考实现时加 `--from <真源>` |
| 2 | 配置脱敏 | 只改 `network.json` / `paths.json`；逐项替换凭据、IP、sharecode、应用卡片 |
| 3 | 最小闭环 | hooks → 状态文件 → 哨兵 → 板；断哨兵须灭灯（失效保护） |
| 4 | 8080 服务与 SPA | 端点契约、三档轮询 + 退避、计数契约、SW/manifest |
| 5 | 8420 门户与下发 | 访问码 POST 配对、`/ctl` 同源代理、成败以回读为准 |
| 6 | 固件 | 编译 → 整片备份 → 只写 `0x10000` → 读回 md5 → `/api ver` 回读 |
| 7 | 单一同步通道 | `--check` / `--apply` / `--rollback` / `--sync-links`；`INVENTORY.json` 自动生成 |
| 8 | 验证体系 | 基线 + 专项（`bl=False`）+ 真浏览器往返 + 一键体检 |
| 9 | 运维与留痕 | 先诊断后重建；一次全量复验；编年史追加决策 |

## 必须遵守的纪律（摘要）

1. 只在一个根目录编辑；其它位置一律称镜像 / 注册点 / 归档。
2. 配置单点化，页面常量由脚本生成，运行时展示值优先问 `/net`。
3. 同步只有一条通道；清单自动生成，禁止手改；`--sync-links` 必须显式开启。
4. 体检只读诊断，`--apply` 才重建；实板下发必须 `--act` 且需人工在场。
5. 改功能必补专项断言；老基线全绿不代表新功能已验；基准哈希失配须留痕重算。
6. 环境态（板端断电 / 断网 / CDP 未就绪 / 瞬时竞态）记 WARN，代码与契约失败才记 FAIL。
7. 取不到数据就显示未知 / 0，不用演示值；人工目视项脚本不代签。

完整条目与验证分层见 `references/03-工程纪律与验证体系.md`。

## 高频故障速查

按现象查 `references/04-踩坑清单与排查手册.md`：偏好刷新丢失（合并语义 + 真浏览器往返）、静态断言假绿、手机拿不到新页（SW 缓存名）、来源恒 0（`_derive_event()` 写死 src）、板端离线误判、macOS TCC / launchd、烧录失败（数据线）、中文 OLED 截断、清单偏差。

## 资源索引

| 文件 | 何时读 |
|---|---|
| `references/01-全流程复盘与学习经验.md` | 需要理解设计动机、阶段划分、十二条可迁移经验与五个反模式；给新人讲来龙去脉 |
| `references/02-参考架构与接口契约.md` | 设计分层、目录、端点、前端计数契约、固件参数、脱敏替换表 |
| `references/03-工程纪律与验证体系.md` | 建立验证体系、写体检脚本、定分级口径、走标准改动流程 |
| `references/04-踩坑清单与排查手册.md` | 出现故障时按现象定位，或做改动前的风险自查 |
| `references/05-从零搭建操作手册.md` | 实际动手，逐步命令与验收点、macOS 注意、上线前清单 |
| `scripts/scaffold.py` | 生成目录骨架；`--from` 复制参考实现代码层 |
| `assets/paths.json.template`、`assets/network.json.template` | 脚手架使用的脱敏配置模板 |

大文件按需检索：在 references 中用关键词 `CANON_BASELINE`、`NVS`、`SW 缓存`、`/align`、`--act`、`TCC` 直接定位，不要整篇灌入上下文。

## 验收清单（收尾前逐条确认）

- [ ] 唯一真源、单点配置、单一同步通道已落地；`--check` 偏差 0
- [ ] `--full` 体检无 FAIL，WARN 均可解释
- [ ] 新功能有独立专项断言，且跑过真浏览器往返
- [ ] 断网 / 服务停 / 板端断电三种场景显示诚实降级态
- [ ] 凭据全部脱敏，令牌权限 0600
- [ ] `VERSION.md` 已追加决策留痕，基准哈希变化有前后值记录
- [ ] 「需人工在场项」单列且未伪报 PASS

## 诚实边界

系统自包含 ≠ 零系统注册：launchd plist、hooks 软链、令牌、应用卡片、线上托管站与烧在板上的固件都在目录之外。纯软件无法替代烧录、按键手感、OLED 目视与断电重启验收。分发给他人时先执行脱敏清单，并提醒对方按自身环境重算所有计数与基准值。
