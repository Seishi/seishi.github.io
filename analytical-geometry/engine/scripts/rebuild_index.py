#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""扫描 problems/*/ 生成仓库根目录题目列表页 index.html。"""

from __future__ import annotations

import json
import re
import sys
from html import unescape
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
PROBLEMS = REPO / "problems"
TEMPLATE = Path(__file__).resolve().parent.parent / "template" / "index.html"

DIR_RE = re.compile(r"^(\d{8})-(\d{2})-(.+)$")
EX_RE = re.compile(r"^ex(\d+)(?:-|$)", re.I)
EXER_RE = re.compile(r"^exer(\d+)(?:-|$)", re.I)
TAG_RE = re.compile(r"<[^>]+>")
BR_RE = re.compile(r"<br\s*/?>", re.I)


def strip_html(text: str) -> str:
    text = BR_RE.sub(" ", text or "")
    return unescape(TAG_RE.sub("", text)).strip()


def _label(slug: str) -> str:
    m = EXER_RE.match(slug or "")
    if m:
        return f"习题 {int(m.group(1))}"
    m = EX_RE.match(slug or "")
    if m:
        return f"例题 {int(m.group(1))}"
    return "演示"


def collect() -> list[dict]:
    rows = []
    if not PROBLEMS.is_dir():
        return rows
    for d in PROBLEMS.iterdir():
        if not d.is_dir() or d.name.startswith("_") or d.name.startswith("."):
            continue
        m = DIR_RE.match(d.name)
        if not m:
            continue
        if not (d / "index.html").is_file():
            print(f"skip {d.name} 无 index.html", file=sys.stderr)
            continue
        day, seq, slug = m.group(1), m.group(2), m.group(3)
        meta = {}
        mp = d / "meta.json"
        if mp.is_file():
            try:
                meta = json.loads(mp.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                meta = {}
        slug = meta.get("slug") or slug
        title = meta.get("title")
        rows.append({
            "id": meta.get("id") or d.name,
            "href": f"problems/{d.name}/index.html",
            "slug": slug,
            "label": _label(slug),
            "tags": meta.get("tags") or [],
            "title": strip_html(title) if title else d.name,
            "created": meta.get("created") or "",
            "date": f"{day[0:4]}-{day[4:6]}-{day[6:8]}",
            "source": bool(meta.get("source_file")),
            "seq": int(seq),
            "day": day,
        })
    rows.sort(key=lambda r: (r["day"], r["seq"]))
    return rows


def write_index(out: Path | None = None) -> Path:
    rows = collect()
    out = out or (REPO / "index.html")
    html = TEMPLATE.read_text(encoding="utf-8").replace(
        "__PROBLEMS_JSON__", json.dumps(rows, ensure_ascii=False)
    )
    out.write_text(html, encoding="utf-8")
    return out


def main():
    out = write_index()
    print(f"PASS  已生成: {out}  ({len(collect())} 题)")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"FAIL  {e}", file=sys.stderr)
        sys.exit(1)
