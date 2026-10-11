#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Allocate a per-problem directory: problems/YYYYMMDD-NN-slug/"""

import argparse
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
PROBLEMS = REPO / "problems"
# 目录名只用 ASCII：例题N → exN，习题N → exerN，其余非 ASCII 直接拒绝
ZH_PREFIX = (("例题", "ex"), ("习题", "exer"), ("练习", "prac"))
SLUG_RE = re.compile(r"[^0-9A-Za-z\-]+")


def slugify(raw: str) -> str:
    s = raw.strip()
    for zh, en in ZH_PREFIX:
        s = s.replace(zh, en)
    if re.search(r"[^\x00-\x7F]", s):
        raise SystemExit("目录名请用英文 slug，如 ex2-ellipse-chord、exer3-hyperbola")
    s = SLUG_RE.sub("-", s).strip("-")
    s = re.sub(r"-{2,}", "-", s).lower()
    if not s:
        raise SystemExit("slug 不能为空，书上的题用 ex2-ellipse-chord，自拟题用 ellipse-chord")
    return s[:64]


def next_id(day: str, slug: str) -> str:
    PROBLEMS.mkdir(parents=True, exist_ok=True)
    seq = 1
    for p in PROBLEMS.iterdir():
        if p.is_dir() and p.name.startswith(f"{day}-"):
            try:
                seq = max(seq, int(p.name.split("-")[1]) + 1)
            except (IndexError, ValueError):
                continue
    return f"{day}-{seq:02d}-{slug}"


def main():
    ap = argparse.ArgumentParser(description="新建一道题的目录")
    ap.add_argument("slug", help="如 ex2-ellipse-chord 或 ellipse-chord")
    ap.add_argument("--source", help="题目原图路径，会复制为 source.<ext>")
    ap.add_argument("--type", choices=("text", "image"),
                    help="来源类型；有 --source 时默认 image")
    args = ap.parse_args()

    slug = slugify(args.slug)
    now = datetime.now().astimezone()
    pid = next_id(now.strftime("%Y%m%d"), slug)
    dest = PROBLEMS / pid
    dest.mkdir(parents=True)

    source_file = None
    source_type = args.type or ("image" if args.source else "text")
    if args.source:
        src = Path(args.source).expanduser().resolve()
        if not src.is_file():
            dest.rmdir()
            sys.exit(f"找不到原图: {src}")
        source_file = f"source{src.suffix.lower() or '.bin'}"
        shutil.copy2(src, dest / source_file)
        source_type = args.type or "image"

    meta = {
        "id": pid,
        "slug": slug,
        "created": now.isoformat(timespec="seconds"),
        "source_type": source_type,
        "source_file": source_file,
        "tags": [],
        "title": None,
        "answer": None,
    }
    (dest / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(dest)


if __name__ == "__main__":
    main()
