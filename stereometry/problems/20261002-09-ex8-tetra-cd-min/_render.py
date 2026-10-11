#!/usr/bin/env python3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _kit import cam, centroid, emit
import sympy as sp
import geometry_kernel as gk
import bodies

q = sp.Rational(1, 4) + sp.sqrt(2) / 4
p = 2 * q / (4 * q - 1)
ax = 2 - 1 / q
ay = sp.sqrt(-q ** 2 + 4 * q - 1)
H = gk.V(0, 0, 0)
C = gk.V(-p, 0, 0)
D = gk.V(q, 0, 0)
A = gk.V(ax, ay, 0)
B = gk.V(0, 0, 1)
M = gk.V(-p / 2, 0, 0)
ans = gk.tex(sp.Rational(3, 4) + sp.sqrt(2) / 2)
pts = {"A": A, "B": B, "C": C, "D": D, "H": H, "M": M}
scale = 2.2
tp = gk.to_three(pts, scale=scale)
center = centroid(tp)
topo = bodies.tri_pyramid("B", ("A", "C", "D"))

def c(d):
    return cam(tp, center, d)

emit(
    HERE,
    lesson={
        "language": "zh-CN",
        "meta": "交互解题 · 线段最小值",
        "title": (
            r"三棱锥 $A$-$BCD$ 中，点 $B$ 在平面 $ACD$ 上的射影 $H$ 在线段 $CD$ 上。"
            r"设 $M$ 是线段 $CH$ 的中点。若 $\angle BAH=30^{\circ}$，$AB=2$，"
            r"$\triangle ABM$、$\triangle ABD$ 的面积均为 $1$，则线段 $CD$ 长度的最小值是"
        ),
        "answerLabel": r"$CD$ 长度的最小值",
        "answerValue": f"${ans}$",
    },
    steps=[
        {
            "title": "把射影放到原点",
            "content": (
                r"<p>平面 $ACD$ 取作 $z=0$，$H$ 为原点，$CD$ 沿 $x$ 轴，"
                r"$BH\perp$ 平面 $ACD$，故 $B$ 在 $z$ 轴上。</p>"
                r"<p>$\angle BAH=30^{\circ}$、$AB=2$ 推出 $|AH|=\sqrt{3}$、$BH=1$：</p>"
                r"$$\cos 30^{\circ}=\dfrac{|AH|}{AB}\implies |AH|=\sqrt{3},\quad B=(0,0,1).$$"
                r"<p>设 $C=(-p,0,0)$、$D=(q,0,0)$，且 $p>0,q>0$ 以保证 $H$ 在线段 $CD$ 上，$CD=p+q$。</p>"
            ),
            "highlight": ["Axis", "Plane_ACD", "Point_H", "Point_B", "Line_BH", "Len_AB",
                          "Point_A", "Point_C", "Point_D"],
            "cameraPos": c([6, 5, 5]),
        },
        {
            "title": "面积条件",
            "content": (
                r"<p>$M$ 是 $CH$ 中点，$M=\left(-\dfrac{p}{2},0,0\right)$。"
                r"$S_{\triangle ABD}=S_{\triangle ABM}=1$，即 "
                r"$\bigl|(\overrightarrow{AB}\times\overrightarrow{AD})\bigr|=2$、"
                r"$\bigl|(\overrightarrow{AB}\times\overrightarrow{AM})\bigr|=2$。</p>"
                r"<p>再加 $|AH|^{2}=3$，得到</p>"
                r"$$p=\dfrac{2q}{4q-1},\qquad q\in\bigl[2-\sqrt{3},\,2+\sqrt{3}\bigr].$$"
            ),
            "highlight": ["Point_M", "Point_A", "Point_B", "Point_D", "Plane_ABD",
                          "Plane_ABM", "Len_AB"],
            "cameraPos": c([5, 6, 4]),
        },
        {
            "title": "对 $q$ 求 $CD$ 的最小值",
            "content": (
                r"<p>$CD=p+q=\dfrac{q(4q+1)}{4q-1}$。求导得唯一驻点 "
                r"$q=\dfrac{1+\sqrt{2}}{4}$ 落在区间内，</p>"
                r"$$CD_{\min}=\dfrac{3}{4}+\dfrac{\sqrt{2}}{2}=" + ans + r".$$"
                r"<p>端点处 $CD=6\pm\sqrt{3}$ 都更大。故线段 $CD$ 长度的最小值为 $" + ans + r"$。</p>"
            ),
            "highlight": ["Line_CD", "Point_C", "Point_D", "Point_H", "Point_M"],
            "cameraPos": c([6, 4, 5]),
        },
    ],
    pts=pts,
    topo=topo,
    extra_edges=[
        {"a": "B", "b": "H", "color": "aux", "dashed": True},
        {"a": "A", "b": "H", "color": "aux", "dashed": True},
        {"a": "C", "b": "H", "color": "aux"},
    ],
    extra_spheres=["H", "M"],
    elements={
        "Axis": {"type": "axes", "size": 2.5},
        "Point_H": {"type": "point", "center": "H"},
        "Point_B": {"type": "point", "center": "B"},
        "Point_A": {"type": "point", "center": "A"},
        "Point_C": {"type": "point", "center": "C"},
        "Point_D": {"type": "point", "center": "D"},
        "Point_M": {"type": "point", "center": "M"},
        "Line_BH": {"type": "line", "a": "B", "b": "H", "color": "emphasis", "depthTest": False},
        "Line_CD": {"type": "line", "a": "C", "b": "D", "color": "emphasis", "depthTest": False},
        "Len_AB": {"type": "measure", "a": "A", "b": "B", "label": "2"},
        "Plane_ACD": {"type": "plane", "pts": ["A", "C", "D"]},
        "Plane_ABD": {"type": "plane", "pts": ["A", "B", "D"]},
        "Plane_ABM": {"type": "plane", "pts": ["A", "B", "M"]},
    },
    ans=ans,
    scale=scale,
)
