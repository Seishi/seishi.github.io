#!/usr/bin/env python3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _kit import cam, centroid, emit
import sympy as sp
import geometry_kernel as gk
import bodies

# k=0: line y=-sqrt(3), circle x^2+y^2=4. Intersections:
# x^2+3=4, x=±1, y=-sqrt(3)
O = gk.V(0, 0, 0)
A = gk.V(1, -sp.sqrt(3), 0)
B = gk.V(-1, -sp.sqrt(3), 0)
M = gk.V(0, -sp.sqrt(3), 0)
P = gk.V(0, -sp.Rational(2, 3) * sp.sqrt(3), -sp.sqrt(sp.Rational(8, 3)))
G = gk.simplify_vec((O + A + B + P) / 4)

# 另一端点 k=1/√2：d²=2，P 落在 xOy 内（四面体退化成平面图形），S=8π
k2 = 1 / sp.sqrt(2)
x = sp.symbols("x")
yline = k2 * x - sp.sqrt(3)
xs = sp.solve(x ** 2 + yline ** 2 - 4, x)
A2 = gk.V(xs[0], k2 * xs[0] - sp.sqrt(3), 0)
B2 = gk.V(xs[1], k2 * xs[1] - sp.sqrt(3), 0)
grad = gk.V(k2, -1, 0)
M2 = gk.simplify_vec(sp.sqrt(3) * grad / grad.dot(grad))
d2 = M2.norm()
x_om = 8 / d2 - 2 * d2
unit_om = M2 / d2
P2 = gk.simplify_vec(unit_om * x_om)  # z=0
G2 = gk.simplify_vec((O + A2 + B2 + P2) / 4)
ans = r"[6\pi,8\pi]"
pts = {
    "O": O, "A": A, "B": B, "P": P, "M": M, "G": G,
    "A2": A2, "B2": B2, "P2": P2, "M2": M2, "G2": G2,
}
scale = 1.4
tp = gk.to_three(pts, scale=scale)
center = centroid(tp)
topo = bodies.tri_pyramid("P", ("A", "B", "O"))

def c(d):
    return cam(tp, center, d)

