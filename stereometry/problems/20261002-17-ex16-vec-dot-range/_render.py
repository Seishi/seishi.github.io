#!/usr/bin/env python3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _kit import cam, centroid, emit
import sympy as sp
import geometry_kernel as gk

# Illustrate min: |u|=3, p ∥ -u, q ∥ u, u·v = -9
u = gk.V(3, 0, 0)
# 最小值 r=3：p 与 u 反向，q 与 u 同向
Z = gk.V(0, 0, 0)
X = u
Pvec = gk.V(-4, 0, 0)
Y = X + Pvec
Qvec = gk.V(2, 0, 0)
W = Qvec
# 最大值 r=4：p 与 u 同向，q 与 u 反向，整组沿 y 平移以免重叠
B3 = gk.V(0, 3, 0)
B1 = gk.V(4, 3, 0)
B2 = gk.V(8, 3, 0)
B4 = gk.V(-2, 3, 0)
pts = {
    "A1": X, "A2": Y, "A3": Z, "A4": W,
    "B1": B1, "B2": B2, "B3": B3, "B4": B4,
}
ans = r"[-9,40]"
scale = 1.3
tp = gk.to_three(pts, scale=scale)
center = centroid(tp)
topo = {
    "spheres": list(pts),
    "edges": [
        {"a": "A1", "b": "A2"}, {"a": "A1", "b": "A3"},
        {"a": "A3", "b": "A4"}, {"a": "A2", "b": "A4"},
        {"a": "B1", "b": "B2", "dashed": True, "color": "aux"},
        {"a": "B1", "b": "B3", "dashed": True, "color": "aux"},
        {"a": "B3", "b": "B4", "dashed": True, "color": "aux"},
        {"a": "B2", "b": "B4", "dashed": True, "color": "aux"},
    ],
}

def c(d):
    return cam(tp, center, d)

emit(
    HERE,
    lesson={
        "language": "zh-CN",
        "meta": "交互解题 · 数量积范围",
        "title": (
            r"若空间向量 $\vec a_1,\vec a_2,\vec a_3,\vec a_4$ 满足 "
            r"$|\vec a_1-\vec a_3|\le|\vec a_1-\vec a_2|=2|\vec a_3-\vec a_4|=4$，"
            r"则 $(\vec a_1-\vec a_3)\cdot(\vec a_2-\vec a_4)$ 的取值范围是"
        ),
        "answerLabel": r"$(\vec a_1-\vec a_3)\cdot(\vec a_2-\vec a_4)$ 的取值范围",
        "answerValue": r"$[-9,40]$",
    },
    steps=[
        {
            "title": "改写成三个独立向量",
            "content": (
                r"<p>令 $\vec u=\vec a_1-\vec a_3$，$\vec p=\vec a_2-\vec a_1$，$\vec q=\vec a_4-\vec a_3$，"
                r"则 $|\vec p|=4$，$|\vec q|=2$，$|\vec u|\le 4$，且三点可以独立选取，"
                r"故 $\vec u,\vec p,\vec q$ 仅受长度约束。</p>"
                r"<p>所求 $\vec v=\vec a_2-\vec a_4=\vec p+\vec u-\vec q$，于是</p>"
                r"$$\vec u\cdot\vec v=|\vec u|^{2}+\vec u\cdot\vec p-\vec u\cdot\vec q.$$"
            ),
            "highlight": ["Axis", "Point_A1", "Point_A2", "Point_A3", "Point_A4",
                          "Vec_u", "Vec_p"],
            "cameraPos": c([6, 5, 6]),
        },
        {
            "title": r"对固定 $|\vec u|=r$ 取极值",
            "content": (
                r"<p>$\vec u\cdot\vec p\in[-4r,4r]$，$\vec u\cdot\vec q\in[-2r,2r]$，互相独立，故</p>"
                r"$$\vec u\cdot\vec v\in\bigl[r^{2}-6r,\ r^{2}+6r\bigr],\qquad r\in[0,4].$$"
            ),
            "highlight": ["Vec_u", "Vec_p", "Vec_q", "Point_A1", "Point_A3"],
            "cameraPos": c([7, 4, 4]),
        },
        {
            "title": r"情形：最小值 $-9$",
            "content": (
                r"<p>下端 $r^{2}-6r=(r-3)^{2}-9$ 在 $r=3$ 取到 $-9$："
                r"$\vec p$ 与 $\vec u$ 反向、$\vec q$ 与 $\vec u$ 同向。图中实线四点 $A_i$ 就是这一款。</p>"
            ),
            "highlight": ["Vec_u", "Vec_p", "Vec_q", "Vec_v",
                          "Point_A1", "Point_A2", "Point_A3", "Point_A4"],
            "cameraPos": c([6, 5, 3]),
        },
        {
            "title": r"情形：最大值 $40$",
            "content": (
                r"<p>上端 $r^{2}+6r$ 在 $r=4$ 取到 $40$："
                r"$\vec p$ 与 $\vec u$ 同向、$\vec q$ 与 $\vec u$ 反向。图中虚线四点 $B_i$ 就是这一款。</p>"
                r"<p>因此 $(\vec a_1-\vec a_3)\cdot(\vec a_2-\vec a_4)$ 的取值范围是 $[-9,40]$。</p>"
            ),
            "highlight": ["Vec_uB", "Vec_pB", "Vec_qB", "Vec_vB",
                          "Point_B1", "Point_B2", "Point_B3", "Point_B4"],
            "cameraPos": c([8, 6, 5]),
        },
    ],
    pts=pts,
    topo=topo,
    elements={
        "Axis": {"type": "axes", "size": 4},
        "Point_A1": {"type": "point", "center": "A1"},
        "Point_A2": {"type": "point", "center": "A2"},
        "Point_A3": {"type": "point", "center": "A3"},
        "Point_A4": {"type": "point", "center": "A4"},
        "Point_B1": {"type": "point", "center": "B1"},
        "Point_B2": {"type": "point", "center": "B2"},
        "Point_B3": {"type": "point", "center": "B3"},
        "Point_B4": {"type": "point", "center": "B4"},
        "Vec_u": {"type": "arrow", "origin": "A3", "dir": [1, 0, 0], "length": 3 * scale, "color": "normal"},
        "Vec_p": {"type": "arrow", "origin": "A1", "dir": [-1, 0, 0], "length": 4 * scale, "color": "emphasis"},
        "Vec_q": {"type": "arrow", "origin": "A3", "dir": [1, 0, 0], "length": 2 * scale, "color": "emphasis"},
        "Vec_v": {"type": "arrow", "origin": "A4", "dir": [-1, 0, 0], "length": 3 * scale, "color": "normal"},
        "Vec_uB": {"type": "arrow", "origin": "B3", "dir": [1, 0, 0], "length": 4 * scale, "color": "normal"},
        "Vec_pB": {"type": "arrow", "origin": "B1", "dir": [1, 0, 0], "length": 4 * scale, "color": "emphasis"},
        "Vec_qB": {"type": "arrow", "origin": "B3", "dir": [-1, 0, 0], "length": 2 * scale, "color": "emphasis"},
        "Vec_vB": {"type": "arrow", "origin": "B4", "dir": [1, 0, 0], "length": 6 * scale, "color": "normal"},
    },
    ans=ans,
    scale=scale,
)
