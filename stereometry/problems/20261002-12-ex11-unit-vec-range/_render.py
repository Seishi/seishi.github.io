#!/usr/bin/env python3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _kit import cam, centroid, emit
import sympy as sp
import geometry_kernel as gk
import bodies

# Four unit vectors, adjacent angle 60°, diagonals 90° (p=q=0), s=4
O = gk.V(0, 0, 0)
P1 = gk.V(1, 0, 0)
P2 = gk.V(sp.Rational(1, 2), sp.sqrt(3) / 2, 0)
# w · v = 1/2, |w|=1, p=u·w=0 so w1=0
# w1 + w2√3 = 1 from w·v=1/2: (1/2)w1+(√3/2)w2=1/2 => w1+√3 w2=1
# w1=0 => w2=1/√3, w3²=1-1/3=2/3
P3 = gk.V(0, 1 / sp.sqrt(3), sp.sqrt(sp.Rational(2, 3)))
# x1=1/2 (u·x=1/2), x·w=1/2, |x|=1
# (1/2)*0 + x2/√3 + x3 √(2/3) = 1/2
# x2²+x3²=3/4
# This is solvable; pick a concrete solution.
# From earlier: q=v·x= 1/2 * x1 + √3/2 * x2 = 1/4 + √3/2 x2 =0 => x2=-1/(2√3)
# then x2/√3 + x3√(2/3)=1/2
# -1/(2√3)/√3 + x3√(2/3)=1/2
# -1/6 + x3√(2/3)=1/2
# x3√(2/3)=2/3
# x3= (2/3)/√(2/3)=(2/3)√(3/2)=√6 / 3
# check x2²+x3²=1/12 + 6/9=1/12+2/3=1/12+8/12=9/12=3/4. Good.
P4 = gk.V(sp.Rational(1, 2), -1 / (2 * sp.sqrt(3)), sp.sqrt(6) / 3)
# 逼近下端：p=3/4, q=-3/7，菱形更扁，|P1P3|²+|P2P4|²=47/14
p_lo = sp.Rational(3, 4)
q_lo = -p_lo / (p_lo + 1)
Q1 = gk.V(1, 0, 0)
Q2 = gk.V(sp.Rational(1, 2), sp.sqrt(3) / 2, 0)
q3x = p_lo
q3y = (1 - q3x) / sp.sqrt(3)
q3z = sp.sqrt(sp.simplify(1 - q3x ** 2 - q3y ** 2))
Q3 = gk.V(q3x, q3y, q3z)
q4x = sp.Rational(1, 2)
# Q2·Q4 = q_lo：1/4 + (√3/2) q4y = q_lo
q4y = 2 * (q_lo - sp.Rational(1, 4)) / sp.sqrt(3)
# Q3·Q4=1/2 用来求 q4z 的符号与大小
# q3x q4x + q3y q4y + q3z q4z = 1/2
q4z = (sp.Rational(1, 2) - q3x * q4x - q3y * q4y) / q3z
Q4 = gk.V(q4x, q4y, q4z)
pts = {
    "O": O, "P1": P1, "P2": P2, "P3": P3, "P4": P4,
    "Q1": Q1, "Q2": Q2, "Q3": Q3, "Q4": Q4,
}
ans = r"(3,4]"
scale = 2.2
tp = gk.to_three(pts, scale=scale)
center = centroid(tp)
topo = {
    "spheres": ["O", "P1", "P2", "P3", "P4", "Q1", "Q2", "Q3", "Q4"],
    "edges": [
        {"a": "O", "b": "P1"}, {"a": "O", "b": "P2"},
        {"a": "O", "b": "P3"}, {"a": "O", "b": "P4"},
        {"a": "P1", "b": "P2"}, {"a": "P2", "b": "P3"},
        {"a": "P3", "b": "P4"}, {"a": "P4", "b": "P1"},
        {"a": "Q1", "b": "Q2", "dashed": True, "color": "aux"},
        {"a": "Q2", "b": "Q3", "dashed": True, "color": "aux"},
        {"a": "Q3", "b": "Q4", "dashed": True, "color": "aux"},
        {"a": "Q4", "b": "Q1", "dashed": True, "color": "aux"},
        {"a": "O", "b": "Q1", "dashed": True, "color": "aux"},
        {"a": "O", "b": "Q2", "dashed": True, "color": "aux"},
        {"a": "O", "b": "Q3", "dashed": True, "color": "aux"},
        {"a": "O", "b": "Q4", "dashed": True, "color": "aux"},
    ],
}

def c(d):
    return cam(tp, center, d)

