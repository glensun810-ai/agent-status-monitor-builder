#!/usr/bin/env python3
"""Generate a clean skeleton for a local Agent status monitor system.

Usage:
  python3 scaffold.py --target /path/to/new-project
  python3 scaffold.py --target /path/to/new-project --from /path/to/reference-truth
  python3 scaffold.py --target /path/to/new-project --from /path/to/ref --with-docs

The script never deletes existing files. Copying a reference implementation skips
secrets, caches and history documents by default; run the printed desensitization
checklist afterwards.
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
]

COPY_DIRS = [
    "01-核心界面",
    "02-状态灯链路",
    "03-固件",
    "04-验证",
    "05-运行配置",
]
COPY_TOP_FILES = ["sync_runtime.py", "health_check.py"]

SKIP_NAMES = {"__pycache__", ".DS_Store", ".git", "secrets.h", "lan_token"}
SKIP_SUFFIXES = {".pyc", ".zip", ".genie", ".bak"}

README_TEXT = """# Agent 状态监控小系统（骨架）

> 由 agent-status-monitor-builder 脚手架生成于 {today}。本目录是**唯一真源**。

## 目录
- `01-核心界面/` 单文件 SPA + sw.js + 服务端 + manifest + 验证脚本（整体不可拆）
- `02-状态灯链路/` 采集 / 哨兵 / 门户 py 源副本 + ui_contract.json
- `03-固件/` 固件源码与编译 / 烧录规程
- `04-验证/` 基线口径 + 专项 + 真浏览器脚本
- `05-运行配置/` launchd plist 只读存档
- `06-文档/` 交付报告与说明书
- `07-归档/` 历史版本备份

## 纪律（先读）
1. 只在本目录编辑；其它位置是镜像 / 注册点 / 归档。
2. 路径只改 `paths.json`，网络只改 `network.json` 的 `params`。
3. `sync_runtime.py --check` 只读，`--apply` 才重建；`INVENTORY.json` 自动生成勿手改。
4. `health_check.py` 只读诊断；真实板子下发须显式 `--act` 且人在场。
5. 改功能必补专项断言；老基线全绿不等于新功能已验。
6. 取不到数据显示未知 / 0，不造演示数据；人工目视项脚本不代签。
7. 每次改动在 `VERSION.md` 追加决策留痕；基准哈希变化记录前后值。

## 下一步
参照技能 `references/05-从零搭建操作手册.md` 的 Step 2–9 逐层实现。
若使用 `--from` 复制了参考实现，先完成终端打印的脱敏清单。
"""

VERSION_TEXT = """# 版本与勘误编年史

> 增量追加，旧文原文不回改；冲突时追加勘误小节并注明「原文不回改」。
> 现役真值只写在 `README.md` 的现役状态表，本文件的历史数值是当时中间值。

| 版本 | 日期 | 关键决策 / 变更 |
|---|---|---|
| W0 | {today} | 目录骨架建立，确定唯一真源与验证纪律 |
"""

BASELINE_TEXT = """# 验证基线口径（骨架）

- 基线 = 静态契约 + 端点/在线契约 + 对齐专项；项数由各套件实际输出累加，禁止硬编码。
- 每新增功能建 `verify_wXX.py` 专项，设 `bl=False` 独立判定，不混入老基线。
- 环境态（板端断电 / 断网 / CDP 未就绪 / 瞬时竞态）记 WARN；代码 / 配置 / 契约 / 清单失败记 FAIL。
- 人工目视与实板下发（`--act`）按设计未命中，脚本不得伪造 PASS。
- 体积护栏、SW 缓存名、`budget_revision`、`CANON_BASELINE` 变化须在 `VERSION.md` 留痕。
"""

DIR_NOTE = """本目录由脚手架创建。实现内容参见技能 `references/02-参考架构与接口契约.md`
与 `references/05-从零搭建操作手册.md`。运行时镜像内的路径不要在源码副本里批量替换。
"""

DESENSITIZE = [
    "network.json：lan / host / board_ip / board_mdns / ap_ssid / ap_url 全部换成目标环境值",
    "paths.json：mirror 路径、publish.entry_dir / app_id、线上站点 host 与 sharecode",
    "03-固件/wb_light/secrets.h：用 secrets.h.example 重建，不保留原 WiFi 密码",
    "lan_token / 访问码 / .genie 应用卡片：重新生成，令牌文件权限 0600",
    "门户兼容开关（如 k_fw 交换）：确认互斥决策，不恢复已撤销的开关",
    "INVENTORY.json / CANON_BASELINE / 验证项数 / 体积护栏：首次跑通后重算并留痕",
    "06-文档/ 与 07-归档/：默认不复制，避免把原项目史实与史料带进新项目",
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
    print("     No existing file was deleted.")
    print("\n[必做] 脱敏与替换清单：")
    for i, item in enumerate(DESENSITIZE, 1):
        print(f"  {i}. {item}")
    print("\n[下一步] 参照 references/05-从零搭建操作手册.md Step 2-9；")
    print("          实现或复制 sync_runtime.py / health_check.py 后，先跑只读体检，再 --apply 重建清单。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
