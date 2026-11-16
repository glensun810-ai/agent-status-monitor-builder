# agent-status-monitor-builder

一套可复用的 WorkBuddy Skill，用于**从零搭建、复刻或审计一套轻量本地「Agent 状态监控」小系统**：Agent 运行时事件采集 → 本地 HTTP 服务与单文件看板 → 状态灯 / OLED 实物反馈 → 断言驱动验证与一键体检。

A reusable WorkBuddy skill for building a local Agent status monitor: runtime event collection, a single-file dashboard, ESP32 status light / OLED feedback, and assertion-driven verification.

> 当前对应参考实现 **W29**（2026-11-16）现役状态。仓库为**公开脱敏版**，工程契约与本机副本一致，环境实值按下方声明通用化。

## 安装

```bash
git clone https://github.com/glensun810-ai/agent-status-monitor-builder.git \
  ~/.workbuddy/skills/agent-status-monitor-builder
```

clone 后该目录即为可直接加载的 Skill（`SKILL.md` 位于根目录）。也可下载 `dist/agent-status-monitor-builder.zip`，解压到 `~/.workbuddy/skills/` 后使用。压缩包内容由技能打包工具从干净的暂存目录生成，与仓库中的 9 个技能文件逐字一致，不含 `.git` / `README.md` / `dist` 自身。

## 内容

| 路径 | 说明 |
|---|---|
| `SKILL.md` | 技能入口：触发场景、五层架构、九步流程、**11 条纪律**、高频故障速查、验收清单与诚实边界 |
| `references/01-全流程复盘与学习经验.md` | **六阶段**复盘、**16 条**可迁移经验、**9 个**反模式，第六节为 W29 预算数字链与 A4 回归复盘 |
| `references/02-参考架构与接口契约.md` | 目录骨架、端点契约、**W29 新增能力契约**、前端计数契约、**现役真值表**、固件要点、脱敏替换表 |
| `references/03-工程纪律与验证体系.md` | **10 条**硬纪律、验证分层与项数口径、WARN/FAIL 分级、一次改动的标准动作 |
| `references/04-踩坑清单与排查手册.md` | **28 个**真实坑：环境 5 / 前端数据 13 / 硬件验收 7 / 协作成本 3，按「现象 → 根因 → 处置 → 预防」组织 |
| `references/05-从零搭建操作手册.md` | Step 0–9 命令与验收点、macOS 注意、上线前 11 项清单 |
| `scripts/scaffold.py` | 生成目录骨架（含 `08-视频号/`）；`--from` 复制参考实现代码层，跳过密钥、事件流水与素材 |
| `assets/*.template` | 脱敏后的 `paths.json` / `network.json` 模板，含固件无网页配网说明 |
| `dist/*.zip` | 与仓库技能文件一致的脱敏分发包 |

## 快速开始

```bash
python3 scripts/scaffold.py --target /path/to/new-project
```

随后按 `references/05-从零搭建操作手册.md` 的 Step 2–9 逐层实现。若本机已有参考实现，可加 `--from <真源目录>` 复制代码层，并**立即执行终端打印的脱敏清单**。

触发语句示例：`搭建 Agent 状态监控`、`复刻这套状态灯系统`、`帮我搭一个智能体状态看板`、`设计唯一真源与体积护栏`、`换网向导 / 热力图四维度怎么接真实数据`、`排查偏好刷新丢失或假绿断言`。

本 Skill 提供方法论、目录骨架、契约范例、排坑手册与脚手架，**不包含可直接运行的业务代码**；所有数值都是参考实现史实，复刻时须按自身环境重算。

## 本次更新（W29 · 2026-11-16）

相对上一版（`8e9ffb4`，W28 口径）的主要变化：

1. **现役真值对齐**：`index.html` 195,966 B、`CANON_BASELINE` 重算、INVENTORY 188 文件、契约计数 id 253 / **button 109**、SW `wb-board-w29-v1`、W29 专项 **101 项**、`--full` **854/855 PASS · WARN 1 · FAIL 0**、`--full --act` 887/888 PASS；旧版的按钮 116 与 754/754 口径已作废。
2. **新增能力契约**：纯前端换网向导（`/net` + `/api` 同网判定、救援 AP、**固件无网页配网**声明）、热力图四维度（`/stats` 自带逐条 csv、真实覆盖天数、空维度不绘推测数据、暂不做月/季）、`renderLinkState()` 连接状态单一出口、`setMonitorPaused(v)` 合并双实现、状态 elId **必须在真实 DOM 中存在**的通用断言。
3. **新增工程教训**：A4-①「调用错函数」不是竞态、A4-② **假绿断言**（只查源码字面量不查 DOM）、压缩后函数结束变 `}function …` 的断言锚点、理论空白 8,180 B ≠ 实测可压缩 3,077 B、护栏与 `min_headroom` 不放宽、先落地后压缩、README 现役真值表不会被同步脚本自动回写。
4. **新增 W29 预算数字链**：194,002 → 195,250 → 194,942 → 200,738（超硬上限 ABORT）→ 199,030 → 195,953（安全压缩）→ 195,966 B（A4 修复），以及基准哈希的留痕链。
5. **脚手架与模板**：新增 `08-视频号/`、跳过 `.jsonl` 运行时数据、脱敏清单补 `config.h` 的 WiFi 凭据、纪律文本补真契约断言与体积预算；两个模板补「固件无网页配网」「运行时事件流水不入真源清单」。
6. **运维事实纠偏**：8080 已正规化为 launchd 常驻（KeepAlive 拉起实测通过，临时 keepalive 脚本退出）、线上静态连接向导已同步 W29 前端；月/季聚合（W30）与 skill 真实复刻试用列为后续工作。