emit(
    HERE,
    lesson={
        "language": "zh-CN",
        "meta": "交互解题 · 取值范围",
        "title": (
            r"若互不相等的单位空间向量 $\overrightarrow{OP_i}\ (i=1,2,3,4)$ 满足 "
            r"$|P_1P_2|=|P_2P_3|=|P_3P_4|=|P_4P_1|=1$，则 "
            r"$|P_1P_3|^{2}+|P_2P_4|^{2}$ 的取值范围是"
        ),
        "answerLabel": r"$|P_1P_3|^{2}+|P_2P_4|^{2}$ 的取值范围",
        "answerValue": r"$(3,4]$",
    },
    steps=[
        {
            "title": "化成单位向量的内积",
            "content": (
                r"<p>$|\overrightarrow{OP_i}|=1$，且相邻弦长为 $1$，故</p>"
                r"$$|P_iP_{i+1}|^{2}=2-2\,\overrightarrow{OP_i}\cdot\overrightarrow{OP_{i+1}}=1"
                r"\implies \overrightarrow{OP_i}\cdot\overrightarrow{OP_{i+1}}=\dfrac{1}{2}.$$"
                r"<p>记 $p=\overrightarrow{OP_1}\cdot\overrightarrow{OP_3}$，"
                r"$q=\overrightarrow{OP_2}\cdot\overrightarrow{OP_4}$，则</p>"
                r"$$|P_1P_3|^{2}+|P_2P_4|^{2}=4-2(p+q).$$"
            ),
            "highlight": ["Axis", "Sphere_unit", "Point_P1", "Point_P2", "Point_P3", "Point_P4",
                          "Line_P1P2"],
            "cameraPos": c([6, 5, 6]),
        },
        {
            "title": r"Gram 矩阵半正定且秩 $\le 3$",
            "content": (
                r"<p>四个单位向量的 Gram 矩阵主对角为 $1$，相邻为 $\dfrac{1}{2}$，对角为 $p,q$。"
                r"它必须半正定且行列式为 $0$（四向量在三维空间）。</p>"
                r"<p>$\det G=0$ 给出 $(p-1)(q-1)(pq+p+q)=0$。向量互不相等排除 $p=1$ 或 $q=1$，故</p>"
                r"$$q=-\dfrac{p}{p+1}.$$"
            ),
            "highlight": ["Point_P1", "Point_P2", "Point_P3", "Point_P4", "Line_P1P3", "Line_P2P4"],
            "cameraPos": c([5, 6, 4]),
        },
        {
            "title": r"情形：取到上端 $4$",
            "content": (
                r"<p>$3\times 3$ 主子式非负推出 $p,q\in\left[-\dfrac{1}{2},1\right)$。"
                r"再代 $q=-\dfrac{p}{p+1}$，得 $p\in\left(-\dfrac{1}{2},1\right)$，从而</p>"
                r"$$4-2(p+q)=4-\dfrac{2p^{2}}{p+1}.$$"
                r"<p>$p=q=0$ 时取到 $4$。图中实线球面菱形 $P_1P_2P_3P_4$ 对角互相垂直，就是这一款。</p>"
            ),
            "highlight": ["Line_P1P3", "Line_P2P4", "Point_P1", "Point_P2", "Point_P3", "Point_P4",
                          "Sphere_unit"],
            "cameraPos": c([6, 4, 5]),
        },
        {
            "title": r"情形：逼近下端 $3$",
            "content": (
                r"<p>当 $p\to 1^{-}$ 或 $p\to-\dfrac{1}{2}^{+}$ 时，$4-\dfrac{2p^{2}}{p+1}\to 3$，"
                r"但取不到（向量互不相等）。图中虚线 $Q_1Q_2Q_3Q_4$ 取 $p=\dfrac{3}{4}$，"
                r"目标值为 $\dfrac{47}{14}$，已经明显比实线菱形更扁。</p>"
                r"<p>因此 $|P_1P_3|^{2}+|P_2P_4|^{2}$ 的取值范围是 $(3,4]$。</p>"
            ),
            "highlight": ["Line_Q1Q3", "Line_Q2Q4", "Point_Q1", "Point_Q2", "Point_Q3", "Point_Q4",
                          "Sphere_unit"],
            "cameraPos": c([5, 6, 4]),
        },
    ],
    pts=pts,
    topo=topo,
    extra_edges=[
        {"a": "P1", "b": "P3", "color": "aux", "dashed": True},
        {"a": "P2", "b": "P4", "color": "aux", "dashed": True},
        {"a": "Q1", "b": "Q3", "color": "aux", "dashed": True},
        {"a": "Q2", "b": "Q4", "color": "aux", "dashed": True},
    ],
    elements={
        "Axis": {"type": "axes", "size": 2.2},
        "Point_P1": {"type": "point", "center": "P1"},
        "Point_P2": {"type": "point", "center": "P2"},
        "Point_P3": {"type": "point", "center": "P3"},
        "Point_P4": {"type": "point", "center": "P4"},
        "Point_Q1": {"type": "point", "center": "Q1"},
        "Point_Q2": {"type": "point", "center": "Q2"},
        "Point_Q3": {"type": "point", "center": "Q3"},
        "Point_Q4": {"type": "point", "center": "Q4"},
        "Line_P1P2": {"type": "line", "a": "P1", "b": "P2", "color": "emphasis", "depthTest": False},
        "Line_P1P3": {"type": "line", "a": "P1", "b": "P3", "color": "emphasis", "depthTest": False},
        "Line_P2P4": {"type": "line", "a": "P2", "b": "P4", "color": "emphasis", "depthTest": False},
        "Line_Q1Q3": {"type": "line", "a": "Q1", "b": "Q3", "color": "emphasis", "depthTest": False},
        "Line_Q2Q4": {"type": "line", "a": "Q2", "b": "Q4", "color": "emphasis", "depthTest": False},
        "Sphere_unit": {"type": "sphere", "center": "O", "radius": 1 * scale, "opacity": 0.1},
    },
    ans=ans,
    scale=scale,
)
