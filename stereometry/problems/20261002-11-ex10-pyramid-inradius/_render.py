#!/usr/bin/env python3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _kit import cam, centroid, emit
import sympy as sp
import geometry_kernel as gk
import bodies

a = 1 / sp.sqrt(3)
h = sp.Rational(1, 2)
# cuboid ABCD-EFGH: bottom ABCD z=0, top EFGH z=h? Wait height AE=h=1/2, base square side a.
# Standard cuboid: A origin, AB x, AD y, AE z.
pts = gk.cuboid(a, a, h)
# Relabel E,F,G,H as A1,B1,C1,D1 already.
# P center of top square EFGH = A1B1C1D1
P = gk.V(a / 2, a / 2, h)
pts["P"] = P
# incenter of pyramid P-ABCD: along the axis, at height r from base
# r=1/6, so I = (a/2, a/2, r)
I = gk.V(a / 2, a / 2, sp.Rational(1, 6))
pts["I"] = I
ans = gk.tex(sp.Rational(1, 6))
scale = 4.0
tp = gk.to_three(pts, scale=scale)
center = centroid(tp)
topo = bodies.cuboid(bottom=("A", "B", "C", "D"), top=("A1", "B1", "C1", "D1"))

def c(d):
    return cam(tp, center, d)

emit(
    HERE,
    lesson={
        "language": "zh-CN",
        "meta": "交互解题 · 内切球半径",
        "title": (
            r"长方体 $ABCD$-$EFGH$ 中，$AB=BC$，点 $P$ 是正方形 $EFGH$ 的中心。"
            r"若 $|AE|+\dfrac{\sqrt{3}}{2}|AD|=1$，则四棱锥 $P$-$ABCD$ 内切球半径的最大值是"
        ),
        "answerLabel": r"内切球半径的最大值",
        "answerValue": f"${ans}$",
    },
    steps=[
        {
            "title": "底面为正方形的四棱锥",
            "content": (
                r"<p>$AB=BC$ 的长方体底面是正方形，记边长 $a=AD=AB$，高 $AE=h$。"
                r"$P$ 是上底中心，故 $P$-$ABCD$ 是正四棱锥，高为 $h$，顶点在底面中心正上方。</p>"
                r"<p>条件 $h+\dfrac{\sqrt{3}}{2}a=1$，即 $h=1-\dfrac{\sqrt{3}}{2}a$，"
                r"且 $a\in\left(0,\dfrac{2}{\sqrt{3}}\right)$。</p>"
            ),
            "highlight": ["Axis", "Plane_ABCD", "Point_P", "Len_AB", "Len_AE"],
            "cameraPos": c([6, 5, 6]),
        },
        {
            "title": "内切球半径公式",
            "content": (
                r"<p>$r=\dfrac{3V}{S_{\text{全}}}$。$V=\dfrac{1}{3}a^{2}h$，"
                r"侧面是四个全等等腰三角形，斜高 $\sqrt{h^{2}+\dfrac{a^{2}}{4}}$，故</p>"
                r"$$r=\dfrac{ah}{a+2\sqrt{h^{2}+\dfrac{a^{2}}{4}}}.$$"
            ),
            "highlight": ["Point_I", "Sphere_in", "Point_P", "Plane_ABCD"],
            "cameraPos": c([5, 6, 4]),
        },
        {
            "title": "代入约束并对 $a$ 求最大",
            "content": (
                r"<p>令 $s=\dfrac{\sqrt{3}}{2}a$，则 $s\in(0,1)$，$h=1-s$，</p>"
                r"$$r(s)=\dfrac{s(1-s)}{s+\sqrt{4s^{2}-6s+3}}.$$"
                r"<p>$r'(s)=0$ 的根为 $s=\dfrac{1}{2}$，即 $a=\dfrac{1}{\sqrt{3}}$、$h=\dfrac{1}{2}$，"
                r"$r=\dfrac{1}{6}$。端点 $s\to 0^{+}$ 或 $s\to 1^{-}$ 时 $r\to 0$。内切球半径的最大值为 $" + ans + r"$。</p>"
            ),
            "highlight": ["Point_P", "Point_I", "Sphere_in", "Len_AB", "Len_AE"],
            "cameraPos": c([6, 4, 5]),
        },
    ],
    pts=pts,
    topo=topo,
    extra_edges=[
        {"a": "P", "b": "A", "color": "aux"},
        {"a": "P", "b": "B", "color": "aux"},
        {"a": "P", "b": "C", "color": "aux"},
        {"a": "P", "b": "D", "color": "aux"},
    ],
    extra_spheres=["P", "I"],
    elements={
        "Axis": {"type": "axes", "size": 2},
        "Point_P": {"type": "point", "center": "P"},
        "Point_I": {"type": "point", "center": "I"},
        "Len_AB": {"type": "measure", "a": "A", "b": "B", "label": r"a"},
        "Len_AE": {"type": "measure", "a": "A", "b": "A1", "label": r"h"},
        "Plane_ABCD": {"type": "plane", "pts": ["A", "B", "C", "D"]},
        "Sphere_in": {"type": "sphere", "center": "I", "radius": float(sp.Rational(1, 6) * scale), "opacity": 0.2},
    },
    ans=ans,
    scale=scale,
)
