#!/usr/bin/env python3
"""Shared helpers for escape-hatch lesson renders."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "engine" / "lib"), str(ROOT / "engine" / "scripts")]

import sympy as sp  # noqa: E402
import geometry_kernel as gk  # noqa: E402
from generate import render_html  # noqa: E402
from validate import validate, fit_camera  # noqa: E402


def fnum(expr) -> float:
    return float(sp.N(expr))


def cam(tp, center, direction):
    x, y, z = fit_camera(tp, center, direction)
    return {"x": round(x, 2), "y": round(y, 2), "z": round(z, 2)}


def centroid(tp):
    n = len(tp)
    return [sum(tp[k][i] for k in tp) / n for i in range(3)]


def spec_points(pts: dict) -> dict:
    out = {}
    for name, v in pts.items():
        out[name] = [str(sp.simplify(v[i])) for i in range(3)]
    return out


def emit(here: Path, *, lesson, steps, pts, topo, elements, ans, scale=1.5,
         extra_edges=None, extra_spheres=None, solid=None, query=None,
         answers=None):
    here = Path(here)
    tp = gk.to_three(pts, scale=scale)
    spheres = list(topo.get("spheres") or [])
    if extra_spheres:
        for s in extra_spheres:
            if s not in spheres:
                spheres.append(s)
    edges = list(topo.get("edges") or [])
    if extra_edges:
        edges = edges + extra_edges
    center = centroid(tp)
    if answers:
        lesson = dict(lesson)
        lesson["answers"] = answers
        if "answerValue" in lesson:
            del lesson["answerValue"]
    elif "answerValue" not in lesson:
        lesson = dict(lesson)
        lesson["answerValue"] = f"${ans}$"
    lesson.setdefault("language", "zh-CN")

    data = {
        "lesson": lesson,
        "steps": steps,
        "model": {
            "scale": scale,
            "target": center,
            "initialCamera": fit_camera(tp, center, [6, 5, 7]),
            "points": tp,
            "spheres": spheres,
            "edges": edges,
            "elements": elements,
        },
    }
    if solid:
        data["model"]["solid"] = solid

    spec_doc = {
        "spec": {
            "language": "zh-CN",
            "body": "custom",
            "scale": scale,
            "points": spec_points(pts),
            "topo": {"spheres": spheres, "edges": [
                {"a": e["a"], "b": e["b"]} for e in edges if "a" in e and "b" in e
            ]},
            "query": query or {
                "type": "volume",
                "kind": "tetra",
                "pts": list(pts)[:4],
            },
            "_note": "所求不属于 5 类 query；index.html 由 _render.py 精确渲染。",
        },
        "lesson": data["lesson"],
        "steps": data["steps"],
        "model": {"elements": data["model"]["elements"]},
        "_answer": ans,
    }
    (here / "problem.json").write_text(
        json.dumps(spec_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    errs = validate(data, answer=ans)
    if errs:
        print("FAIL", here.name)
        for e in errs:
            print(" -", e)
        return False

    out = here / "index.html"
    render_html(data, out)
    print(f"PASS  {out}  (答案 {ans})")
    try:
        from build_index import write_index
        write_index()
    except Exception:
        pass
    return True
