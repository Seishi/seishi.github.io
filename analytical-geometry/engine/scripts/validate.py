#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validate.py — 写出 HTML 前对 lesson data 做静态自检。"""

import json
import re
import sys
from pathlib import Path

ALLOWED_TAGS = ("line-circle", "ellipse", "hyperbola", "parabola", "parametric-polar")

ALLOWED_ELEMENT_TYPES = (
    "point", "line", "segment", "circle", "ellipse", "hyperbola", "parabola",
    "implicit", "polar", "parametric", "axes", "focus", "directrix", "arrow",
    "measure", "locus",
)

CURVE_TYPES = (
    "circle", "ellipse", "hyperbola", "parabola", "implicit", "polar", "parametric",
)

POINT_REF_FIELDS = ("a", "b", "center", "origin", "point", "mover")

CURVE_INLINE_FIELDS = {
    "circle": (("radius",),),
    "ellipse": (("a", "b"),),
    "hyperbola": (("a", "b"),),
    "parabola": (("p",),),
    "implicit": (("expr",),),
    "polar": (("r(theta)",), ("r",)),
    "parametric": (("x(t)", "y(t)"), ("x", "y")),
}

LATEX_CMD = re.compile(r"\\[a-zA-Z]+")
FRAC_RE = re.compile(r"\\t?frac(?![a-zA-Z])")


def validate(data, *, tags=None, answer=None) -> list:
    """返回问题列表，空列表表示通过。"""
    errs = []
    if tags is None:
        tags = data.get("spec_tags")

    lesson = data.get("lesson")
    if not lesson:
        errs.append("缺少 lesson")
        lesson = {}
    steps = data.get("steps")
    if "steps" not in data:
        errs.append("缺少 steps")
        steps = []
    elif not steps:
        errs.append("steps 为空")
        steps = []
    model = data.get("model")
    if not model:
        errs.append("缺少 model")
        model = {}

    points = model.get("points") or {}
    elements = model.get("elements") or {}
    plot_curves = model.get("plot_curves") or {}

    if not tags:
        errs.append("tags 为空或不在 ALLOWED_TAGS")
    else:
        for t in tags:
            if t not in ALLOWED_TAGS:
                errs.append(f"tag {t!r} 不在 ALLOWED_TAGS {ALLOWED_TAGS}")

    for i, st in enumerate(steps):
        if not isinstance(st, dict):
            errs.append(f"steps[{i}] 不是对象")
            continue
        for field in ("title", "content", "highlight"):
            if field not in st:
                errs.append(f"steps[{i}] 缺少 {field}")
        hl = st.get("highlight")
        if "highlight" in st:
            if not isinstance(hl, list):
                errs.append(f"steps[{i}].highlight 必须是数组，不能是 {type(hl).__name__}")
            elif not hl:
                errs.append(f"steps[{i}].highlight 为空")
            else:
                for key in hl:
                    if key not in elements:
                        errs.append(
                            f"steps[{i}].highlight 的 {key!r} 不存在"
                            f"（可用：{sorted(elements)}）"
                        )
        for field in ("title", "content"):
            text = st.get(field) or ""
            if isinstance(text, str) and text.count("$") % 2:
                errs.append(f"steps[{i}].{field} 里 $ 数量为奇数，公式定界符没配对")

    title = lesson.get("title") or ""
    if isinstance(title, str) and title.count("$") % 2:
        errs.append("lesson.title 里 $ 数量为奇数，公式定界符没配对")

    check_latex(title, "lesson.title", errs)
    check_latex(lesson.get("answerLabel"), "lesson.answerLabel", errs)
    av = lesson.get("answerValue") or ""
    if av:
        check_latex(av, "lesson.answerValue", errs)
    for i, st in enumerate(steps):
        if not isinstance(st, dict):
            continue
        check_latex(st.get("title"), f"steps[{i}].title", errs)
        check_latex(st.get("content"), f"steps[{i}].content", errs)

    answers = lesson.get("answers")
    if answers is not None:
        if not isinstance(answers, list) or not answers:
            errs.append("lesson.answers 必须是非空数组")
        else:
            for i, a in enumerate(answers):
                if not isinstance(a, dict) or not a.get("label") or not a.get("value"):
                    errs.append(f"lesson.answers[{i}] 需要同时有非空的 label 和 value")
                else:
                    check_latex(a["label"], f"lesson.answers[{i}].label", errs)
                    check_latex(a["value"], f"lesson.answers[{i}].value", errs)
        plain = re.sub(r"<[^>]+>", "", av)
        if len(plain) > 40:
            errs.append(
                f"lesson.answerValue 过长（{len(plain)} 字）且同时存在 answers，答案卡会被撑变形"
            )

    multipart = bool(
        re.search(r"[(（]\s*1\s*[)）]", title)
        and re.search(r"[(（]\s*2\s*[)）]", title)
    )
    if multipart and not answers:
        errs.append(
            "题面含 (1)/(2) 等小问编号，但没有 lesson.answers。"
            '请改用 lesson.answers 逐问列出'
        )

    blob = json.dumps(data, ensure_ascii=False)
    if "{{" in blob:
        errs.append("未替换占位符")
    if FRAC_RE.search(blob):
        errs.append(r"禁止使用 \frac 或 \tfrac（含 measure.label），请改用 \dfrac")

    for key, el in elements.items():
        if not isinstance(el, dict):
            errs.append(f"elements[{key!r}] 不是对象")
            continue
        etype = el.get("type")
        if etype not in ALLOWED_ELEMENT_TYPES:
            errs.append(
                f"elements[{key!r}].type={etype!r} 不是合法类型："
                f"{ALLOWED_ELEMENT_TYPES}"
            )
            continue
        _check_required_fields(key, el, etype, errs)
        for field in POINT_REF_FIELDS:
            ref = el.get(field)
            if isinstance(ref, str) and ref not in points:
                errs.append(
                    f"elements[{key!r}].{field} 引用了不存在的点 {ref!r}"
                    f"（已有：{sorted(points)}）"
                )

    dg = model.get("draggable")
    if dg:
        pt = dg.get("point")
        if pt not in points:
            errs.append(f"draggable.point {pt!r} 不在 model.points")
        on = dg.get("on")
        on_curve = isinstance(on, str) and on in plot_curves
        on_seg = (
            isinstance(on, (list, tuple))
            and len(on) == 2
            and all(isinstance(x, str) and x in points for x in on)
        )
        if not on_curve and not on_seg:
            errs.append(
                "draggable.on 既不是 plot_curves 的 key，也不是长度为 2 的点名列表"
            )

    if answer:
        shown = av + "".join(
            str(a.get("value", "")) for a in (answers or []) if isinstance(a, dict)
        )
        if answer not in shown:
            errs.append(f"答案卡未出现 kernel 答案 {answer!r}（答案卡内容：{shown!r}）")
        if steps and answer not in ((steps[-1] or {}).get("content") or ""):
            errs.append(f"末步骤 content 未出现 kernel 答案 {answer!r}")

    return errs


