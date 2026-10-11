#!/usr/bin/env python3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _kit import cam, centroid, emit
import sympy as sp
import geometry_kernel as gk
import bodies

pts = gk.cuboid(3, 1, 2)
pts["M"] = gk.V(sp.Rational(3, 2), 0, 2)
N1 = gk.V(sp.Rational(4, 3), 0, sp.Rational(5, 16))
N2 = gk.V(sp.Rational(5, 3), 1, sp.Rational(9, 16))
pts["N"] = N1
pts["N2"] = N2
ans = r"\dfrac{5}{16}"
scale = 1.6
tp = gk.to_three(pts, scale=scale)
center = centroid(tp)
topo = bodies.cuboid()

def c(d):
    return cam(tp, center, d)

mp = {k: gk.tex_vec(v) for k, v in pts.items()}
emit(
    HERE,
    lesson={
        "language": "zh-CN",
        "meta": "交互解题 · 点到平面距离",
        "title": (
            r"长方体 $ABCD$-$A_1B_1C_1D_1$ 中，$AB=3$，$BC=1$，$AA_1=2$，"
            r"$M$ 为 $A_1B_1$ 的中点。点 $N$ 是长方体表面上一点，满足 $NB=NM=ND$，"
            r"则 $N$ 到平面 $ABCD$ 的距离为"
        ),
        "answerLabel": r"$N$ 到平面 $ABCD$ 的距离",
    },
    answers=[
        {"label": r"$N$ 在侧面 $ABB_1A_1$", "value": r"$\dfrac{5}{16}$"},
        {"label": r"$N$ 在侧面 $DCC_1D_1$", "value": r"$\dfrac{9}{16}$"},
    ],
    steps=[
        {
            "title": "建系",
            "content": (
                r"<p>以 $A$ 为原点，$AB$、$AD$、$AA_1$ 为 $x$、$y$、$z$ 轴：</p>"
                r"$$A(0,0,0),\ B(3,0,0),\ D(0,1,0),\ A_1(0,0,2).$$"
                r"<p>$M$ 为 $A_1B_1$ 中点，故 $M" + mp["M"] + r"$。平面 $ABCD$ 即 $z=0$，"
                r"所求就是 $N$ 的竖坐标。</p>"
            ),
            "highlight": ["Axis", "Plane_ABCD", "Len_AB", "Len_BC", "Len_AA1",
                          "Point_M", "Line_A1B1"],
            "cameraPos": c([7, 5, 6]),
        },
        {
            "title": "$NB=NM=ND$ 化为垂直平分面",
            "content": (
                r"<p>$N$ 到 $B$、$M$ 等距，故 $N$ 在线段 $BM$ 的垂直平分面上；"
                r"到 $B$、$D$ 等距，故 $N$ 在 $BD$ 的垂直平分面上。</p>"
                r"<p>设 $N=(x,y,z)$，由 $|N-B|^2=|N-M|^2$ 与 $|N-B|^2=|N-D|^2$ 得</p>"
                r"$$12x-16z=11,\qquad 3x-y=4.$$"
            ),
            "highlight": ["Point_M", "Point_B", "Point_D", "Line_BM", "Line_BD",
                          "Plane_perpBM", "Plane_perpBD"],
            "cameraPos": c([8, 4, 3]),
        },
        {
            "title": r"情形一：$N$ 在侧面 $ABB_1A_1$",
            "content": (
                r"<p>在 $y=0$ 上联立 $12x-16z=11$、$3x=4$，得</p>"
                r"$$N_1\left(\dfrac{4}{3},0,\dfrac{5}{16}\right).$$"
                r"<p>它落在矩形 $ABB_1A_1$ 内部。到地面 $ABCD$（$z=0$）的距离就是竖坐标 $\dfrac{5}{16}$。</p>"
            ),
            "highlight": ["Point_N", "Plane_ABB1A1", "Plane_ABCD",
                          "Line_BN", "Line_MN", "Line_DN", "Point_M", "Point_B", "Point_D"],
            "cameraPos": c([8, 3, 4]),
        },
        {
            "title": r"情形二：$N$ 在侧面 $DCC_1D_1$",
            "content": (
                r"<p>在 $y=1$ 上联立得</p>"
                r"$$N_2\left(\dfrac{5}{3},1,\dfrac{9}{16}\right).$$"
                r"<p>它落在矩形 $DCC_1D_1$ 内部，到地面距离为 $\dfrac{9}{16}$。"
                r"其它四个面无解或超出边界。因此距离为 $\dfrac{5}{16}$ 或 $\dfrac{9}{16}$。</p>"
            ),
            "highlight": ["Point_N2", "Plane_DCC1D1", "Plane_ABCD",
                          "Line_BN2", "Line_MN2", "Line_DN2", "Point_M", "Point_B", "Point_D"],
            "cameraPos": c([4, 7, 4]),
        },
    ],
    pts=pts,
    topo=topo,
    extra_edges=[
        {"a": "B", "b": "M", "color": "aux", "dashed": True},
        {"a": "B", "b": "D", "color": "aux", "dashed": True},
        {"a": "B", "b": "N", "color": "aux", "dashed": True},
        {"a": "M", "b": "N", "color": "aux", "dashed": True},
        {"a": "D", "b": "N", "color": "aux", "dashed": True},
        {"a": "B", "b": "N2", "color": "aux", "dashed": True},
        {"a": "M", "b": "N2", "color": "aux", "dashed": True},
        {"a": "D", "b": "N2", "color": "aux", "dashed": True},
    ],
    extra_spheres=["M", "N", "N2"],
    elements={
        "Axis": {"type": "axes", "size": 3.5},
        "Point_M": {"type": "point", "center": "M"},
        "Point_B": {"type": "point", "center": "B"},
        "Point_D": {"type": "point", "center": "D"},
        "Point_N": {"type": "point", "center": "N"},
        "Point_N2": {"type": "point", "center": "N2"},
        "Line_A1B1": {"type": "line", "a": "A1", "b": "B1", "color": "emphasis", "depthTest": False},
        "Line_BM": {"type": "line", "a": "B", "b": "M", "color": "emphasis", "depthTest": False},
        "Line_BD": {"type": "line", "a": "B", "b": "D", "color": "emphasis", "depthTest": False},
        "Line_BN": {"type": "line", "a": "B", "b": "N", "color": "emphasis", "depthTest": False},
        "Line_MN": {"type": "line", "a": "M", "b": "N", "color": "emphasis", "depthTest": False},
        "Line_DN": {"type": "line", "a": "D", "b": "N", "color": "emphasis", "depthTest": False},
        "Line_BN2": {"type": "line", "a": "B", "b": "N2", "color": "emphasis", "depthTest": False},
        "Line_MN2": {"type": "line", "a": "M", "b": "N2", "color": "emphasis", "depthTest": False},
        "Line_DN2": {"type": "line", "a": "D", "b": "N2", "color": "emphasis", "depthTest": False},
        "Len_AB": {"type": "measure", "a": "A", "b": "B", "label": "3"},
        "Len_BC": {"type": "measure", "a": "B", "b": "C", "label": "1"},
        "Len_AA1": {"type": "measure", "a": "A", "b": "A1", "label": "2"},
        "Plane_ABCD": {"type": "plane", "pts": ["A", "B", "C", "D"]},
        "Plane_ABB1A1": {"type": "plane", "pts": ["A", "B", "B1", "A1"]},
        "Plane_DCC1D1": {"type": "plane", "pts": ["D", "C", "C1", "D1"]},
        "Plane_perpBM": {"type": "plane", "pts": ["N", "N2", "M"]},
        "Plane_perpBD": {"type": "plane", "pts": ["N", "N2", "D"]},
    },
    ans=ans,
    scale=scale,
)
