#!/usr/bin/env python3
"""Generate a clean skeleton for a local Agent status monitor system.

Usage:
  python3 scaffold.py --target /path/to/new-project
  python3 scaffold.py --target /path/to/new-project --from /path/to/reference-truth
  python3 scaffold.py --target /path/to/new-project --from /path/to/ref --with-docs

The script never deletes existing files. Copying a reference implementation skips
secrets, caches, runtime event logs, media assets and history documents by default;
run the printed desensitization checklist afterwards.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import date
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
ASSETS = SKILL_ROOT / "assets"

DIRS = [
    "01-核心界面",
    "02-状态灯链路",
    "03-固件/wb_light",
    "04-验证",
    "05-运行配置",
    "06-文档",
    "07-归档",
    "08-视频号",
]

# 08-视频号/ 默认不复制：成片与素材体积大，且属原项目史实资产。
COPY_DIRS = [
    "01-核心界面",
    "02-状态灯链路",
    "03-固件",
    "04-验证",
    "05-运行配置",
]
COPY_TOP_FILES = ["sync_runtime.py", "health_check.py"]

SKIP_NAMES = {"__pycache__", ".DS_Store", ".git", "secrets.h", "lan_token"}
SKIP_SUFFIXES = {".pyc", ".zip", ".genie", ".bak", ".jsonl"}

README_TEXT = """# Agent 状态监控小系统（骨架）

> 由 agent-status-monitor-builder 脚手架生成于 {today}。本目录是**唯一真源**。

## 目录
- `01-核心界面/` 单文件 SPA + sw.js + 服务端 + manifest + 验证脚本（整体不可拆）
- `02-状态灯链路/` 采集 / 哨兵 / 门户 py 源副本 + ui_contract.json
- `03-固件/` 固件源码与编译 / 烧录规程；无网页配网，SSID 硬编码 config.h
- `04-验证/` 基线口径 + 专项 + 真浏览器脚本
- `05-运行配置/` launchd plist 只读存档
- `06-文档/` 交付报告与说明书
- `07-归档/` 历史版本备份
- `08-视频号/` 成片、脚本与可复现生成器（素材类，默认不随 --from 复制）

## 纪律（先读）
1. 只在本目录编辑；其它位置是镜像 / 注册点 / 归档。运行时事件流水也不在真源目录。
2. 路径只改 `paths.json`，网络只改 `network.json` 的 `params`；IP 漂移由 `/net` 动态返回。
3. `sync_runtime.py --check` 只读，`--apply` 才重建；`INVENTORY.json` 自动生成勿手改。
4. `health_check.py` 默认即 quick 只读（无 `--quick` 参数，仅 `--full` / `--act` / `--strict`）；真实板子下发须显式 `--act` 且人在场。
5. 改功能必补专项断言；老基线全绿不等于新功能已验；断言须校验真实 DOM，不写只查源码字面量的假绿断言。
6. 体积护栏与 `min_headroom` 不放宽；近预算时先落地后压缩，压缩器默认 dry-run 且带字面量保护，压缩后复跑全套断言。
7. 取不到数据显示未知 / 0，不造演示数据；真实覆盖天数诚实标注；人工目视项脚本不代签。
8. 每次改动在 `VERSION.md` 追加决策留痕；基准哈希变化记录前后值；**README 现役真值表须手工同步，sync 不代劳**。

## 下一步
参照技能 `references/05-从零搭建操作手册.md` 的 Step 2–9 逐层实现。
若使用 `--from` 复制了参考实现，先完成终端打印的脱敏清单。
"""

VERSION_TEXT = """# 版本与勘误编年史

> 增量追加，旧文原文不回改；冲突时追加勘误小节并注明「原文不回改」。
> 现役真值只写在 `README.md` 的现役状态表，本文件的历史数值是当时中间值。
> 同步脚本不会自动回写 README；每次真值变动须手工同步该表。

| 版本 | 日期 | 关键决策 / 变更 |
|---|---|---|
| W0 | {today} | 目录骨架建立，确定唯一真源与验证纪律 |
"""

BASELINE_TEXT = """# 验证基线口径（骨架）