def _check_required_fields(key, el, etype, errs):
    def missing(*fields):
        for field in fields:
            if field not in el:
                errs.append(f"elements[{key!r}] 缺少 {etype} 必需的字段 {field!r}")

    if etype == "point":
        missing("center")
    elif etype == "line":
        has_ab = "a" in el and "b" in el
        has_curve = "curve" in el
        if not has_ab and not has_curve:
            errs.append(f"elements[{key!r}] 是 line，需要 (a 和 b) 或 curve")
    elif etype == "segment":
        missing("a", "b")
    elif etype == "measure":
        missing("a", "b", "label")
    elif etype == "arrow":
        missing("origin", "dir", "length")
    elif etype in ("focus", "directrix"):
        missing("of", "which")
    elif etype == "locus":
        missing("point", "mover")
    elif etype == "axes":
        pass
    elif etype in CURVE_TYPES:
        if "curve" in el:
            return
        alts = CURVE_INLINE_FIELDS.get(etype, ())
        if not any(all(f in el for f in group) for group in alts):
            need = " 或 ".join("(" + ", ".join(g) + ")" for g in alts)
            errs.append(f"elements[{key!r}] 是 {etype}，需要 curve 或内联字段 {need}")


def _outside_math(text):
    """剥掉 $$…$$ 与 $…$，剩下的就是 MathJax 不会处理的部分。"""
    t = re.sub(r"\$\$.*?\$\$", " ", text, flags=re.S)
    return re.sub(r"\$[^$]*\$", " ", t)


def check_latex(text, where, errs):
    """LaTeX 必须被 $…$ 包住，否则页面上会原样显示源码。"""
    if not isinstance(text, str) or not text:
        return
    if text.count("$") % 2:
        errs.append(f"{where} 里 $ 数量为奇数，公式定界符没配对")
        return
    bare = sorted(set(LATEX_CMD.findall(_outside_math(text))))
    if bare:
        errs.append(
            f"{where} 有没被 $…$ 包住的 LaTeX 命令 {bare[:4]}，会原样显示成源码"
        )


def extract(html: str) -> dict:
    m = re.search(
        r'<script id="lesson-data" type="application/json">(.*?)</script>',
        html, re.S,
    )
    if not m:
        raise ValueError("HTML 里找不到 lesson-data 数据岛")
    return json.loads(m.group(1))


def main():
    if len(sys.argv) < 2:
        sys.exit("用法: python3 scripts/validate.py <成品.html>")
    path = Path(sys.argv[1])
    data = extract(path.read_text(encoding="utf-8"))
    errs = validate(data)
    if errs:
        print(f"FAIL ({len(errs)} 个问题):")
        for e in errs:
            print("  -", e)
        sys.exit(1)
    print(f"PASS  {path}  ({len(data.get('steps') or [])} 步)")


if __name__ == "__main__":
    main()
