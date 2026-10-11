#!/usr/bin/env python3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _kit import cam, centroid, emit
import sympy as sp
import geometry_kernel as gk
import bodies

phi = (1 + sp.sqrt(5)) / 2
s = (5 + sp.sqrt(5)) / 6
A = gk.V(0, 0, 0)
D = gk.V(phi, 0, 0)
B = gk.V(-1, 1, 0)
P = gk.V(-1, 0, 1)
C = gk.V(-1, s, 0)
ans = gk.tex(phi)
pts = {"A": A, "B": B, "C": C, "D": D, "P": P}
scale = 1.8
tp = gk.to_three(pts, scale=scale)
center = centroid(tp)
topo = bodies.quad_pyramid("P", ("A", "B", "C", "D"))

def c(d):
    return cam(tp, center, d)

emit(
    HERE,
    lesson={
        "language": "zh-CN",
        "meta": "交互解题 · 线段最大值",
        "title": (
            r"四棱锥 $P$-$ABCD$ 中，$\angle PAD=\angle PBC=135^{\circ}$，"
            r"$\angle PAB=\angle PBA=60^{\circ}$，且 $AD\perp$ 平面 $PBC$。已知 $|AB|=\sqrt{2}$，"
            r"平面 $PAB$ 和平面 $PCD$ 所成角的正弦值为 $\dfrac{1}{3}$，求 $|AD|$ 的最大值"
        ),
        "answerLabel": r"$|AD|$ 的最大值",
        "answerValue": f"${ans}$",
    },
    steps=[
        {
            "title": "由垂直与等边确定坐标",
            "content": (
                r"<p>底面 $ABCD$ 在 $z=0$。$AD\perp$ 平面 $PBC$，故平面 $PBC$ 是竖直面。"
                r"取 $A$ 为原点、$AD$ 沿 $x$ 轴，则 $P,B,C$ 有相同的横坐标。</p>"
                r"<p>$\triangle PAB$ 中 $\angle PAB=\angle PBA=60^{\circ}$，$AB=\sqrt{2}$，故它是等边三角形，"
                r"$PA=PB=\sqrt{2}$。$\angle PAD=135^{\circ}$ 推出 $B$、$P$ 的横坐标为 $-1$：</p>"
                r"$$A(0,0,0),\ P(-1,0,1),\ B(-1,1,0),\ D(h,0,0).$$"
            ),
            "highlight": ["Axis", "Plane_ABCD", "Plane_PBC", "Point_P", "Point_A", "Point_B",
                          "Len_AB", "Len_AD"],
            "cameraPos": c([7, 5, 5]),
        },
        {
            "title": r"$\angle PBC=135^{\circ}$ 与 $C$",
            "content": (
                r"<p>$C=(-1,s,0)$。$\overrightarrow{BP}=(0,-1,1)$ 与 $\overrightarrow{BC}=(0,s-1,0)$ 的夹角为 "
                r"$135^{\circ}$ 当且仅当 $s>1$。</p>"
            ),
            "highlight": ["Point_C", "Point_B", "Point_P", "Plane_PBC", "Len_AB"],
            "cameraPos": c([6, 4, 6]),
        },
        {
            "title": "二面角正弦约束",
            "content": (
                r"<p>平面 $PAB$、$PCD$ 的法向量叉积给出 "
                r"$\sin\varphi=\dfrac{1}{3}$，从而 $h$ 是 $s$ 的函数。"
                r"$s\in\bigl(1,\dfrac{3+\sqrt{5}}{2}\bigr]$。</p>"
                r"<p>$|h|$ 在 $s=\dfrac{5+\sqrt{5}}{6}$ 处取到最大值 $\dfrac{1+\sqrt{5}}{2}$。"
                r"因此 $|AD|$ 的最大值是 $" + ans + r"$。</p>"
            ),
            "highlight": ["Plane_PAB", "Plane_PCD", "Point_P", "Point_A", "Point_B",
                          "Point_C", "Point_D"],
            "cameraPos": c([5, 6, 4]),
        },
    ],
    pts=pts,
    topo=topo,
    elements={
        "Axis": {"type": "axes", "size": 3},
        "Point_P": {"type": "point", "center": "P"},
        "Point_A": {"type": "point", "center": "A"},
        "Point_B": {"type": "point", "center": "B"},
        "Point_C": {"type": "point", "center": "C"},
        "Point_D": {"type": "point", "center": "D"},
        "Len_AB": {"type": "measure", "a": "A", "b": "B", "label": r"\sqrt{2}"},
        "Len_AD": {"type": "measure", "a": "A", "b": "D", "label": r"|AD|"},
        "Plane_ABCD": {"type": "plane", "pts": ["A", "B", "C", "D"]},
        "Plane_PBC": {"type": "plane", "pts": ["P", "B", "C"]},
        "Plane_PAB": {"type": "plane", "pts": ["P", "A", "B"]},
        "Plane_PCD": {"type": "plane", "pts": ["P", "C", "D"]},
    },
    ans=ans,
    scale=scale,
)
