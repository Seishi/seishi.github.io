#!/usr/bin/env python3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _kit import cam, centroid, emit
import sympy as sp
import geometry_kernel as gk
import bodies

h1 = 3 * sp.sqrt(2) / 2
h2 = 9 * sp.sqrt(2) / 2
# 直角在 B 的最小：h1=6√2, h2=2√2
h1b = 6 * sp.sqrt(2)
h2b = 2 * sp.sqrt(2)
C = gk.V(0, 0, 0)
D = gk.V(5, 0, 0)
A = gk.V(0, h1, 0)
B = gk.V(5, h2, 0)
Ap = gk.V(0, h1b, 0)
Bp = gk.V(5, h2b, 0)
P = gk.V(sp.Rational(9, 5), 0, sp.Rational(12, 5))
ans = gk.tex(12 * sp.sqrt(2))
pts = {"A": A, "B": B, "C": C, "D": D, "P": P, "Ap": Ap, "Bp": Bp}
scale = 0.9
tp = gk.to_three(pts, scale=scale)
center = centroid(tp)
topo = bodies.quad_pyramid("P", ("A", "B", "C", "D"))

def c(d):
    return cam(tp, center, d)

mp = {k: gk.tex_vec(v) for k, v in pts.items()}
emit(
    HERE,
    lesson={
        "language": "zh-CN",
        "meta": "交互解题 · 体积最小值",
        "title": (
            r"四棱锥 $P$-$ABCD$ 中，$\triangle PAB$ 为直角三角形，且它在平面 $PDC$ 上的投影恰为 "
            r"$\triangle PDC$。已知 $PC=3$，$PD=4$，$CD=5$，求四棱锥 $P$-$ABCD$ 体积的最小值"
        ),
        "answerLabel": r"体积的最小值",
        "answerValue": f"${ans}$",
    },
    steps=[
        {
            "title": "由 $3$-$4$-$5$ 与投影条件建系",
            "content": (
                r"<p>底面 $ABCD$ 在 $z=0$。$PC=3$、$PD=4$、$CD=5$，故 $\triangle PDC$ 直角在 $P$。"
                r"把 $C$ 放原点、$CD$ 沿 $x$ 轴，并取 $P$ 在 $xz$ 平面：</p>"
                r"$$C(0,0,0),\ D(5,0,0),\ P\left(\dfrac{9}{5},0,\dfrac{12}{5}\right).$$"
                r"<p>$\triangle PAB$ 在平面 $PDC$ 上的投影恰为 $\triangle PDC$，"
                r"故 $A$、$B$ 在该平面上的射影分别是 $C$、$D$，于是 $AC\perp$ 平面 $PDC$、$BD\perp$ 平面 $PDC$。</p>"
            ),
            "highlight": ["Axis", "Plane_ABCD", "Plane_PDC", "Len_PC", "Len_PD", "Len_CD",
                          "Point_P", "Point_C", "Point_D"],
            "cameraPos": c([8, 5, 4]),
        },
        {
            "title": "用高度参数表示底面",
            "content": (
                r"<p>平面 $PDC$ 的法向量沿 $y$ 轴，故</p>"
                r"$$A=(0,h_1,0),\quad B=(5,h_2,0).$$"
                r"<p>为使底面是凸四边形，$h_1$、$h_2$ 同号。底面积为 $\dfrac{5}{2}(|h_1|+|h_2|)$，"
                r"$P$ 到底面距离 $\dfrac{12}{5}$，体积</p>"
                r"$$V=2(|h_1|+|h_2|).$$"
            ),
            "highlight": ["Point_A", "Point_B", "Point_C", "Point_D", "Plane_ABCD",
                          "Line_AC", "Line_BD"],
            "cameraPos": c([6, 6, 6]),
        },
        {
            "title": r"情形一：直角在 $A$",
            "content": (
                r"<p>$\overrightarrow{PA}\cdot\overrightarrow{AB}=0$ 化成 $h_1(h_2-h_1)=9$。"
                r"取 $h_1>0$、$h_2>0$，则 $h_2=h_1+\dfrac{9}{h_1}$，</p>"
                r"$$V=2\left(2h_1+\dfrac{9}{h_1}\right)\ge 12\sqrt{2},$$"
                r"<p>当 $h_1=\dfrac{3\sqrt{2}}{2}$、$h_2=\dfrac{9\sqrt{2}}{2}$ 时等号成立。"
                r"图中实线底面 $ABCD$ 就是这一款。</p>"
            ),
            "highlight": ["Plane_PAB", "Plane_ABCD", "Point_P", "Point_A", "Point_B",
                          "Len_PA", "Len_AB", "Line_AC", "Line_BD"],
            "cameraPos": c([5, 7, 4]),
        },
        {
            "title": r"情形二：直角在 $B$",
            "content": (
                r"<p>$\overrightarrow{PB}\cdot\overrightarrow{BA}=0$ 化成 $h_2(h_1-h_2)=16$，"
                r"$h_1=h_2+\dfrac{16}{h_2}$，</p>"
                r"$$V=2\left(2h_2+\dfrac{16}{h_2}\right)\ge 16\sqrt{2},$$"
                r"<p>当 $h_2=2\sqrt{2}$、$h_1=6\sqrt{2}$ 时等号成立。图中虚线底面 $A'B'CD$ 就是这一款，"
                r"比情形一大。直角在 $P$ 时更大。故全局最小为 $" + ans + r"$。</p>"
            ),
            "highlight": ["Plane_PApBp", "Plane_ApBpCD", "Point_P", "Point_Ap", "Point_Bp",
                          "Line_ApC", "Line_BpD"],
            "cameraPos": c([8, 8, 5]),
        },
    ],
    pts=pts,
    topo=topo,
    extra_edges=[
        {"a": "A", "b": "C", "color": "aux", "dashed": True},
        {"a": "B", "b": "D", "color": "aux", "dashed": True},
        {"a": "Ap", "b": "Bp", "color": "aux", "dashed": True},
        {"a": "Ap", "b": "C", "color": "aux", "dashed": True},
        {"a": "Bp", "b": "D", "color": "aux", "dashed": True},
        {"a": "P", "b": "Ap", "color": "aux", "dashed": True},
        {"a": "P", "b": "Bp", "color": "aux", "dashed": True},
    ],
    extra_spheres=["Ap", "Bp"],
    elements={
        "Axis": {"type": "axes", "size": 5},
        "Point_P": {"type": "point", "center": "P"},
        "Point_A": {"type": "point", "center": "A"},
        "Point_B": {"type": "point", "center": "B"},
        "Point_C": {"type": "point", "center": "C"},
        "Point_D": {"type": "point", "center": "D"},
        "Point_Ap": {"type": "point", "center": "Ap"},
        "Point_Bp": {"type": "point", "center": "Bp"},
        "Line_AC": {"type": "line", "a": "A", "b": "C", "color": "emphasis", "depthTest": False},
        "Line_BD": {"type": "line", "a": "B", "b": "D", "color": "emphasis", "depthTest": False},
        "Line_ApC": {"type": "line", "a": "Ap", "b": "C", "color": "emphasis", "depthTest": False},
        "Line_BpD": {"type": "line", "a": "Bp", "b": "D", "color": "emphasis", "depthTest": False},
        "Len_PC": {"type": "measure", "a": "P", "b": "C", "label": "3"},
        "Len_PD": {"type": "measure", "a": "P", "b": "D", "label": "4"},
        "Len_CD": {"type": "measure", "a": "C", "b": "D", "label": "5"},
        "Len_PA": {"type": "measure", "a": "P", "b": "A", "label": r"PA"},
        "Len_AB": {"type": "measure", "a": "A", "b": "B", "label": r"AB"},
        "Plane_ABCD": {"type": "plane", "pts": ["A", "B", "C", "D"]},
        "Plane_PDC": {"type": "plane", "pts": ["P", "D", "C"]},
        "Plane_PAB": {"type": "plane", "pts": ["P", "A", "B"]},
        "Plane_PApBp": {"type": "plane", "pts": ["P", "Ap", "Bp"]},
        "Plane_ApBpCD": {"type": "plane", "pts": ["Ap", "Bp", "D", "C"]},
    },
    ans=ans,
    scale=scale,
)
