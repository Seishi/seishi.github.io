#!/usr/bin/env python3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _kit import cam, centroid, emit
import sympy as sp
import geometry_kernel as gk
import bodies

h = 2
pts = gk.regular_pyramid(3, 2, h)
# rename P -> S
pts["S"] = pts.pop("P")
E = gk.simplify_vec((pts["B"] + pts["C"]) / 2)
pts["E"] = E
# locus: two rays from S along ±n, n = u-2v-2w
u = (pts["A"] - pts["S"])
u = u / u.norm()
v = (pts["B"] - pts["S"])
v = v / v.norm()
w = (pts["C"] - pts["S"])
w = w / w.norm()
n = gk.simplify_vec(u - 2 * v - 2 * w)
n = n / n.norm()
D1 = pts["S"] + 2 * n
D2 = pts["S"] - 2 * n
pts["D"] = D1
pts["D2"] = D2
ans = r"\text{过 }S\text{ 的定直线}(D\ne S)"
scale = 2.0
tp = gk.to_three(pts, scale=scale)
center = centroid(tp)
topo = bodies.tri_pyramid("S", ("A", "B", "C"))

def c(d):
    return cam(tp, center, d)

emit(
    HERE,
    lesson={
        "language": "zh-CN",
        "meta": "交互解题 · 轨迹",
        "title": (
            r"给定一个正三棱锥 $S$-$ABC$（$SA=SB=SC$，$AB=BC=CA$）。"
            r"空间中有不同于 $S$ 的点 $D$，满足 "
            r"$\lvert\cos\angle ASD-2\cos\angle BSD-2\cos\angle CSD\rvert=3$，"
            r"求这种点 $D$ 的轨迹"
        ),
        "answerLabel": r"点 $D$ 的轨迹",
        "answerValue": r"过 $S$ 的定直线（$D\ne S$）",
    },
    steps=[
        {
            "title": "用单位向量改写",
            "content": (
                r"<p>设 $\vec u,\vec v,\vec w,\vec t$ 分别为 $\overrightarrow{SA},\overrightarrow{SB},\overrightarrow{SC},\overrightarrow{SD}$ 方向上的单位向量。条件即</p>"
                r"$$\bigl|\vec t\cdot(\vec u-2\vec v-2\vec w)\bigr|=3.$$"
            ),
            "highlight": ["Axis", "Plane_ABC", "Point_S", "Point_A", "Point_B", "Point_C"],
            "cameraPos": c([6, 5, 6]),
        },
        {
            "title": r"向量 $\vec u-2\vec v-2\vec w$ 的模",
            "content": (
                r"<p>正三棱锥中 $\vec u\cdot\vec v=\vec v\cdot\vec w=\vec w\cdot\vec u$，直接展开得</p>"
                r"$$\lvert\vec u-2\vec v-2\vec w\rvert^{2}=9.$$"
                r"<p>于是 $\lvert\vec t\cdot\vec n\rvert=\lvert\vec n\rvert$ 且 $|\vec t|=1$，"
                r"必须 $\vec t=\pm\vec n/\lvert\vec n\rvert$。方向完全确定。</p>"
            ),
            "highlight": ["Point_S", "Line_locus", "Point_D", "Point_D2", "Point_E", "Plane_SAE"],
            "cameraPos": c([7, 4, 4]),
        },
        {
            "title": "几何位置",
            "content": (
                r"<p>$\vec u-2\vec v-2\vec w=3\vec u-2(\vec u+\vec v+\vec w)$ 落在面 $SAE$ 内"
                r"（$E$ 为 $BC$ 中点），即对称面内。两个方向 $\vec t=\pm\vec n/\lvert\vec n\rvert$ "
                r"对应图中的 $D$ 与 $D'$，都可以沿该直线任意远离 $S$。</p>"
                r"<p>点 $D$ 的轨迹是过顶点 $S$ 的一条定直线（位于面 $SAE$ 内），且 $D\ne S$。</p>"
            ),
            "highlight": ["Line_locus", "Plane_SAE", "Point_S", "Point_D", "Point_D2",
                          "Point_E", "Point_A"],
            "cameraPos": c([5, 6, 5]),
        },
    ],
    pts=pts,
    topo=topo,
    extra_edges=[
        {"a": "S", "b": "E", "color": "aux", "dashed": True},
        {"a": "D2", "b": "D", "color": "aux"},
    ],
    extra_spheres=["E", "D", "D2"],
    elements={
        "Axis": {"type": "axes", "size": 3},
        "Point_S": {"type": "point", "center": "S"},
        "Point_A": {"type": "point", "center": "A"},
        "Point_B": {"type": "point", "center": "B"},
        "Point_C": {"type": "point", "center": "C"},
        "Point_D": {"type": "point", "center": "D"},
        "Point_D2": {"type": "point", "center": "D2"},
        "Point_E": {"type": "point", "center": "E"},
        "Line_locus": {"type": "line", "a": "D2", "b": "D", "color": "emphasis", "depthTest": False},
        "Plane_ABC": {"type": "plane", "pts": ["A", "B", "C"]},
        "Plane_SAE": {"type": "plane", "pts": ["S", "A", "E"]},
    },
    ans=r"D\ne S",
    scale=scale,
)
