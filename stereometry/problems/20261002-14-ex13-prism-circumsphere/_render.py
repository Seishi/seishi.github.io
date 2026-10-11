#!/usr/bin/env python3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _kit import cam, centroid, emit
import sympy as sp
import geometry_kernel as gk
import bodies

pts = gk.right_prism({"A": (0, 0), "B": (6, 0), "C": (0, 2)}, 4)
E = gk.V(0, 0, 2)
F = gk.V(2, 0, 0)
pts["E"] = E
pts["F"] = F
ans = gk.tex(sp.sqrt(11))
scale = 1.15
tp = gk.to_three(pts, scale=scale)
center = centroid(tp)
topo = bodies.prism(bottom=("A", "B", "C"), top=("A1", "B1", "C1"))

def c(d):
    return cam(tp, center, d)

emit(
    HERE,
    lesson={
        "language": "zh-CN",
        "meta": "交互解题 · 外接球半径",
        "title": (
            r"直三棱柱 $ABC$-$A_1B_1C_1$ 中，$AC\perp AB$，$AC=2$，$AA_1=4$，$AB=6$。"
            r"点 $E$、$F$ 分别是棱 $AA_1$、$AB$ 上的动点，当折线 $C_1$-$E$-$F$-$B_1$ 的长度"
            r"即 $C_1E+EF+FB_1$ 最小时，三棱锥 $B_1C_1EF$ 的外接球半径是"
        ),
        "answerLabel": r"三棱锥 $B_1C_1EF$ 的外接球半径",
        "answerValue": f"${ans}$",
    },
    steps=[
        {
            "title": "建系",
            "content": (
                r"<p>底面直角三角形放在 $z=0$：$A$ 为原点，$AB$ 沿 $x$ 轴，$AC$ 沿 $y$ 轴，高 $4$。</p>"
                r"$$A(0,0,0),\ B(6,0,0),\ C(0,2,0),\ A_1(0,0,4).$$"
            ),
            "highlight": ["Axis", "Plane_ABC", "Len_AB", "Len_AC", "Len_AA1",
                          "Point_E", "Point_F"],
            "cameraPos": c([8, 5, 6]),
        },
        {
            "title": "展开求最短折线",
            "content": (
                r"<p>把侧面 $ACC_1A_1$ 与 $ABB_1A_1$ 摊平：$C_1$ 到 $E$ 再到 $F$ 再到 $B_1$ 变成平面折线。"
                r"最短路径是直线，对应</p>"
                r"$$E=(0,0,2),\qquad F=(2,0,0).$$"
                r"<p>即 $E$ 为 $AA_1$ 中点，$AF=2$。</p>"
            ),
            "highlight": ["Point_E", "Point_F", "Point_C1", "Point_B1", "Line_C1E",
                          "Line_EF", "Line_FB1", "Plane_ABB1A1"],
            "cameraPos": c([6, 6, 3]),
        },
        {
            "title": "四面体 $B_1C_1EF$ 的外接球",
            "content": (
                r"<p>四点 $B_1(6,0,4)$、$C_1(0,2,4)$、$E(0,0,2)$、$F(2,0,0)$。"
                r"解 $|X-B_1|=|X-C_1|=|X-E|=|X-F|$，得外接半径 $R=\sqrt{11}$。</p>"
            ),
            "highlight": ["Point_B1", "Point_C1", "Point_E", "Point_F", "Sphere_R",
                          "Plane_B1C1EF"],
            "cameraPos": c([5, 6, 5]),
        },
    ],
    pts=pts,
    topo=topo,
    extra_edges=[
        {"a": "C1", "b": "E", "color": "aux"},
        {"a": "E", "b": "F", "color": "aux"},
        {"a": "F", "b": "B1", "color": "aux"},
        {"a": "B1", "b": "C1", "color": "aux", "dashed": True},
        {"a": "C1", "b": "F", "color": "aux", "dashed": True},
        {"a": "B1", "b": "E", "color": "aux", "dashed": True},
    ],
    extra_spheres=["E", "F"],
    elements={
        "Axis": {"type": "axes", "size": 5},
        "Point_E": {"type": "point", "center": "E"},
        "Point_F": {"type": "point", "center": "F"},
        "Point_C1": {"type": "point", "center": "C1"},
        "Point_B1": {"type": "point", "center": "B1"},
        "Line_C1E": {"type": "line", "a": "C1", "b": "E", "color": "emphasis", "depthTest": False},
        "Line_EF": {"type": "line", "a": "E", "b": "F", "color": "emphasis", "depthTest": False},
        "Line_FB1": {"type": "line", "a": "F", "b": "B1", "color": "emphasis", "depthTest": False},
        "Len_AB": {"type": "measure", "a": "A", "b": "B", "label": "6"},
        "Len_AC": {"type": "measure", "a": "A", "b": "C", "label": "2"},
        "Len_AA1": {"type": "measure", "a": "A", "b": "A1", "label": "4"},
        "Plane_ABC": {"type": "plane", "pts": ["A", "B", "C"]},
        "Plane_ABB1A1": {"type": "plane", "pts": ["A", "B", "B1", "A1"]},
        "Plane_B1C1EF": {"type": "plane", "pts": ["B1", "C1", "E"]},
        "Sphere_R": {"type": "sphere", "center": "E", "radius": float(sp.sqrt(11) * scale), "opacity": 0.08},
    },
    ans=ans,
    scale=scale,
)
