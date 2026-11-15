# agent-status-monitor-builder

一套可复用的 WorkBuddy Skill，用于**从零搭建、复刻或审计一套轻量本地「Agent 状态监控」小系统**：Agent 运行时事件采集 → 本地 HTTP 服务与单文件看板 → 状态灯 / OLED 实物反馈 → 断言驱动验证与一键体检。

A reusable WorkBuddy skill for building a local Agent status monitor: runtime event collection, a single-file dashboard, ESP32 status light / OLED feedback, and assertion-driven verification.

## 安装

```bash
git clone https://github.com/glensun810-ai/agent-status-monitor-builder.git \
  ~/.workbuddy/skills/agent-status-monitor-builder
```

clone 后该目录即为可直接加载的 Skill（`SKILL.md` 位于根目录）。也可下载 `dist/agent-status-monitor-builder.zip`，解压到 `~/.workbuddy/skills/` 后使用。

## 内容

| 路径 | 说明 |
|---|---|
| `SKILL.md` | 技能入口：触发场景、五层架构、九步流程、七条纪律、验收清单 |
| `references/01-全流程复盘与学习经验.md` | 五阶段复盘、12 条可迁移经验、5 个反模式 |
| `references/02-参考架构与接口契约.md` | 目录骨架、端点契约、前端计数契约、固件要点、脱敏替换表 |
| `references/03-工程纪律与验证体系.md` | 唯一真源、验证分层、WARN/FAIL 口径、标准改动流程 |
| `references/04-踩坑清单与排查手册.md` | 22 个真实坑：现象 → 根因 → 处置 → 预防 |
| `references/05-从零搭建操作手册.md` | Step 0–9 命令与验收点、macOS 注意、上线前清单 |
| `scripts/scaffold.py` | 生成目录骨架；`--from` 复制参考实现代码层 |
| `assets/*.template` | 脱敏后的 `paths.json` / `network.json` 模板 |
| `dist/*.zip` | 与仓库内容一致的脱敏分发包 |

## 快速开始

```bash
python3 scripts/scaffold.py --target /path/to/new-project
```

随后按 `references/05-从零搭建操作手册.md` 的 Step 2–9 逐层实现。若本机已有参考实现，可加 `--from <真源目录>` 复制代码层，并**立即执行终端打印的脱敏清单**。

本 Skill 提供方法论、目录骨架、契约范例、排坑手册与脚手架，**不包含可直接运行的业务代码**。

## 脱敏声明（公开仓库）

发布前已对全部文本文件与分发包执行全量脱敏，本仓库：

- 不含真实内网 IP、主机名 / mDNS 名、AP SSID 实值、设备标识或固件版本实值；
- 不含 `sharecode`、`app_id`、`lan_token`、访问码、WiFi 密码、应用卡片、线上站点地址、本机绝对路径、个人邮箱或任何密钥 / 令牌值；
- 模板中的 `192.168.1.x`、`your-mac.local`、`REPLACE-ME` 均为占位示例；`secrets.h`、`lan_token`、`sharecode`、`.genie` 等词仅作为「需要替换的字段名」出现，没有实际值；
- 文中 W 编号、验证项数、体积护栏、页面计数契约等是参考实现当时的工程示例值，不是凭据；
- Git 提交作者使用 GitHub noreply 邮箱，不暴露真实邮箱。

使用前仍须按 `references/05-从零搭建操作手册.md` Step 2，把全部占位值替换为自己的环境参数。若要把自己的实现公开，请再次执行该清单。

## 维护

本仓库与本机 Skill 副本分离维护。修改 Skill 后：同步本目录文件 → 重新生成 `dist/` 压缩包 → commit / push。压缩包由技能打包工具生成，内容与仓库中的技能文件逐字一致。
