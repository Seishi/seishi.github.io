#!/usr/bin/env python3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _kit import cam, centroid, emit
import sympy as sp
import geometry_kernel as gk
import bodies

# cone vertex S at (0,0,8√2), base z=0 radius 4? Skill: cone vertex P on z, base z=0.
# Use S=P at z=h=8√2, O at origin, base radius 4.
h = 8 * sp.sqrt(2)
pts = gk.cone(4, h)
S = pts["P"]
A = pts["A"]  # (4,0,0)
# Wait cone() has P at (0,0,h) and A at (4,0,0) on BASE z=0.
# Generatrix PA from P(0,0,h) to A(4,0,0). Midpoint M.
M = gk.simplify_vec((S + A) / 2)
B = pts["C"]  # (-4,0,0) opposite
# ellipse center (-1, 0, 6√2) in math: wait our z is from 0 at base to h at vertex.
# Previous calc had S at origin, A at z=8√2. Now S at z=h, base at 0.
# Map: z_old = h - z_new. Old M(2,0,4√2) -> new: x=2, z=h-4√2=8√2-4√2=4√2. Yes M=(2,0,4√2)
# Old B(-4,0,8√2) was the base in old (vertex origin). New B is (-4,0,0).
# Old ellipse center (-1,0,6√2) -> new z=8√2-6√2=2√2, x=-1. K=(-1,0,2√2)
K = gk.V(-1, 0, 2 * sp.sqrt(2))
# minor axis ends: y=±2√2 at the center, in the plane.
E1 = gk.V(-1, 2 * sp.sqrt(2), 2 * sp.sqrt(2))
E2 = gk.V(-1, -2 * sp.sqrt(2), 2 * sp.sqrt(2))
pts["M"] = M
pts["K"] = K
pts["E1"] = E1
pts["E2"] = E2
ans = gk.tex(3 * sp.sqrt(17) / 17)
scale = 0.55
tp = gk.to_three(pts, scale=scale)
center = centroid({k: tp[k] for k in ["O", "P", "A", "B", "C", "D"]})
topo = bodies.round_solid(bottom=("A", "B", "C", "D"), apex="P", axis=("O", "P"))

def c(d):
    return cam(tp, center, d)

emit(
    HERE,
    lesson={
        "language": "zh-CN",
        "meta": "交互解题 · 椭圆离心率",
        "title": (
            r"机场为旅客提供的圆锥纸杯，该纸杯母线长为 $12$ 厘米，开口直径为 $8$ 厘米。"
            r"旅客使用纸杯喝水时，当水面与纸杯内壁所形成的椭圆经过母线中点时，椭圆的离心率为"
        ),
        "answerLabel": r"椭圆的离心率",
        "answerValue": f"${ans}$",
    },
    steps=[
        {
            "title": "圆锥的轴截面",
            "content": (
                r"<p>母线 $12$，底面半径 $4$，高 $h=\sqrt{12^{2}-4^{2}}=8\sqrt{2}$。"
                r"半顶角 $\alpha$ 满足 $\sin\alpha=\dfrac{1}{3}$。</p>"
                r"<p>轴截面是等腰三角形。水面所在平面垂直于轴截面时，交线就是椭圆的长轴。</p>"
            ),
            "highlight": ["Axis", "Cone_side", "Point_P", "Point_A", "Len_PA", "Len_OA"],
            "cameraPos": c([8, 6, 5]),
        },
        {
            "title": "椭圆过母线中点",
            "content": (
                r"<p>取母线 $PA$ 的中点 $M$。喝水时水面经过 $M$，并在对侧经过开口上的点 $C$"
                r"（轴截面另一底端点），交线为 $MC$。</p>"
                r"<p>$M\left(2,0,4\sqrt{2}\right)$，$C(-4,0,0)$，"
                r"$MC=2\sqrt{17}$，此即长轴 $2a$，故 $a=\sqrt{17}$。</p>"
            ),
            "highlight": ["Point_M", "Point_C", "Line_MC", "Point_P", "Point_A", "Plane_water"],
            "cameraPos": c([7, 4, 3]),
        },
        {
            "title": "短半轴与离心率",
            "content": (
                r"<p>水面方程 $z=\left(-\dfrac{2\sqrt{2}}{3}\right)x+\dfrac{8\sqrt{2}}{3}$ 代入圆锥，"
                r"投影椭圆中心 $x=-1$，半短轴（沿 $y$，已在水面内）$b=2\sqrt{2}$。</p>"
                r"$$e=\sqrt{1-\dfrac{b^{2}}{a^{2}}}=\sqrt{1-\dfrac{8}{17}}=" + ans + r".$$"
            ),
            "highlight": ["Point_K", "Point_E1", "Point_E2", "Line_MC", "Line_minor",
                          "Plane_water"],
            "cameraPos": c([4, 6, 6]),
        },
    ],
    pts=pts,
    topo=topo,
    extra_edges=[
        {"a": "M", "b": "C", "color": "aux", "dashed": True},
        {"a": "E1", "b": "E2", "color": "aux", "dashed": True},
    ],
    extra_spheres=["M", "K", "E1", "E2"],
    solid={"type": "cone", "base": "O", "apex": "P", "radius": 4 * scale, "opacity": 0.12},
    elements={
        "Axis": {"type": "axes", "size": 6},
        "Point_P": {"type": "point", "center": "P"},
        "Point_A": {"type": "point", "center": "A"},
        "Point_C": {"type": "point", "center": "C"},
        "Point_M": {"type": "point", "center": "M"},
        "Point_K": {"type": "point", "center": "K"},
        "Point_E1": {"type": "point", "center": "E1"},
        "Point_E2": {"type": "point", "center": "E2"},
        "Line_MC": {"type": "line", "a": "M", "b": "C", "color": "emphasis", "depthTest": False},
        "Line_minor": {"type": "line", "a": "E1", "b": "E2", "color": "emphasis", "depthTest": False},
        "Len_PA": {"type": "measure", "a": "P", "b": "A", "label": "12"},
        "Len_OA": {"type": "measure", "a": "O", "b": "A", "label": "4"},
        "Plane_water": {"type": "plane", "pts": ["M", "C", "E1"]},
        "Cone_side": {"type": "cone", "base": "O", "apex": "P", "radius": 4 * scale, "opacity": 0.18},
    },
    ans=ans,
    scale=scale,
)
