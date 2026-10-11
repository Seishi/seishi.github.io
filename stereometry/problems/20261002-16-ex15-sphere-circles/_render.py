#!/usr/bin/env python3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _kit import cam, centroid, emit
import sympy as sp
import geometry_kernel as gk
import bodies

# n=5 symmetric packing
n = 5
alpha = sp.asin(sp.sqrt((5 - sp.sqrt(5)) / 10))  # r for n=5
r = sp.sqrt((5 - sp.sqrt(5)) / 10)
O = gk.V(0, 0, 0)
# C0 pole along z, colatitude 0 for the central circle's pole
# surrounding poles at colatitude 2α, azimuth 2π i / n
ca = 1 - 2 * r ** 2  # cos 2α
sa = 2 * r * sp.sqrt(1 - r ** 2)  # sin 2α
Z = gk.V(0, 0, 1)
pts = {"O": O, "Z": Z}
for i in range(5):
    th = 2 * sp.pi * i / 5
    pts[f"K{i}"] = gk.V(sa * sp.cos(th), sa * sp.sin(th), ca)
ans = r"\sqrt{1-\dfrac{1}{4\sin^{2}\dfrac{\pi}{n}}}"
scale = 2.2
tp = gk.to_three(pts, scale=scale)
center = centroid(tp)
topo = {
    "spheres": list(pts),
    "edges": [{"a": "O", "b": "Z"}] + [{"a": "O", "b": f"K{i}"} for i in range(5)]
    + [{"a": f"K{i}", "b": f"K{(i+1)%5}"} for i in range(5)],
}

def c(d):
    return cam(tp, center, d)

emit(
    HERE,
    lesson={
        "language": "zh-CN",
        "meta": "交互解题 · 球面圆半径",
        "title": (
            r"在半径为 $1$ 的球面上有 $n+1$ 个半径相等的圆 $C_0,C_1,\ldots,C_n$，"
            r"且对任意 $i\in\{1,2,3,4,n\}$，$C_i$ 与 $C_0$ 相切，$C_i$ 与 $C_{i+1}$ 相切，"
            r"这里 $C_{n+1}=C_1$。这 $n+1$ 个圆的半径等于"
        ),
        "answerLabel": r"圆的半径",
    },
    answers=[
        {"label": r"$n+1$ 个等圆的半径", "value": f"${ans}$"},
    ],
    steps=[
        {
            "title": "等半径圆的极点",
            "content": (
                r"<p>球半径 $1$，小圆半径 $r$ 时，极点到小圆的球心角 $\alpha=\arcsin r$。"
                r"$C_0$ 的极点放在北极，周围 $n$ 个等圆的极点在纬度 $2\alpha$ 上成正 $n$ 边形，"
                r"且相邻相切给出圆心角 $2\alpha$。</p>"
            ),
            "highlight": ["Axis", "Sphere_unit", "Point_Z", "Point_K0"],
            "cameraPos": c([6, 5, 6]),
        },
        {
            "title": "球面正三角形",
            "content": (
                r"<p>三极点 $C_0,C_i,C_{i+1}$ 构成边长均为 $2\alpha$ 的等边球面三角形，"
                r"顶角 $\dfrac{2\pi}{n}$。余弦定理：</p>"
                r"$$\cos 2\alpha=\cos^{2}2\alpha+\sin^{2}2\alpha\cos\dfrac{2\pi}{n}.$$"
            ),
            "highlight": ["Point_Z", "Point_K0", "Point_K1", "Line_K0K1", "Sphere_unit"],
            "cameraPos": c([5, 6, 4]),
        },
        {
            "title": "解出 $r$",
            "content": (
                r"<p>令 $x=\cos 2\alpha$，得 $x=\dfrac{\cos(2\pi/n)}{1-\cos(2\pi/n)}$，从而</p>"
                r"$$r^{2}=\sin^{2}\alpha=1-\dfrac{1}{4\sin^{2}(\pi/n)}.$$"
                r"<p>图中画出 $n=5$ 的情形。这 $n+1$ 个圆的半径等于 $" + ans + r"$。</p>"
            ),
            "highlight": ["Point_K0", "Point_K1", "Point_K2", "Point_K3", "Point_K4",
                          "Sphere_unit"],
            "cameraPos": c([6, 4, 5]),
        },
    ],
    pts=pts,
    topo=topo,
    elements={
        "Axis": {"type": "axes", "size": 2},
        "Point_Z": {"type": "point", "center": "Z"},
        "Point_K0": {"type": "point", "center": "K0"},
        "Point_K1": {"type": "point", "center": "K1"},
        "Point_K2": {"type": "point", "center": "K2"},
        "Point_K3": {"type": "point", "center": "K3"},
        "Point_K4": {"type": "point", "center": "K4"},
        "Line_K0K1": {"type": "line", "a": "K0", "b": "K1", "color": "emphasis", "depthTest": False},
        "Sphere_unit": {"type": "sphere", "center": "O", "radius": 1 * scale, "opacity": 0.1},
    },
    ans=ans,
    scale=scale,
)