## 关键契约速览（示例值，复刻须重算）

| 项 | 参考实现 W29 值 |
|---|---|
| 体积护栏 / 最小余量 | 200,000 B / 4,000 B ⇒ 硬上限 196,000 B；现役余量 4,034 B（可新增仅 34 B） |
| 计数契约 | id 253 全唯一 / button 109 / setInterval 2 / style 2 / script 3；新功能不新增定时器 |
| 验证基线 | 504 项（450 + W19 54），自动命中 456 项；专项设 `bl=False` 不计入基线 |
| 专项项数 | budget 25 / w19 54 / w21 33 / w23 37 / w24 23 / w25 44 / w26 48 / w27 76 / **w29 101** |
| 数据口径 | `dur_s` 是相邻状态跃变间的任务周期（单条封顶 900s），≠ AI 思考时长 / 人工工时；不完整自然日不做日环比 |
| 命名铁律 | 官方 **TRAE CN** / 短码 `trae`；其余写法均属错别字 |

## 脱敏声明（公开仓库）

发布前已对全部文本文件与分发包执行全量脱敏，本仓库：

- **不含**真实内网 IP、主机名 / mDNS 名、AP SSID 实值、设备标识、固件版本实值、临时脚本的本机绝对路径；
- **不含** `sharecode`、`app_id`、`lan_token`、访问码、WiFi 密码、应用卡片、线上站点地址、个人邮箱或任何密钥 / 令牌值；
- 固件版本统一写成 `vX.Y.Z-info-wXX`，AP SSID 统一写成 `ESP32-Direct`，临时自愈托管统一称「临时 keepalive 脚本」，内部人称统一称「运维负责人」；
- 模板中的 `192.168.1.x`、`your-mac.local`、`REPLACE-ME`、`ESP32-Direct-REPLACE` 均为占位示例；`secrets.h`、`config.h`、`lan_token`、`sharecode`、`.genie` 等词仅作为「需要替换的字段名」出现，没有实际值；
- 文中 W 编号、页面字节数、验证项数、体积护栏、计数契约、规范化哈希等是参考实现当时的**工程示例值**，不是凭据；`192.168.4.1` 为板载 AP 通用地址；
- Git 提交作者使用 GitHub noreply 邮箱，不暴露真实邮箱。

使用前仍须按 `references/05-从零搭建操作手册.md` Step 2，把全部占位值替换为自己的环境参数。若要把自己的实现公开，请再次执行该清单。

## 与本机 Skill 副本的关系

本机 `~/.workbuddy/skills/agent-status-monitor-builder/` 是内部工作副本，保留参考实现的完整真值；本仓库是它的**公开脱敏镜像**。两者的方法论、目录、端点、计数契约、W29 全部能力与排坑结论一致，仅上节所列的 4 类环境实值 / 内部叙事被通用化。同步时先复制 9 个技能文件，再对公开副本执行通用化，最后重新打包并提交。

## 维护

```bash
# 1) 同步并通用化 9 个技能文件后，用干净暂存目录重打包
python3 <skill-creator>/scripts/package_skill.py \
  /path/to/stage/agent-status-monitor-builder ./dist

# 2) 用 SSH 推送（提交作者用 noreply 邮箱）
git -c user.name=glensun810-ai \
    -c user.email=glensun810-ai@users.noreply.github.com \
    commit -m "Update skill to WXX state"
git push origin HEAD
```

推送走 `git@github.com:glensun810-ai/agent-status-monitor-builder.git`（SSH），不经过 HTTP 代理。每次改动遵循 Skill 自身的纪律：补断言 → 只读体检 → 显式同步 → 一次全量复验 → 编年史留痕 → 手工维护现役真值表；提交信息写明本次变更与脱敏口径。
