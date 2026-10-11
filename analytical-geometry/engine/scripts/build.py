#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build.py — spec 求解 -> 占位符替换 -> 补默认值 -> 注入模板 -> 静态自检。

    python3 scripts/build.py spec.json lesson.json out.html
"""

import json
import re
import sys
from html import unescape
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(SKILL_DIR / "lib"))

from solve import solve  # noqa: E402
from validate import validate  # noqa: E402
import geometry_kernel as gk  # noqa: E402

PLACEHOLDER_RE = re.compile(r"\{\{([a-zA-Z0-9_.]+)\}\}")
TEMPLATE = SKILL_DIR / "template" / "lesson.html"
LESSON_PLACEHOLDER = "__LESSON_DATA__"


def lookup(ctx, dotted):
    cur = ctx
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            avail = sorted(cur) if isinstance(cur, dict) else "(非字典)"
            raise KeyError(f"占位符 {{{{{dotted}}}}} 里的 {part!r} 不存在。该层可用键：{avail}")
        cur = cur[part]
    return cur


def substitute(node, ctx):
    """递归替换占位符。整串就是一个占位符时，直接换成原始对象（可为 dict/list）。"""
    if isinstance(node, str):
        whole = PLACEHOLDER_RE.fullmatch(node.strip())
        if whole:
            return lookup(ctx, whole.group(1))
        return PLACEHOLDER_RE.sub(lambda m: str(lookup(ctx, m.group(1))), node)
    if isinstance(node, list):
        return [substitute(x, ctx) for x in node]
    if isinstance(node, dict):
        return {k: substitute(v, ctx) for k, v in node.items()}
    return node


def fill_defaults(data, sol, spec):
    """把能自动推出来的东西补上，模型就不必手写这些字段。"""
    model = data.setdefault("model", {})
    model.setdefault("points", sol["math_points"])
    model.setdefault("plot_curves", sol["plot_curves"])
    model.setdefault("frame", sol["frame"])
    if model.get("draggable"):
        model.setdefault("mathPoints", sol["math_points"])
        dr = model["draggable"]
        dr.setdefault("t0", dr.get("t"))
    lesson = data.setdefault("lesson", {})
    lesson.setdefault("language", spec.get("language", "zh-CN"))
    if spec.get("language") == "en":
        ui_path = SKILL_DIR / "template" / "ui-en.json"
        if ui_path.exists():
            lesson.setdefault("ui", json.loads(ui_path.read_text(encoding="utf-8")))
    if not lesson.get("answers"):
        lesson.setdefault("answerValue", f"${sol['answer']}$")
    return data


def render_html(data, out_path):
    html = TEMPLATE.read_text(encoding="utf-8").replace(
        LESSON_PLACEHOLDER, json.dumps(data, ensure_ascii=False)
    )
    out_path.write_text(html, encoding="utf-8")


_TAG_RE = re.compile(r"<[^>]+>")
_BR_RE = re.compile(r"<br\s*/?>", re.I)


def _strip_html(text: str) -> str:
    text = _BR_RE.sub(" ", text or "")
    return unescape(_TAG_RE.sub("", text)).strip()


def _answer_text(lesson: dict) -> str:
    items = lesson.get("answers")
    if isinstance(items, list) and items:
        vals = []
        for a in items:
            if isinstance(a, dict) and a.get("value"):
                vals.append(str(a["value"]).strip())
        if vals:
            return "；".join(vals)
    av = lesson.get("answerValue")
    if av:
        return str(av).strip()
    return ""


def _sync_meta(out_path: Path, spec: dict, data: dict) -> None:
    problems = (SKILL_DIR.parent / "problems").resolve()
    try:
        rel = out_path.resolve().relative_to(problems)
    except ValueError:
        return
    dest = problems / rel.parts[0]
    meta_path = dest / "meta.json"
    if not dest.is_dir() or not meta_path.is_file():
        return
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    lesson = data.get("lesson") or {}
    meta["tags"] = spec.get("tags") or []
    meta["title"] = _strip_html(lesson.get("title") or "")
    meta["answer"] = _answer_text(lesson)
    meta_path.write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build(spec: dict, lesson_data: dict, out_path: Path) -> Path:
    sol = solve(spec)
    ctx = {
        "answer": sol["answer"],
        "mp": sol["mp"],
        "vals": sol["vals"],
        "eq": sol["eq"],
    }
    data = fill_defaults(substitute(lesson_data, ctx), sol, spec)
    data = gk.dfrac_tree(data)
    errs = validate(data, tags=spec.get("tags"))
    if errs:
        print(f"FAIL ({len(errs)} 个问题)，未写出文件:", file=sys.stderr)
        for e in errs:
            print("  -", e, file=sys.stderr)
        sys.exit(1)

    render_html(data, out_path)
    print(f"PASS  已生成: {out_path}")
    _sync_meta(out_path, spec, data)
    try:
        from rebuild_index import write_index
        write_index()
    except ImportError:
        pass
    return out_path


def main():
    args = sys.argv[1:]
    if len(args) == 2:
        doc = json.loads(Path(args[0]).read_text(encoding="utf-8"))
        if "spec" not in doc:
            sys.exit(f"{args[0]} 缺少顶层 \"spec\" 字段（单文件形式要求 spec 与 lesson/steps/model 同级）")
        spec = doc.pop("spec")
        lesson_data, out = doc, Path(args[1])
    elif len(args) == 3:
        spec = json.loads(Path(args[0]).read_text(encoding="utf-8"))
        lesson_data, out = json.loads(Path(args[1]).read_text(encoding="utf-8")), Path(args[2])
    else:
        sys.exit("用法: python3 scripts/build.py problem.json out.html\n"
                 "  或: python3 scripts/build.py spec.json lesson.json out.html")
    out = out.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    build(spec, lesson_data, out)


if __name__ == "__main__":
    main()
