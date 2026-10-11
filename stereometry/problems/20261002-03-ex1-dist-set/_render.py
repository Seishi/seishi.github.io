#!/usr/bin/env python3
"""例题1：四面体到平面距离集合的元素个数。枚举题，escape hatch 出图。"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "engine" / "lib"), str(ROOT / "engine" / "scripts")]

import geometry_kernel as gk
import bodies
from generate import render_html
from validate import validate, fit_camera
import sympy as sp

ans = r"1,2,3"

def put_base_xy(pts, base, apex):
    """旋转平移：底面 base 落到 z=0，apex 在 z>=0。"""
    a, b, c = (pts[n] for n in base)
    e1 = gk.simplify_vec((b - a) / (b - a).norm())
    n = gk.simplify_vec(gk.normal_from_points(a, b, c))
    n = gk.simplify_vec(n / n.norm())
    if n.dot(pts[apex] - a) < 0:
        n = -n
    e2 = gk.simplify_vec(n.cross(e1))
    out = {}
    for k, p in pts.items():
        w = p - a
        out[k] = gk.V(sp.simplify(w.dot(e1)), sp.simplify(w.dot(e2)), sp.simplify(w.dot(n)))
    return out

A0 = gk.V(1, 1, 1)
B0 = gk.V(1, -1, -1)
C0 = gk.V(-1, 1, -1)
D0 = gk.V(-1, -1, 1)
raw = {
    "A": A0, "B": B0, "C": C0, "D": D0,
    "E": gk.midpoint(A0, B0),
    "F": gk.midpoint(A0, C0),
    "G": gk.midpoint(D0, B0),
    "H": gk.midpoint(D0, C0),
    "U": gk.midpoint(D0, A0),
    "V": gk.midpoint(D0, B0),
    "W": gk.midpoint(D0, C0),
}
# 1–3, |S|=3：d(D)=h, d(A)=h/2, d(B)=h, d(C)=2h
raw["U3"] = A0 * sp.Rational(2, 3) + D0 * sp.Rational(1, 3)  # DU:UA=2:1
raw["V3"] = gk.midpoint(D0, B0)
raw["W3"] = C0 * sp.Rational(1, 3) + D0 * sp.Rational(2, 3)  # DW:WC=1:2
pts = put_base_xy(raw, ("A", "B", "C"), "D")
assert all(sp.simplify(pts[n][2]) == 0 for n in ("A", "B", "C"))
assert sp.simplify(pts["D"][2]).is_positive

scale = 1.8
tp = gk.to_three(pts, scale=scale)
topo = bodies.tri_pyramid("D", ("A", "B", "C"))
topo["spheres"] = ["A", "B", "C", "D", "E", "F", "G", "H", "U", "V", "W", "U3", "V3", "W3"]
center = [sum(tp[k][i] for k in ("A", "B", "C", "D")) / 4 for i in range(3)]

def cam(direction):
    x, y, z = fit_camera(tp, center, direction)
    return {"x": round(x, 2), "y": round(y, 2), "z": round(z, 2)}

data = {
    "lesson": {
        "language": "zh-CN",
        "meta": "交互解题 · 距离集合",
        "title": (
            "空间中四面体 $ABCD$ 与平面 $\\alpha$："
            "四点都不在 $\\alpha$ 上，且不都在同侧；"
            "若某棱与 $\\alpha$ 有交点，则该点总是这条棱的中点或三等分点。"
            "设 $S$ 为四点到 $\\alpha$ 的距离组成的集合，求 $|S|$ 的所有可能值"
        ),
        "answerLabel": "集合 $S$ 元素个数的所有可能值",
        "answerValue": f"${ans}$",
    },
    "steps": [
        {
            "title": "平面怎样切开四面体",
            "content": (
                r"<p>把四面体看成棱锥 $D$-$ABC$，底面 $ABC$ 放在水平面 $z=0$，顶点 $D$ 在上方。</p>"
                r"<p>四点都不在 $\alpha$ 上，又不同侧，故 $\alpha$ 把顶点分成两类：</p>"
                r"<ul>"
                r"<li>$1$–$3$：一侧 $1$ 点，另一侧 $3$ 点，截 $3$ 条棱；</li>"
                r"<li>$2$–$2$：两侧各 $2$ 点，截 $4$ 条棱（截面为四边形）。</li>"
                r"</ul>"
            ),
            "highlight": [
                "Axis", "Plane_ABC", "Point_A", "Point_B", "Point_C", "Point_D",
            ],
            "cameraPos": cam([5, 4, 6]),
        },
        {
            "title": "截点位置决定距离比",
            "content": (
                r"<p>点 $X,Y$ 分居 $\alpha$ 两侧时，棱 $XY$ 与 $\alpha$ 的交点分线段比等于到平面的距离比。</p>"
                r"<p>交点是中点 $\Rightarrow d(X,\alpha)=d(Y,\alpha)$；"
                r"是三等分点 $\Rightarrow$ 距离比为 $1:2$ 或 $2:1$。</p>"
                r"<p>因此每个距离只能是某个基准 $h$ 的 $h,\ \dfrac{h}{2},\ 2h$。</p>"
            ),
            "highlight": [
                "Line_DA", "Line_DB", "Line_DC",
                "Point_U", "Point_V", "Point_W",
            ],
            "cameraPos": cam([6, 2, 5]),
        },
        {
            "title": r"情形 $2$–$2$",
            "content": (
                r"<p>两侧各两点，截面为四边形。图中 $\alpha$ 过 $AB,AC,DB,DC$ 的中点 $E,F,G,H$："
                r"此时四点距离都是 $h$，$|S|=1$。</p>"
                r"<p>把其中若干条跨棱改成三等分，两侧距离仍只能取 $h,\dfrac{h}{2},2h$ 这三档，"
                r"交约束后 $|S|\in\{1,2,3\}$，凑不出 $4$ 个互异距离。</p>"
            ),
            "highlight": [
                "Plane_Alpha22", "Line_AB", "Line_AC", "Line_DB", "Line_DC",
                "Point_E", "Point_F", "Point_G", "Point_H",
            ],
            "cameraPos": cam([6, 4, 5]),
        },
        {
            "title": r"情形 $1$–$3$",
            "content": (
                r"<p>孤立点一侧、另三点另一侧，截 $DA,DB,DC$ 三条棱。</p>"
                r"<p>浅色截面 $UVW$ 过三条棱中点、平行于底面：四点距离都是 $h$，$|S|=1$。"
                r"把截点整体移近底面（三等分）则 $|S|=2$。</p>"
                r"<p>另一截面 $U_3V_3W_3$ 取距离比 $2:1,\ 1:1,\ 1:2$，"
                r"四点距离为 $h,\dfrac{h}{2},h,2h$，$|S|=3$。</p>"
                r"<p>两种分隔都能取到 $1,2,3$，都不能取到 $4$。所以 $|S|$ 的所有可能值为 $1,2,3$。</p>"
            ),
            "highlight": [
                "Plane_Alpha13", "Plane_Alpha13b",
                "Line_DA", "Line_DB", "Line_DC",
                "Point_U", "Point_V", "Point_W",
                "Point_U3", "Point_V3", "Point_W3",
            ],
            "cameraPos": cam([4, 6, 4]),
        },
    ],
    "model": {
        "scale": scale,
        "target": center,
        "initialCamera": fit_camera(tp, center, [5, 4, 6]),
        "points": tp,
        "spheres": topo["spheres"],
        "edges": topo["edges"],
        "elements": {
            "Axis": {"type": "axes", "size": 3},
            "Plane_Alpha22": {"type": "plane", "pts": ["E", "F", "H", "G"]},
            "Plane_Alpha13": {"type": "plane", "pts": ["U", "V", "W"]},
            "Plane_Alpha13b": {"type": "plane", "pts": ["U3", "V3", "W3"]},
            "Plane_ABC": {"type": "plane", "pts": ["A", "B", "C"]},
            "Point_A": {"type": "point", "center": "A"},
            "Point_B": {"type": "point", "center": "B"},
            "Point_C": {"type": "point", "center": "C"},
            "Point_D": {"type": "point", "center": "D"},
            "Point_E": {"type": "point", "center": "E"},
            "Point_F": {"type": "point", "center": "F"},
            "Point_G": {"type": "point", "center": "G"},
            "Point_H": {"type": "point", "center": "H"},
            "Point_U": {"type": "point", "center": "U"},
            "Point_V": {"type": "point", "center": "V"},
            "Point_W": {"type": "point", "center": "W"},
            "Point_U3": {"type": "point", "center": "U3"},
            "Point_V3": {"type": "point", "center": "V3"},
            "Point_W3": {"type": "point", "center": "W3"},
            "Line_AB": {"type": "line", "a": "A", "b": "B", "color": "emphasis", "depthTest": False},
            "Line_AC": {"type": "line", "a": "A", "b": "C", "color": "emphasis", "depthTest": False},
            "Line_DA": {"type": "line", "a": "D", "b": "A", "color": "emphasis", "depthTest": False},
            "Line_DB": {"type": "line", "a": "D", "b": "B", "color": "emphasis", "depthTest": False},
            "Line_DC": {"type": "line", "a": "D", "b": "C", "color": "emphasis", "depthTest": False},
        },
    },
}

here = Path(__file__).resolve().parent
doc = {
    "spec": {
        "language": "zh-CN",
        "body": "custom",
        "scale": scale,
        "points": {k: [str(c) for c in v] for k, v in pts.items()},
        "topo": topo,
        "query": {"type": "volume", "kind": "tetra", "pts": ["A", "B", "C", "D"]},
        "_note": "所求是 |S| 的可能值，不属于 5 类 query；index.html 由本脚本渲染。",
    },
    "lesson": data["lesson"],
    "steps": data["steps"],
    "model": {"elements": data["model"]["elements"]},
    "_answer": ans,
}
(here / "problem.json").write_text(
    json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

errs = validate(data, answer=ans)
if errs:
    print("FAIL")
    for e in errs:
        print(" -", e)
    sys.exit(1)

out = here / "index.html"
render_html(data, out)
print(f"PASS  已生成: {out}  (答案 {ans})")
