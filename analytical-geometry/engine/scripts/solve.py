#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_DIR / "lib"))

try:
    import sympy as sp
except ImportError:
    sys.exit("缺少 sympy。请先征得用户同意再安装：python3 -m pip install sympy")

import geometry_kernel as gk
import curves as cv

QUERY_TYPES = (
    "point_line_distance",
    "line_line_angle",
    "chord_length",
    "eccentricity",
    "focal_radius",
    "area_triangle",
    "intersection",
    "custom",
)


def foot_of_perp(P, a, b, c):
    d = a ** 2 + b ** 2
    x = (b * (b * P[0] - a * P[1]) - a * c) / d
    y = (a * (-b * P[0] + a * P[1]) - b * c) / d
    return gk.V2(sp.simplify(x), sp.simplify(y))


def line_abc(line, curves, points):
    if isinstance(line, str):
        return curves[line].abc()
    if isinstance(line, (list, tuple)) and len(line) == 2:
        return gk.line_abc_from_points(points[line[0]], points[line[1]])
    raise TypeError(f"无法解析直线 {line!r}")


def line_dir(abc):
    a, b, _c = abc
    return gk.V2(b, -a)


def as_line_curve(line, curves, points):
    if isinstance(line, str):
        return curves[line]
    a, b, c = line_abc(line, curves, points)
    return cv.make_curve("_line", {"type": "line", "a": a, "b": b, "c": c}, points)


def make_curves(spec, points):
    return {k: cv.make_curve(k, cs, points) for k, cs in spec.get("curves", {}).items()}


def apply_given(g, points, curves):
    kind, name = g["kind"], g["name"]
    if kind == "point":
        points[name] = gk.parse_xy(g["at"])
    elif kind == "midpoint":
        a, b = g["of"]
        points[name] = gk.midpoint(points[a], points[b])
    elif kind == "ratio":
        a, b = g["of"]
        t = sp.sympify(g["t"])
        points[name] = sp.simplify(points[a] + t * (points[b] - points[a]))
    elif kind == "on_line":
        t = sp.sympify(g["t"])
        line = g["line"]
        if isinstance(line, (list, tuple)) and len(line) == 2 and line[0] in points:
            A, B = points[line[0]], points[line[1]]
            points[name] = sp.simplify(A + t * (B - A))
        else:
            points[name] = as_line_curve(line, curves, points).point_at(t)
    elif kind == "focus":
        points[name] = curves[g["of"]].focus(g.get("which", "right"))
    elif kind == "vertex":
        points[name] = curves[g["of"]].vertex(g.get("which"))
    elif kind == "on_curve":
        points[name] = curves[g["curve"]].point_at(sp.sympify(g["t"]), which=g.get("which"))
    elif kind == "foot":
        a, b, c = line_abc(g["line"], curves, points)
        points[name] = foot_of_perp(points[g["point"]], a, b, c)
    elif kind == "intersection":
        k1, k2 = g["of"]
        hits = cv.intersect(curves[k1], curves[k2])
        points[name] = cv.pick_intersection(hits, g.get("which"))
    else:
        raise ValueError(f"未知 given.kind {kind!r}")


def build_scene(spec):
    points = {k: gk.parse_xy(v) for k, v in spec.get("points", {}).items()}
    curves = make_curves(spec, points)
    for g in spec.get("givens", []):
        apply_given(g, points, curves)
        curves = make_curves(spec, points)
    return points, curves


def as_tex(v):
    if isinstance(v, str):
        return v
    if isinstance(v, sp.Matrix):
        return gk.tex_point(v)
    return gk.tex(v)