emit(
    HERE,
    lesson={
        "language": "zh-CN",
        "meta": "交互解题 · 外接球半径",
        "title": (
            r"四面体中，取其异面的两条棱的中点连线称为该四面体的一条「内棱」，"
            r"三条内棱两两垂直的四面体称为「垂棱四面体」。"
            r"空间直角坐标系中，$xOy$ 平面内有圆 $O:x^{2}+y^{2}=4$，"
            r"直线 $y=kx-\sqrt{3}$ 与圆 $O$ 交于 $A$、$B$ 两点，$P$ 为 $xOy$ 平面下方一点。"
            r"若 $P$-$ABO$ 为垂棱四面体，则其外接球表面积 $S(k)$ 的取值范围是"
        ),
        "answerLabel": r"$S(k)$ 的取值范围",
        "answerValue": r"$[6\pi,8\pi]$",
    },
    steps=[
        {
            "title": "垂棱四面体即对棱相等",
            "content": (
                r"<p>三条内棱两两垂直，等价于三组对棱分别相等（等面四面体 / 垂心四面体的特例）：</p>"
                r"$$PA=BO,\quad PB=AO,\quad PO=AB.$$"
                r"<p>$A$、$B$ 在圆 $x^{2}+y^{2}=4$ 上，故 $AO=BO=2$，从而 $PA=PB=2$，且 $PO=AB$。</p>"
            ),
            "highlight": ["Axis", "Plane_xOy", "Point_A", "Point_B", "Point_O", "Point_P",
                          "Line_AB"],
            "cameraPos": c([6, 5, 6]),
        },
        {
            "title": r"情形 $k=0$",
            "content": (
                r"<p>圆心到直线距离 $d=\dfrac{\sqrt{3}}{\sqrt{k^{2}+1}}$。"
                r"$PO=AB=2\sqrt{4-d^{2}}$ 要求 $d^{2}\in[2,3]$，即 $k^{2}\le\dfrac{1}{2}$。</p>"
                r"<p>$k=0$ 时 $d=\sqrt{3}$ 取到上端：$A(1,-\sqrt{3},0)$、$B(-1,-\sqrt{3},0)$，"
                r"$P$ 在 $xOy$ 下方。此时外接半径 $R=\sqrt{\dfrac{3}{2}}$，表面积 $S=6\pi$。</p>"
            ),
            "highlight": ["Plane_xOy", "Line_AB", "Point_M", "Point_P", "Point_A", "Point_B",
                          "Point_O", "Len_OA", "Line_PO", "Sphere_R"],
            "cameraPos": c([7, 3, 5]),
        },
        {
            "title": r"情形 $|k|=\dfrac{1}{\sqrt{2}}$",
            "content": (
                r"<p>三组对棱为 $2,2,c$，其中 $c=2\sqrt{4-d^{2}}$。外接半径 "
                r"$R=\sqrt{\dfrac{6-d^{2}}{2}}$，表面积 $S=2\pi(6-d^{2})$。</p>"
                r"<p>$|k|=\dfrac{1}{\sqrt{2}}$ 时 $d^{2}=2$ 取到下端：$P$ 落到 $xOy$ 内（四面体退化），"
                r"$S=8\pi$。图中虚线为这一款的 $A',B',P'$。</p>"
                r"<p>$d^{2}$ 从 $2$ 连续变到 $3$，故 $S(k)$ 的取值范围是 $[6\pi,8\pi]$。</p>"
            ),
            "highlight": ["Line_A2B2", "Point_A2", "Point_B2", "Point_P2", "Point_M2",
                          "Point_O", "Line_P2O", "Sphere_R2", "Plane_xOy"],
            "cameraPos": c([6, 2, 7]),
        },
    ],
    pts=pts,
    topo=topo,
    extra_edges=[
        {"a": "O", "b": "M", "color": "aux", "dashed": True},
        {"a": "P", "b": "M", "color": "aux", "dashed": True},
        {"a": "A2", "b": "B2", "color": "aux", "dashed": True},
        {"a": "O", "b": "A2", "color": "aux", "dashed": True},
        {"a": "O", "b": "B2", "color": "aux", "dashed": True},
        {"a": "P2", "b": "A2", "color": "aux", "dashed": True},
        {"a": "P2", "b": "B2", "color": "aux", "dashed": True},
        {"a": "P2", "b": "O", "color": "aux", "dashed": True},
        {"a": "O", "b": "M2", "color": "aux", "dashed": True},
    ],
    extra_spheres=["M", "G", "A2", "B2", "P2", "M2", "G2"],
    elements={
        "Axis": {"type": "axes", "size": 3},
        "Point_A": {"type": "point", "center": "A"},
        "Point_B": {"type": "point", "center": "B"},
        "Point_O": {"type": "point", "center": "O"},
        "Point_P": {"type": "point", "center": "P"},
        "Point_M": {"type": "point", "center": "M"},
        "Point_G": {"type": "point", "center": "G"},
        "Point_A2": {"type": "point", "center": "A2"},
        "Point_B2": {"type": "point", "center": "B2"},
        "Point_P2": {"type": "point", "center": "P2"},
        "Point_M2": {"type": "point", "center": "M2"},
        "Line_AB": {"type": "line", "a": "A", "b": "B", "color": "emphasis", "depthTest": False},
        "Line_PO": {"type": "line", "a": "P", "b": "O", "color": "emphasis", "depthTest": False},
        "Line_A2B2": {"type": "line", "a": "A2", "b": "B2", "color": "emphasis", "depthTest": False},
        "Line_P2O": {"type": "line", "a": "P2", "b": "O", "color": "emphasis", "depthTest": False},
        "Len_OA": {"type": "measure", "a": "O", "b": "A", "label": "2"},
        "Plane_xOy": {"type": "plane", "pts": ["A", "B", "O"]},
        "Sphere_R": {"type": "sphere", "center": "G", "radius": float(sp.sqrt(sp.Rational(3, 2))) * scale, "opacity": 0.1},
        "Sphere_R2": {"type": "sphere", "center": "G2", "radius": float(sp.sqrt(2)) * scale, "opacity": 0.08},
        "Plane_ABO": {"type": "plane", "pts": ["A", "B", "O"]},
    },
    ans=ans,
    scale=scale,
)
