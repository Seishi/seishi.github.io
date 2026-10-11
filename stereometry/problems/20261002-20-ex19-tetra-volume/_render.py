#!/usr/bin/env python3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _kit import cam, centroid, emit
import sympy as sp
import geometry_kernel as gk
import bodies

a = sp.sqrt(sp.Rational(59, 2))
pts = gk.regular_tetrahedron(a)
# shift so centroid at a nice place; rotate is already standard
ans = gk.tex(59 * sp.sqrt(59) / 24)
scale = 0.85
tp = gk.to_three(pts, scale=scale)
center = centroid(tp)
topo = bodies.tri_pyramid("D", ("A", "B", "C"))
# regular tetra all 6 edges
topo["edges"] = [
    {"a": "A", "b": "B"}, {"a": "B", "b": "C"}, {"a": "C", "b": "A"},
    {"a": "A", "b": "D"}, {"a": "B", "b": "D"}, {"a": "C", "b": "D"},
]

def c(d):
    return cam(tp, center, d)

emit(
    HERE,
    lesson={
        "language": "zh-CN",
        "meta": "交互解题 · 体积",
        "title": (
            r"在空间直角坐标系 $O$-$xyz$ 中，一个正四面体的顶点 $A,B,C,D$ 的横坐标分别为 $2,3,5,7$，"
            r"则该正四面体的体积是"
        ),
        "answerLabel": r"正四面体的体积",
        "answerValue": f"${ans}$",
    },
    steps=[
        {
            "title": "横坐标的方差与棱长",
            "content": (
                r"<p>四个横坐标 $2,3,5,7$，均值 $\dfrac{17}{4}$，</p>"
                r"$$\sum(x_i-\bar x)^{2}=\dfrac{59}{4}.$$"
                r"<p>正四面体顶点相对重心各向同性：$\sum_i (\vec v_i\cdot\vec e_x)^{2}=\dfrac{a^{2}}{2}$，"
                r"其中 $a$ 为棱长。因此 $a^{2}=\dfrac{59}{2}$。</p>"
            ),
            "highlight": ["Axis", "Point_A", "Point_B", "Point_C", "Point_D", "Len_AB"],
            "cameraPos": c([6, 5, 6]),
        },
        {
            "title": "用棱长写体积",
            "content": (
                r"<p>正四面体体积公式 $V=\dfrac{a^{3}\sqrt{2}}{12}$。"
                r"$a^{3}=\left(\dfrac{59}{2}\right)^{3/2}=\dfrac{59\sqrt{59}}{2\sqrt{2}}$，代入得</p>"
                r"$$V=\dfrac{59\sqrt{59}}{24}.$$"
            ),
            "highlight": ["Point_A", "Point_B", "Point_C", "Point_D", "Plane_ABC", "Len_AB"],
            "cameraPos": c([5, 6, 4]),
        },
        {
            "title": "与外接半径核对",
            "content": (
                r"<p>正四面体外接半径 $R=\dfrac{\sqrt{6}}{4}a$，代入体积公式 "
                r"$V=\dfrac{8\sqrt{3}}{27}R^{3}$ 得到同一结果。"
                r"图中是棱长 $\sqrt{59/2}$ 的正四面体，体积为 $" + ans + r"$。</p>"
            ),
            "highlight": ["Point_A", "Point_B", "Point_C", "Point_D", "Plane_BCD"],
            "cameraPos": c([6, 4, 5]),
        },
    ],
    pts=pts,
    topo=topo,
    elements={
        "Axis": {"type": "axes", "size": 4},
        "Point_A": {"type": "point", "center": "A"},
        "Point_B": {"type": "point", "center": "B"},
        "Point_C": {"type": "point", "center": "C"},
        "Point_D": {"type": "point", "center": "D"},
        "Len_AB": {"type": "measure", "a": "A", "b": "B", "label": r"\sqrt{59/2}"},
        "Plane_ABC": {"type": "plane", "pts": ["A", "B", "C"]},
        "Plane_BCD": {"type": "plane", "pts": ["B", "C", "D"]},
    },
    ans=ans,
    scale=scale,
)
