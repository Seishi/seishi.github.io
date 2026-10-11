#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_DIR / "scripts"))
sys.path.insert(0, str(SKILL_DIR / "lib"))

import sympy as sp

failures = []


def check(ok, name, detail=""):
    print(("PASS  " if ok else "FAIL  ") + name + (f"   {detail}" if detail else ""))
    if not ok:
        failures.append(name)


def main():
    import geometry_kernel as gk

    p = gk.V2(3, 4)
    check(list(p) == [sp.Integer(3), sp.Integer(4)], "V2(3,4)")
    check(gk.tex(sp.Rational(1, 2)) == r"\dfrac{1}{2}", "tex 1/2 uses dfrac", gk.tex(sp.Rational(1, 2)))
    check(gk.tex_point(gk.V2(sp.sqrt(2), 1)) == r"\left(\sqrt{2}, 1\right)",
          "tex_point sqrt2", gk.tex_point(gk.V2(sp.sqrt(2), 1)))
    m = gk.midpoint(gk.V2(0, 0), gk.V2(2, 4))
    check(list(m) == [sp.Integer(1), sp.Integer(2)], "midpoint")
    d = gk.dist(gk.V2(0, 0), gk.V2(3, 4))
    check(sp.simplify(d - 5) == 0, "dist 3-4-5")

    import curves as cv

    E = cv.make_curve("C", {
        "type": "ellipse", "a": 2, "b": 1, "center": [0, 0], "axis": "x"
    }, {})
    eq = E.equation_latex()
    check(r"x^{2}" in eq and r"=1" in eq.replace(" ", "") and r"4" in eq,
          "ellipse equation", eq)
    check(sp.simplify(E.eccentricity() - sp.sqrt(3) / 2) == 0, "ellipse e")
    F = E.focus("right")
    check(sp.simplify(F[0] - sp.sqrt(3)) == 0 and F[1] == 0, "ellipse right focus", F)
    try:
        E.focus("upper")
        check(False, "ellipse x-axis focus upper errors")
    except ValueError:
        check(True, "ellipse x-axis focus upper errors")
    P = E.point_at(sp.pi / 3)
    check(sp.simplify(P[0] - 1) == 0 and sp.simplify(P[1] - sp.sqrt(3) / 2) == 0,
          "ellipse point_at pi/3", P)
    Ey = cv.make_curve("Cy", {
        "type": "ellipse", "a": 2, "b": 1, "center": [0, 0], "axis": "y"
    }, {})
    Fu = Ey.focus("upper")
    check(sp.simplify(Fu[0]) == 0 and sp.simplify(Fu[1] - sp.sqrt(3)) == 0,
          "ellipse y-axis focus upper", Fu)
    try:
        Ey.focus("right")
        check(False, "ellipse y-axis focus right errors")
    except ValueError:
        check(True, "ellipse y-axis focus right errors")
    circ = cv.make_curve("O", {"type": "circle", "center": [0, 0], "radius": 2}, {})
    Q = circ.point_at(0)
    check(sp.simplify(Q[0] - 2) == 0 and Q[1] == 0, "circle point_at 0")
    ln = cv.make_curve("l", {"type": "line", "a": 1, "b": -2, "c": 0}, {})
    abc = ln.abc()
    check(all(sp.simplify(abc[i] - v) == 0 for i, v in enumerate((1, -2, 0))),
          "line abc", abc)

    H = cv.make_curve("H", {
        "type": "hyperbola", "a": 2, "b": 1, "center": [0, 0], "transverse": "x"
    }, {})
    check(sp.simplify(H.eccentricity() - sp.sqrt(5) / 2) == 0, "hyperbola e")
    Pr = H.point_at(0, which="right")
    check(sp.simplify(Pr[0] - 2) == 0 and Pr[1] == 0, "hyperbola right t=0", Pr)
    Par = cv.make_curve("P", {
        "type": "parabola", "p": 2, "vertex": [0, 0], "axis": "x", "direction": "+"
    }, {})
    Fpar = Par.focus("right")
    check(sp.simplify(Fpar[0] - 1) == 0 and Fpar[1] == 0, "parabola focus p/2")
    Pt = Par.point_at(2)
    check(sp.simplify(Pt[0] - 1) == 0 and sp.simplify(Pt[1] - 2) == 0, "parabola point_at", Pt)
    Parab_e = Par.eccentricity()
    check(sp.simplify(Parab_e - 1) == 0, "parabola e=1")
    Param = cv.make_curve("R", {
        "type": "parametric", "x(t)": "2*cos(t)", "y(t)": "sin(t)", "tmin": 0, "tmax": "2*pi"
    }, {})
    Pp = Param.point_at(0)
    check(sp.simplify(Pp[0] - 2) == 0 and Pp[1] == 0, "parametric t=0")
    Polar = cv.make_curve("K", {
        "type": "polar", "r(theta)": "2", "tmin": 0, "tmax": "2*pi"
    }, {})
    Pk = Polar.point_at(0)
    check(sp.simplify(Pk[0] - 2) == 0 and Pk[1] == 0, "polar r=2")
    Imp = cv.make_curve("I", {"type": "implicit", "expr": "x**2 + y**2 - 1"}, {})
    check("x" in Imp.equation_latex(), "implicit eq")

    pts = {}
    E = cv.make_curve("C", {"type": "ellipse", "a": 2, "b": 1, "center": [0, 0], "axis": "x"}, pts)
    L = cv.make_curve("l", {"type": "line", "a": 1, "b": -2, "c": 0}, pts)
    hits = cv.intersect(E, L)
    check(len(hits) == 2, "line-ellipse 2 hits", hits)
    length = cv.chord_length(E, L)
    check(sp.simplify(length - sp.sqrt(10)) == 0, "chord length sqrt(10)", length)

    from solve import solve

    spec = {
        "language": "zh-CN",
        "tags": ["ellipse"],
        "frame": {"xmin": -6, "xmax": 6, "ymin": -4, "ymax": 4},
        "curves": {
            "C": {"type": "ellipse", "a": 2, "b": 1, "center": [0, 0], "axis": "x"},
            "l": {"type": "line", "a": 1, "b": -2, "c": 0},
        },
        "points": {},
        "givens": [
            {"name": "F", "kind": "focus", "of": "C", "which": "right"},
            {"name": "A", "kind": "intersection", "of": ["C", "l"], "which": "right"},
            {"name": "B", "kind": "intersection", "of": ["C", "l"], "which": "left"},
            {"name": "P", "kind": "on_curve", "curve": "C", "t": "pi/3"},
        ],
        "lengths": {"AB": ["A", "B"]},
        "query": {"type": "chord_length", "line": "l", "curve": "C"},
    }
    sol = solve(spec)
    check(sol["answer"] == r"\sqrt{10}" or "sqrt{10}" in sol["answer"].replace(" ", ""),
          "solve chord answer", sol["answer"])
    check("F" in sol["mp"] and "A" in sol["mp"] and "P" in sol["mp"], "mp keys")
    check("C" in sol["eq"], "eq.C")
    check("len" in sol["vals"] or "len_AB" in sol["vals"], "vals chord", sol["vals"].keys())
    check(abs(sol["math_points"]["P"][0] - 1) < 1e-9, "math_points P")

    dspec = {
        "tags": ["line-circle"],
        "curves": {"l": {"type": "line", "a": 3, "b": 4, "c": -6}},
        "points": {"P": [0, 0]},
        "query": {"type": "point_line_distance", "point": "P", "line": "l"},
    }
    dsol = solve(dspec)
    check("dfrac{6}{5}" in dsol["answer"].replace(" ", "") or dsol["answer"] in (r"\dfrac{6}{5}", "6/5"),
          "point-line dist 6/5", dsol["answer"])

    cspec = {
        "tags": ["ellipse"],
        "curves": {"C": {"type": "ellipse", "a": 2, "b": 1, "center": [0, 0], "axis": "x"}},
        "query": {"type": "eccentricity", "curve": "C"},
    }
    check("sqrt{3}" in solve(cspec)["answer"], "e=sqrt3/2", solve(cspec)["answer"])

    # 圆点线距已有 solve point_line_distance；抛物线 e=1 / 参数点 / 极坐标点 / implicit 方程已有 make_curve
    circ_e = {
        "tags": ["line-circle"],
        "curves": {"O": {"type": "circle", "center": [0, 0], "radius": 2}},
        "query": {"type": "eccentricity", "curve": "O"},
    }
    check(solve(circ_e)["answer"].replace(" ", "") in ("0", r"0"),
          "solve circle e=0", solve(circ_e)["answer"])

    hspec_e = {
        "tags": ["hyperbola"],
        "curves": {"H": {"type": "hyperbola", "a": 2, "b": 1, "center": [0, 0], "transverse": "x"}},
        "query": {"type": "eccentricity", "curve": "H"},
    }
    check("sqrt{5}" in solve(hspec_e)["answer"].replace(" ", ""),
          "solve hyperbola e", solve(hspec_e)["answer"])

    aspec = {
        "tags": ["line-circle"],
        "curves": {
            "h": {"type": "line", "a": 0, "b": 1, "c": 0},
            "v": {"type": "line", "a": 1, "b": 0, "c": 0},
        },
        "query": {"type": "line_line_angle", "line1": "h", "line2": "v", "output": "cos"},
    }
    acheck = solve(aspec)["answer"].replace(" ", "")
    check(acheck in ("0", r"0") or acheck.endswith("0"), "line_line_angle cos 0", solve(aspec)["answer"])

    tspec = {
        "tags": ["line-circle"],
        "points": {"A": [0, 0], "B": [2, 0], "C": [0, 2]},
        "query": {"type": "area_triangle", "pts": ["A", "B", "C"]},
    }
    check(solve(tspec)["answer"].replace(" ", "") in ("2", r"2"), "area 2", solve(tspec)["answer"])

    fspec = {
        "tags": ["ellipse"],
        "curves": {"C": {"type": "ellipse", "a": 2, "b": 1, "center": [0, 0], "axis": "x"}},
        "points": {"A": [2, 0]},
        "query": {"type": "focal_radius", "curve": "C", "point": "A", "which": "right"},
    }
    fr = solve(fspec)["answer"]
    check("sqrt{3}" in fr.replace(" ", "") or "sqrt{3}" in fr, "focal radius 2-sqrt3", fr)

    ispec = {
        "tags": ["ellipse"],
        "curves": {
            "C": {"type": "ellipse", "a": 2, "b": 1, "center": [0, 0], "axis": "x"},
            "l": {"type": "line", "a": 1, "b": -2, "c": 0},
        },
        "query": {"type": "intersection", "curve1": "C", "curve2": "l"},
    }
    isol = solve(ispec)
    check("pts" in isol["vals"] or ";" in isol["answer"], "intersection pts", isol)

    xspec = {"tags": ["ellipse"], "query": {"type": "custom", "expr": "sqrt(4)"}}
    check(solve(xspec)["answer"].replace(" ", "") in ("2", r"2"), "custom sqrt4", solve(xspec)["answer"])

    from validate import validate
    import json

    def base_data(**kw):
        d = {
            "lesson": {"meta": "t", "title": "椭圆 $C$", "answerLabel": "弦长", "answerValue": r"$\sqrt{10}$"},
            "steps": [{"title": "建系", "content": "<p>$C$</p>", "highlight": ["Axis"]}],
            "model": {
                "points": {"O": [0, 0]},
                "frame": {"xmin": -4, "xmax": 4, "ymin": -3, "ymax": 3},
                "elements": {"Axis": {"type": "axes"}},
                "plot_curves": {},
            },
            "spec_tags": ["ellipse"],
        }
        d.update(kw)
        return d

    errs = validate(base_data(steps=[{"title": "a", "content": "<p>$1$</p>", "highlight": []}]))
    check(any("highlight" in e for e in errs), "empty highlight FAIL", errs)

    errs = validate(base_data(steps=[{"title": "a", "content": "<p>$1$</p>", "highlight": ["Nope"]}]))
    check(any("Nope" in e for e in errs), "unknown highlight FAIL", errs)

    errs = validate(base_data())
    check(errs == [], "good data PASS", errs)

    errs = validate(base_data(steps=[{"title": "建系", "content": "<p>$C</p>", "highlight": ["Axis"]}]))
    check(any("$" in e for e in errs), "odd $ FAIL", errs)

    errs = validate(base_data(spec_tags=[]))
    check(any("tag" in e.lower() for e in errs), "empty tags FAIL", errs)

    fix_dir = SKILL_DIR / "fixtures"
    empty_hl = json.loads((fix_dir / "bad-empty-highlight.json").read_text(encoding="utf-8"))
    errs = validate(empty_hl)
    check(any("highlight" in e for e in errs), "fixture empty highlight FAIL", errs)

    leftover = json.loads((fix_dir / "bad-unknown-placeholder.json").read_text(encoding="utf-8"))
    errs = validate(leftover)
    check(any("未替换占位符" in e for e in errs), "fixture leftover placeholder FAIL", errs)

    lesson_f1 = {
        "meta": "t",
        "title": "函数 $f(1)$ 的值",
        "answerLabel": "弦长",
        "answerValue": r"$\sqrt{10}$",
    }
    errs = validate(base_data(lesson=lesson_f1))
    check(not any("answers" in e for e in errs) and errs == [], "f(1) title not multipart", errs)

    errs = validate(base_data(steps=[{"title": "a", "content": "<p>$1$</p>", "highlight": "Axis"}]))
    check(any("highlight" in e for e in errs), "highlight string FAIL", errs)

    d = base_data()
    d["model"]["elements"]["Loc"] = {"type": "locus", "point": "Z", "mover": "O"}
    d["steps"][0]["highlight"] = ["Axis", "Loc"]
    errs = validate(d)
    check(any("Z" in e for e in errs), "locus bad point FAIL", errs)

    d = base_data()
    d["lesson"]["answerValue"] = r"$\sqrt{10}"
    errs = validate(d)
    check(any("$" in e for e in errs), "odd $ answerValue FAIL", errs)

    d = base_data()
    d["model"]["elements"]["E"] = {"type": "ellipse"}
    d["steps"][0]["highlight"] = ["Axis", "E"]
    errs = validate(d)
    check(any("ellipse" in e for e in errs), "empty ellipse FAIL", errs)

    from build import substitute, fill_defaults, build
    import tempfile, json

    ctx = {"answer": r"\sqrt{10}", "mp": {"A": r"\left(\sqrt{2}, \dfrac{1}{2}\right)"},
           "vals": {"len": r"\sqrt{10}"}, "eq": {"C": r"\dfrac{x^{2}}{4}+y^{2}=1"}}
    s = substitute("弦长 ${{vals.len}}$ 点 $A{{mp.A}}$", ctx)
    check(r"\sqrt{10}" in s and "mp.A" not in s, "substitute", s)
    try:
        substitute("{{vals.nope}}", ctx)
        check(False, "unknown placeholder should raise")
    except KeyError:
        check(True, "unknown placeholder raises")

    lesson = {
        "lesson": {"meta": "交互解题 · 椭圆弦长", "title": "椭圆 ${{eq.C}}$ 被直线所截弦长",
                   "answerLabel": "弦长"},
        "steps": [{"title": "建系", "content": "<p>方程 ${{eq.C}}$</p>", "highlight": ["Axis"]}],
        "model": {"elements": {"Axis": {"type": "axes"}}},
    }
    filled = fill_defaults(substitute(lesson, ctx), {
        "math_points": {"A": [1.41, 0.5]},
        "plot_curves": {"C": {"type": "ellipse", "cx": 0, "cy": 0, "rx": 2, "ry": 1}},
        "frame": {"xmin": -6, "xmax": 6, "ymin": -4, "ymax": 4},
        "answer": r"\sqrt{10}",
    }, {"language": "zh-CN", "tags": ["ellipse"]})
    check(filled["model"]["points"]["A"][0] > 1, "fill points")
    check(filled["lesson"].get("answerValue") == r"$\sqrt{10}$", "answerValue wrapped")

    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "out.html"
        doc_spec = {**spec}  # Task 6 那个 ellipse chord spec
        lesson_min = {
            "lesson": {"meta": "m", "title": "求弦长", "answerLabel": "弦长"},
            "steps": [{"title": "代入", "content": "<p>弦长为 ${{answer}}$</p>",
                       "highlight": ["Axis"]}],
            "model": {"elements": {"Axis": {"type": "axes"}}},
        }
        build(doc_spec, lesson_min, out)
        html = out.read_text()
        check("__LESSON_DATA__" not in html, "placeholder replaced")
        check("sqrt{10}" in html.replace(" ", ""), "html has answer")
        check("jsxgraphcore.js" in html, "html has jsxgraph")

        drag_out = Path(td) / "drag.html"
        drag_lesson = {
            "lesson": {"meta": "m", "title": "求弦长", "answerLabel": "弦长"},
            "steps": [{"title": "代入", "content": "<p>弦长为 ${{answer}}$</p>",
                       "highlight": ["Axis", "Point_P"]}],
            "model": {
                "elements": {
                    "Axis": {"type": "axes"},
                    "Point_P": {"type": "point", "center": "P"},
                },
                "draggable": {
                    "point": "P",
                    "on": "C",
                    "t": "pi/3",
                    "standardLabel": "标准位 t=π/3",
                    "readouts": [{"label": "弦长 AB", "type": "length", "pts": ["A", "B"]}],
                },
            },
        }
        build(doc_spec, drag_lesson, drag_out)
        drag_html = drag_out.read_text()
        check("draggable" in drag_html, "html has draggable")
        check("readouts" in drag_html, "html has readouts")

    chord_doc = json.loads((fix_dir / "pass-ellipse-chord.json").read_text(encoding="utf-8"))
    chord_spec = chord_doc["spec"]
    chord_lesson = {k: v for k, v in chord_doc.items() if k != "spec"}
    with tempfile.TemporaryDirectory() as td:
        chord_out = Path(td) / "ellipse-chord.html"
        build(chord_spec, chord_lesson, chord_out)
        print(f"PASS  fixture tempfile: {chord_out}")
        chord_html = chord_out.read_text(encoding="utf-8")
        check("sqrt{10}" in chord_html.replace(" ", ""), "fixture tempfile has sqrt{10}")
        check("jxgbox" in chord_html, "fixture tempfile jxgbox")
        check("draggable" in chord_html, "fixture tempfile draggable")

    from new_problem import slugify
    check(slugify("ex2-ellipse-chord") == "ex2-ellipse-chord", "slug ok")
    try:
        slugify("椭圆弦长")
        check(False, "zh slug should exit")
    except SystemExit:
        check(True, "zh slug rejected")

    from rebuild_index import collect, write_index
    rows = collect()
    check(isinstance(rows, list), "collect list")
    write_index()
    repo = Path(__file__).resolve().parent.parent.parent
    root = (repo / "index.html").read_text()
    check("__PROBLEMS_JSON__" not in root, "index placeholder filled")
    check("解析几何" in root, "index title")
    check("ellipse-chord" in root, "root index lists ellipse-chord")
    check("sqrt{10}" not in root.replace(" ", ""), "root index hides answers")
    check(all("answer" not in r for r in rows), "collect omits answer")

    # JSXGraph 1.10 createCurve prepends "x" to parents. Passing `board` as a
    # parent makes minX = createFunction(board) = null, then null.deps throws.
    tpl = (SKILL_DIR / "template" / "lesson.html").read_text(encoding="utf-8")
    import re
    check(re.search(r"create\('curve'[\s\S]{0,500}?,\s*board\s*,", tpl) is None,
          "curve parents omit board")
    check(tpl.find('id="board-wrap"') < tpl.find('id="sidebar"'),
          "board is left of steps")
    check("keepaspectratio: true" in tpl, "board keeps equal x/y units")
    check("function fitBB" in tpl, "fitBB expands viewport instead of cropping")
    check("Math.max((xmax - xmin) / w, (ymax - ymin) / h)" in tpl,
          "fitBB uses max unit so the frame is never cropped")
    check(re.search(r"setBoundingBox\([^)]*,\s*false\s*\)", tpl) is None,
          "setBoundingBox keeps aspect ratio")
    check("el.color === 'aux'" in tpl and "el.type === 'segment'" in tpl,
          "non-original lines default to dashed")
    check("needShift: false" in tpl, "pan does not require Shift")
    check("min: 0.25" in tpl and "max: 8" in tpl, "zoom has min and max")
    check("factorX: 1.1" in tpl, "zoom factor is moderate")
    check("const STEP = 96" in tpl, "wheel zoom is quantized")
    check("function hyperbolaSpan" in tpl and "function parabolaSpan" in tpl,
          "conic parameter range follows the viewport")

    demo_dirs = [p for p in (repo / "problems").glob("*-ellipse-chord") if p.is_dir()]
    check(len(demo_dirs) >= 1, "problems/*/ellipse-chord exists", demo_dirs)
    demo_html = (demo_dirs[0] / "index.html").read_text(encoding="utf-8") if demo_dirs else ""
    check("jxgbox" in demo_html, "demo index jxgbox")
    check("sqrt{10}" in demo_html.replace(" ", ""), "demo index sqrt{10}")
    check("draggable" in demo_html, "demo index draggable")
    check("keepaspectratio: true" in demo_html, "demo keeps equal x/y units")
    check("function fitBB" in demo_html, "demo fitBB present")

    if failures:
        print(f"\n{len(failures)} failed")
        sys.exit(1)
    print("\nall passed")


if __name__ == "__main__":
    main()
