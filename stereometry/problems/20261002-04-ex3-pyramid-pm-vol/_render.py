#!/usr/bin/env python3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _kit import cam, centroid, emit
import sympy as sp
import geometry_kernel as gk
import bodies

rt = sp.sqrt(10)
A = gk.V(0, 0, 0)
B = gk.V(rt, 0, 0)
D = gk.V(0, rt, 0)
C = gk.V(3 * rt / 2, 3 * rt / 2, 0)
P = gk.V(33 * rt / 25, 24 * rt / 25, sp.Rational(12, 5))
kk = -33 * rt / 131 + 25 * sp.sqrt(30) / 131
Pz, Px, Bx = P[2], P[0], B[0]
lam = (Pz - kk * Px) / (Pz - kk * Px + kk * Bx)
M = gk.simplify_vec((1 - lam) * P + lam * B)
# plane z = k x also meets PC
mu = Pz / (Pz - kk * (P[0] - C[0]))  # (1-mu)P+mu C, z=k x
# (1-s) Pz = k ((1-s) Px + s Cx)
s_pc = (Pz - kk * Px) / (Pz - kk * Px + kk * C[0])
Npt = gk.simplify_vec((1 - s_pc) * P + s_pc * C)
Q = gk.simplify_vec((M + Npt) / 2)
ans = gk.tex(2 * sp.sqrt(3))

pts = {"A": A, "B": B, "C": C, "D": D, "P": P, "M": M, "Q": Q, "N": Npt}
scale = 1.15
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
        "meta": "交互解题 · 体积比与线段比",
        "title": (
            r"四棱锥 $P$-$ABCD$ 中，$AB=AD=\sqrt{10}$，$CB=CD=5$，$\angle BAD=90^{\circ}$，"
            r"$PB=4$，$PC=3$。点 $Q$ 为 $\triangle PBC$ 内部任一点，平面 $QAD$ 与 $PB$ 交于 $M$。"
            r"记四面体 $ACDQ$、$ADPQ$ 的体积分别为 $V_1$、$V_2$，求 "
            r"$\dfrac{|PM|}{|BM|}+\dfrac{2V_1}{V_2}$ 的最小值"
        ),
        "answerLabel": r"$\dfrac{|PM|}{|BM|}+\dfrac{2V_1}{V_2}$ 的最小值",
        "answerValue": f"${ans}$",
    },
    steps=[
        {
            "title": "建系并写出底面坐标",
            "content": (
                r"<p>底面 $ABCD$ 放在 $z=0$：$A$ 为原点，$AB$ 沿 $x$ 轴，$AD$ 沿 $y$ 轴。</p>"
                r"$$A" + mp["A"] + r",\quad B" + mp["B"] + r",\quad D" + mp["D"] + r".$$"
                r"<p>由 $CB=CD=5$ 且 $\angle BAD=90^{\circ}$，得 $C$ 在第一象限：</p>"
                r"$$C" + mp["C"] + r".$$"
                r"<p>$P$ 满足 $PB=4$、$PC=3$、$z>0$，落在两球面交线（圆）上。"
                r"下面的最值与 $P$ 在该圆上的具体位置无关，图中取最高点 $"
                + mp["P"] + r"$。</p>"
            ),
            "highlight": ["Axis", "Plane_ABCD", "Len_AB", "Len_AD", "Len_PB", "Len_PC",
                          "Point_P", "Point_C"],
            "cameraPos": c([7, 5, 6]),
        },
        {
            "title": "过 $AD$ 的平面束",
            "content": (
                r"<p>$AD$ 是 $y$ 轴，过 $AD$ 的平面可写成 $z=kx$（$k>0$）。"
                r"它与 $PB$ 交于 $M$，与平面 $PBC$ 交于过 $M$ 的直线；"
                r"$Q$ 就在这条直线落在 $\triangle PBC$ 内的开线段上。</p>"
                r"<p>因此 $\dfrac{|PM|}{|BM|}$ 只由平面参数 $k$ 决定。"
                r"体积 $V_1=\mathrm{vol}(ACDQ)$、$V_2=\mathrm{vol}(ADPQ)$ 对 $Q$ 的比值"
                r"同样只依赖该平面：以 $A$ 为原点，</p>"
                r"$$\dfrac{V_1}{V_2}=\dfrac{15|k|}{\sqrt{10}\,|P_z-k P_x|}.$$"
            ),
            "highlight": ["Plane_QAD", "Plane_PBC", "Line_PB", "Point_M", "Point_Q",
                          "Point_P", "Point_A", "Point_D"],
            "cameraPos": c([8, 4, 3]),
        },
        {
            "title": "目标函数对 $k$ 求最小值",
            "content": (
                r"<p>令 $\lambda$ 为 $M$ 分 $PB$ 的比例，$M=(1-\lambda)P+\lambda B$，则 "
                r"$\dfrac{|PM|}{|BM|}=\dfrac{\lambda}{1-\lambda}$。"
                r"在使平面穿过 $\triangle PBC$ 内部的 $k$ 范围内，</p>"
                r"$$f(k)=\dfrac{\lambda(k)}{1-\lambda(k)}+\dfrac{30k}{\sqrt{10}\,(P_z-k P_x)}.$$"
                r"<p>求导并令 $f'(k)=0$，得唯一驻点，且 $f=2\sqrt{3}$。"
                r"端点处平面退化为底面或面 $PAC$，函数值更大。换该圆上其它 $P$，驻点值不变。"
                r"最小值为 $" + ans + r"$。</p>"
            ),
            "highlight": ["Line_PB", "Point_M", "Point_Q", "Point_P", "Point_B",
                          "Plane_QAD", "Len_PM"],
            "cameraPos": c([5, 6, 5]),
        },
    ],
    pts=pts,
    topo=topo,
    extra_edges=[
        {"a": "P", "b": "M", "color": "aux", "dashed": True},
        {"a": "M", "b": "Q", "color": "aux", "dashed": True},
        {"a": "Q", "b": "N", "color": "aux", "dashed": True},
    ],
    extra_spheres=["M", "Q", "N"],
    elements={
        "Axis": {"type": "axes", "size": 3.2},
        "Point_P": {"type": "point", "center": "P"},
        "Point_C": {"type": "point", "center": "C"},
        "Point_A": {"type": "point", "center": "A"},
        "Point_D": {"type": "point", "center": "D"},
        "Point_B": {"type": "point", "center": "B"},
        "Point_M": {"type": "point", "center": "M"},
        "Point_Q": {"type": "point", "center": "Q"},
        "Line_PB": {"type": "line", "a": "P", "b": "B", "color": "emphasis", "depthTest": False},
        "Len_AB": {"type": "measure", "a": "A", "b": "B", "label": r"\sqrt{10}"},
        "Len_AD": {"type": "measure", "a": "A", "b": "D", "label": r"\sqrt{10}"},
        "Len_PB": {"type": "measure", "a": "P", "b": "B", "label": "4"},
        "Len_PC": {"type": "measure", "a": "P", "b": "C", "label": "3"},
        "Len_PM": {"type": "measure", "a": "P", "b": "M", "label": r"PM"},
        "Plane_ABCD": {"type": "plane", "pts": ["A", "B", "C", "D"]},
        "Plane_PBC": {"type": "plane", "pts": ["P", "B", "C"]},
        "Plane_QAD": {"type": "plane", "pts": ["Q", "A", "D"]},
        "Plane_ACDQ": {"type": "plane", "pts": ["A", "C", "D"]},
        "Plane_ADPQ": {"type": "plane", "pts": ["A", "D", "P"]},
    },
    ans=ans,
    scale=scale,
)