- 基线 = 静态契约 + 端点/在线契约 + 对齐专项；项数由各套件实际输出累加，禁止硬编码。
- 每新增功能建 `verify_wXX.py` 专项，设 `bl=False` 独立判定，不混入老基线。
- 配置 / 状态类断言必须校验真实运行时对象：提取全部 elId 逐个比对 DOM id 集合，任一悬空即 FAIL；禁止只查源码字面量。
- 体积护栏、最小余量、SW 缓存名、`budget_revision`、`CANON_BASELINE` 变化须在 `VERSION.md` 留痕；护栏不放宽。
- 安全压缩后函数结束形如 `}function …`；按「换行 + `}` + 换行」提取函数体的断言改为按下一个 `function` 锚定，并复跑全部 `verify_*.py`。
- 环境态（板端断电 / 断网 / CDP 未就绪 / 瞬时竞态）记 WARN；代码 / 配置 / 契约 / 清单失败记 FAIL。
- 人工目视与实板下发（`--act`）按设计未命中，脚本不得伪造 PASS。
- 数据口径：`dur_s` 是相邻状态跃变间的任务周期，不是 AI 思考时长 / 人工工时；不完整自然日不做同口径日环比。
"""

DIR_NOTE = """本目录由脚手架创建。实现内容参见技能 `references/02-参考架构与接口契约.md`
与 `references/05-从零搭建操作手册.md`。运行时镜像内的路径不要在源码副本里批量替换。
"""

DESENSITIZE = [
    "network.json：lan / host / board_ip / board_mdns / ap_ssid / ap_url 全部换成目标环境值；ap_ssid 须与固件一致",
    "paths.json：mirror 路径、publish.entry_dir / app_id、线上站点 host 与 sharecode",
    "03-固件/wb_light/secrets.h 与 config.h：用 .example 重建，不保留原 WiFi SSID / 密码；固件无网页配网",
    "lan_token / 访问码 / .genie 应用卡片：重新生成，令牌文件权限 0600",
    "运行时事件流水 board_events.jsonl / board_audit.jsonl / 会话台账：不复制、不外发（不在真源目录）",
    "门户兼容开关（如 k_fw 交换）：确认互斥决策，不恢复已撤销的开关",
    "INVENTORY.json / CANON_BASELINE / 验证项数 / 体积护栏 / 计数契约：首次跑通后重算并留痕",
    "压缩过的页面：确认按换行提取函数体的断言已改为按下一个 function 锚定",
    "06-文档/、07-归档/、08-视频号/：默认不复制，避免把原项目史实与素材带进新项目",
]


def write_text(path: Path, text: str, force: bool) -> bool:
    if path.exists() and not force:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True


def copy_template(name: str, target: Path, force: bool) -> None:
    src = ASSETS / name
    if not src.exists():
        raise FileNotFoundError(f"missing asset: {src}")
    data = json.loads(src.read_text(encoding="utf-8"))
    dst = target / name.replace(".template", "")
    if dst.exists() and not force:
        return
    dst.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def safe_to_copy(path: Path) -> bool:
    if path.name in SKIP_NAMES:
        return False
    if any(path.name.endswith(suf) for suf in SKIP_SUFFIXES):
        return False
    if "__pycache__" in path.parts:
        return False
    return path.is_file()


def copy_reference(src_root: Path, target: Path, with_docs: bool, force: bool) -> int:
    count = 0
    rels: list[Path] = []
    for d in COPY_DIRS:
        base = src_root / d
        if base.exists():
            rels.extend(p.relative_to(src_root) for p in base.rglob("*") if safe_to_copy(p))
    if with_docs:
        base = src_root / "06-文档"
        if base.exists():
            rels.extend(p.relative_to(src_root) for p in base.rglob("*") if safe_to_copy(p))
    for f in COPY_TOP_FILES:
        p = src_root / f
        if safe_to_copy(p):
            rels.append(Path(f))

    for rel in rels:
        dst = target / rel
        if dst.exists() and not force:
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_root / rel, dst)
        count += 1
    return count


def main() -> int:
    ap = argparse.ArgumentParser(description="Scaffold an Agent status monitor project")
    ap.add_argument("--target", required=True, help="new project directory (absolute path preferred)")
    ap.add_argument("--from", dest="source", help="optional reference truth directory to copy code from")
    ap.add_argument("--with-docs", action="store_true", help="also copy 06-文档 from reference")
    ap.add_argument("--force", action="store_true", help="allow overwriting template files in a non-empty target")
    args = ap.parse_args()

    target = Path(args.target).expanduser().resolve()
    today = date.today().isoformat()

    if target.exists() and any(target.iterdir()) and not args.force:
        print(f"[ABORT] target is not empty: {target}\nUse --force to allow overwriting template files.")
        return 2

    for d in DIRS:
        (target / d).mkdir(parents=True, exist_ok=True)

    created = 0
    for rel, text in [
        (Path("README.md"), README_TEXT.format(today=today)),
        (Path("VERSION.md"), VERSION_TEXT.format(today=today)),
        (Path("04-验证/baseline.md"), BASELINE_TEXT),
        (Path("02-状态灯链路/README.md"), DIR_NOTE),
        (Path("01-核心界面/README.md"), DIR_NOTE),
    ]:
        created += int(write_text(target / rel, text, args.force))

    copy_template("paths.json.template", target, args.force)
    copy_template("network.json.template", target, args.force)
    created += 2

    copied = 0
    if args.source:
        src_root = Path(args.source).expanduser().resolve()
        if not src_root.is_dir():
            print(f"[ABORT] reference directory not found: {src_root}")
            return 2
        copied = copy_reference(src_root, target, args.with_docs, args.force)

    print(f"[OK] skeleton: {target}")
    print(f"     dirs={len(DIRS)}  generated_files={created}  copied_from_reference={copied}")
    print("     No existing file was deleted. 08-视频号/ is created but never copied from reference.")
    print("\n[必做] 脱敏与替换清单：")
    for i, item in enumerate(DESENSITIZE, 1):
        print(f"  {i}. {item}")
    print("\n[下一步] 参照 references/05-从零搭建操作手册.md Step 2-9；")
    print("          实现或复制 sync_runtime.py / health_check.py 后，先跑只读体检，再 --apply 重建清单。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
