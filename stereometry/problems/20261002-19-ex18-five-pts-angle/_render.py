#!/usr/bin/env python3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _kit import cam, centroid, emit
import sympy as sp
import geometry_kernel as gk

A = gk.V(0, 0, 0)
B = gk.V(1, 0, 0)
C = gk.V(1, 1, 0)
D = gk.V(sp.Rational(1, 2), 1, sp.sqrt(3) / 2)
E = gk.V(sp.Rational(1, 2), 0, sp.sqrt(3) / 2)
E2 = gk.V(sp.Rational(-5, 14), sp.Rational(6, 7), 3 * sp.sqrt(3) / 14)
ans = r"60^{\circ}"
pts = {"A": A, "B": B, "C": C, "D": D, "E": E, "E2": E2}
scale = 2.4
tp = gk.to_three(pts, scale=scale)
center = centroid(tp)
topo = {
    "spheres": ["A", "B", "C", "D", "E", "E2"],
    "edges": [
        {"a": "A", "b": "B"}, {"a": "B", "b": "C"}, {"a": "C", "b": "D"},
        {"a": "D", "b": "E"}, {"a": "E", "b": "A"},
        {"a": "D", "b": "E2", "dashed": True, "color": "aux"},
        {"a": "E2", "b": "A", "dashed": True, "color": "aux"},
    ],
}

def c(d):
    return cam(tp, center, d)

emit(
    HERE,
    lesson={
        "language": "zh-CN",
        "meta": "交互解题 · 空间折线",
        "title": (
            r"已知空间中五个点 $A,B,C,D,E$ 满足 $AB=BC=CD=DE=EA$，且 "
            r"$\angle ABC,\angle BCD,\angle CDE,\angle DEA,\angle EAB$ 中有四个是直角，"
            r"求最后一个角的所有可能大小"
        ),
        "answerLabel": r"最后一个角的可能大小",
    },
    answers=[
        {"label": r"情形一", "value": r"$60^{\circ}$"},
        {"label": r"情形二", "value": r"$\arccos\left(-\dfrac{5}{14}\right)$"},
    ],
    steps=[
        {
            "title": "折成单位向量链",
            "content": (
                r"<p>令 $\vec v_1=\overrightarrow{AB},\ldots,\vec v_5=\overrightarrow{EA}$，则 $|\vec v_i|=1$ 且 "
                r"$\vec v_1+\cdots+\vec v_5=\vec 0$。</p>"
                r"<p>顶点角为 $90^{\circ}$ 当且仅当相邻向量垂直：$\vec v_i\cdot\vec v_{i+1}=0$。"
                r"四个直角意味着五个相邻对里恰有四对垂直。</p>"
            ),
            "highlight": ["Axis", "Point_A", "Point_B", "Point_C", "Point_D", "Point_E",
                          "Line_AB", "Line_BC"],
            "cameraPos": c([6, 5, 6]),
        },
        {
            "title": r"情形一：最后一个角为 $60^{\circ}$",
            "content": (
                r"<p>不妨设 $\vec v_1=(1,0,0)$，$\vec v_2=(0,1,0)$，后面三个单位向量依次垂直。"
                r"其中一解把 $E$ 送到 $\bigl(\dfrac{1}{2},0,\dfrac{\sqrt{3}}{2}\bigr)$，"
                r"折线 $ABCDE$ 如图中实线。</p>"
                r"<p>$\angle EAB$ 满足 $\cos\angle EAB=\overrightarrow{AE}\cdot\overrightarrow{AB}=\dfrac{1}{2}$，"
                r"故最后一个角为 $60^{\circ}$。</p>"
            ),
            "highlight": ["Point_A", "Point_B", "Point_C", "Point_D", "Point_E",
                          "Line_AB", "Line_BC", "Line_CD", "Line_DE", "Line_EA",
                          "Plane_EAB"],
            "cameraPos": c([5, 6, 4]),
        },
        {
            "title": r"情形二：最后一个角为 $\arccos\bigl(-\dfrac{5}{14}\bigr)$",
            "content": (
                r"<p>另一解共用折线 $ABCD$，把 $E$ 换到 "
                r"$E'\bigl(-\dfrac{5}{14},\dfrac{6}{7},\dfrac{3\sqrt{3}}{14}\bigr)$（图中虚线）。</p>"
                r"<p>$\cos\angle E'AB=-\dfrac{5}{14}$。两种本质不同的构型给出最后一个角的所有可能："
                r"$60^{\circ}$ 或 $\arccos\left(-\dfrac{5}{14}\right)$。</p>"
            ),
            "highlight": ["Point_A", "Point_B", "Point_C", "Point_D", "Point_E2",
                          "Line_AB", "Line_BC", "Line_CD", "Line_DE2", "Line_E2A",
                          "Plane_E2AB"],
            "cameraPos": c([4, 7, 5]),
        },
    ],
    pts=pts,
    topo=topo,
    elements={
        "Axis": {"type": "axes", "size": 2},
        "Point_A": {"type": "point", "center": "A"},
        "Point_B": {"type": "point", "center": "B"},
        "Point_C": {"type": "point", "center": "C"},
        "Point_D": {"type": "point", "center": "D"},
        "Point_E": {"type": "point", "center": "E"},
        "Point_E2": {"type": "point", "center": "E2"},
        "Line_AB": {"type": "line", "a": "A", "b": "B", "color": "emphasis", "depthTest": False},
        "Line_BC": {"type": "line", "a": "B", "b": "C", "color": "emphasis", "depthTest": False},
        "Line_CD": {"type": "line", "a": "C", "b": "D", "color": "emphasis", "depthTest": False},
        "Line_DE": {"type": "line", "a": "D", "b": "E", "color": "emphasis", "depthTest": False},
        "Line_EA": {"type": "line", "a": "E", "b": "A", "color": "emphasis", "depthTest": False},
        "Line_DE2": {"type": "line", "a": "D", "b": "E2", "color": "emphasis", "depthTest": False},
        "Line_E2A": {"type": "line", "a": "E2", "b": "A", "color": "emphasis", "depthTest": False},
        "Plane_ABC": {"type": "plane", "pts": ["A", "B", "C"]},
        "Plane_EAB": {"type": "plane", "pts": ["E", "A", "B"]},
        "Plane_E2AB": {"type": "plane", "pts": ["E2", "A", "B"]},
    },
    ans=ans,
    scale=scale,
)