def run_query(query, curves, points):
    qtype = query["type"]
    if qtype not in QUERY_TYPES:
        raise ValueError(f"未知 query.type {qtype!r}，可选 {list(QUERY_TYPES)}")

    if qtype == "chord_length":
        length = cv.chord_length(curves[query["curve"]], as_line_curve(query["line"], curves, points))
        return length, {"len": length}

    if qtype == "point_line_distance":
        a, b, c = line_abc(query["line"], curves, points)
        dist = gk.point_line_distance(points[query["point"]], a, b, c)
        return dist, {"a": a, "b": b, "c": c, "dist": dist}

    if qtype == "eccentricity":
        curve = curves[query["curve"]]
        e = curve.eccentricity()
        vals = {"e": e}
        cs = curve.spec
        if "a" in cs:
            vals["a"] = sp.sympify(cs["a"])
        if "b" in cs:
            vals["b"] = sp.sympify(cs["b"])
        if "a" in cs and "b" in cs:
            a, b = vals["a"], vals["b"]
            if curve.type == "hyperbola":
                vals["c"] = sp.simplify(sp.sqrt(a ** 2 + b ** 2))
            else:
                vals["c"] = sp.simplify(sp.sqrt(sp.Abs(a ** 2 - b ** 2)))
        return e, vals

    if qtype == "line_line_angle":
        d1 = line_dir(line_abc(query["line1"], curves, points))
        d2 = line_dir(line_abc(query["line2"], curves, points))
        dot = d1.dot(d2)
        cosv = sp.simplify(sp.Abs(dot) / (d1.norm() * d2.norm()))
        sinv = sp.simplify(sp.sqrt(1 - cosv ** 2))
        vals = {"d1": d1, "d2": d2, "dot": dot, "cos": cosv, "sin": sinv}
        output = query.get("output", "cos")
        if output == "cos":
            return cosv, vals
        if output == "sin":
            return sinv, vals
        if output == "tan":
            tanv = sp.simplify(sinv / cosv)
            vals["tan"] = tanv
            return tanv, vals
        if output == "degree":
            ang = sp.simplify(sp.deg(sp.acos(cosv)))
            vals["degree"] = ang
            return ang, vals
        raise ValueError(f"line_line_angle.output={output!r}")

    if qtype == "area_triangle":
        n = query["pts"]
        S = gk.area_triangle(points[n[0]], points[n[1]], points[n[2]])
        return S, {"S": S}

    if qtype == "focal_radius":
        curve = curves[query["curve"]]
        F = curve.focus(query.get("which", "right"))
        r = gk.dist(points[query["point"]], F)
        return r, {"r": r}

    if qtype == "intersection":
        hits = cv.intersect(curves[query["curve1"]], curves[query["curve2"]])
        pts = "; ".join(gk.tex_point(p) for p in hits)
        return pts, {"pts": pts}

    if qtype == "custom":
        vals = {}
        if "vals" in query:
            vals = {k: sp.simplify(sp.sympify(v)) for k, v in query["vals"].items()}
        if "expr" in query:
            return sp.simplify(sp.sympify(query["expr"])), vals
        if vals:
            return next(iter(vals.values())), vals
        return "", vals

    raise ValueError(f"未知 query.type {qtype!r}，可选 {list(QUERY_TYPES)}")


def solve(spec):
    points, curves = build_scene(spec)
    query = spec.get("query")
    if query:
        answer_expr, qvals = run_query(query, curves, points)
    else:
        answer_expr, qvals = "", {}

    mp = {name: gk.tex_point(P) for name, P in points.items()}
    eq = {}
    for k, c in curves.items():
        try:
            eq[k] = c.equation_latex()
        except NotImplementedError:
            pass
    vals = {k: as_tex(v) for k, v in qvals.items()}
    for name, pair in spec.get("lengths", {}).items():
        vals[f"len_{name}"] = gk.tex(gk.dist(points[pair[0]], points[pair[1]]))
    for name, pair in spec.get("vectors", {}).items():
        vals[f"vec_{name}"] = gk.tex_point(points[pair[1]] - points[pair[0]])

    if isinstance(answer_expr, str):
        answer = answer_expr
    else:
        answer = gk.tex(answer_expr)

    math_points = {
        name: [gk.unitless_float(P[0]), gk.unitless_float(P[1])]
        for name, P in points.items()
    }
    plot_curves = {k: c.plot_recipe() for k, c in curves.items()}
    fr = spec.get("frame") or {}
    frame = {
        "xmin": float(fr.get("xmin", -8)),
        "xmax": float(fr.get("xmax", 8)),
        "ymin": float(fr.get("ymin", -5)),
        "ymax": float(fr.get("ymax", 5)),
    }
    return {
        "answer": answer,
        "mp": mp,
        "eq": eq,
        "vals": vals,
        "math_points": math_points,
        "plot_curves": plot_curves,
        "frame": frame,
    }


def main():
    raw = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    spec = raw["spec"] if isinstance(raw, dict) and "spec" in raw else raw
    sol = solve(spec)
    print(json.dumps({k: sol[k] for k in ("answer", "mp", "eq", "vals")},
                     ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
