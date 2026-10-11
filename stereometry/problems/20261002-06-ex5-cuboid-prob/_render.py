#!/usr/bin/env python3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _kit import cam, centroid, emit
import sympy as sp
import geometry_kernel as gk
import bodies

pts = gk.cuboid(5, 5, 1)
pts["M"] = gk.V(2, 0, 0)
# a sample interior point of the event region, x=3, g=4*3-2-2sqrt(10)=10-2*3.16=3.67, y=1
pts["P"] = gk.V(3, 1, 0)
# foot from P to A1D1: (0,1,1)
pts["H"] = gk.V(0, 1, 1)
ans = r"\dfrac{S}{25}"
scale = 1.1
tp = gk.to_three(pts, scale=scale)
center = centroid(tp)
topo = bodies.cuboid()

def c(d):
    return cam(tp, center, d)

emit(
    HERE,
    lesson={
        "language": "zh-CN",
        "meta": "交互解题 · 几何概型",
        "title": (
            r"长方体 $ABCD$-$A_1B_1C_1D_1$ 中，$AB=AD=5$，$AA_1=1$，点 $M$ 满足 "
            r"$3\overrightarrow{AM}+2\overrightarrow{BM}=\vec 0$。在正方形 $ABCD$ 内随机取点 $P$，"
            r"$P$ 到直线 $A_1D_1$ 的距离为 $d_1$，$PM$ 长为 $d_2$，"
            r"求事件 $d_1-d_2\ge 1$ 的概率"
        ),
        "answerLabel": r"事件 $d_1-d_2\ge 1$ 的概率",
        "answerValue": r"$\dfrac{S}{25}$",
    },
    steps=[
        {
            "title": "建系并定位 $M$",
            "content": (
                r"<p>$A$ 为原点，$AB$、$AD$、$AA_1$ 沿坐标轴，正方形边长 $5$，高 $1$。</p>"
                r"<p>$3(M-A)+2(M-B)=\vec 0$ 得 $5M=3A+2B$，故 $M$ 在 $AB$ 上且 $AM=2$：</p>"
                r"$$M(2,0,0),\quad A_1D_1:\ (0,t,1).$$"
            ),
            "highlight": ["Axis", "Plane_ABCD", "Point_M", "Line_A1D1", "Len_AB", "Len_AA1"],
            "cameraPos": c([8, 5, 6]),
        },
        {
            "title": "把事件写成平面区域",
            "content": (
                r"<p>设 $P=(x,y,0)$，$0\le x,y\le 5$。则</p>"
                r"$$d_1=\sqrt{x^{2}+1},\qquad d_2=\sqrt{(x-2)^{2}+y^{2}}.$$"
                r"<p>不等式 $d_1-d_2\ge 1$ 等价于 $d_2\le \sqrt{x^{2}+1}-1$（右边非负）。"
                r"两边平方并整理：</p>"
                r"$$y^{2}\le 4x-2-2\sqrt{x^{2}+1}.$$"
            ),
            "highlight": ["Point_P", "Point_M", "Point_H", "Line_A1D1", "Line_PM",
                          "Len_d1", "Plane_ABCD"],
            "cameraPos": c([7, 6, 3]),
        },
        {
            "title": "确定 $x$ 的范围并求面积",
            "content": (
                r"<p>右边 $\ge 0$ 当且仅当 $x\ge \dfrac{4}{3}$。"
                r"在 $[4/3,5]$ 上 $\sqrt{4x-2-2\sqrt{x^{2}+1}}<5$，故 $y$ 从 $0$ 积到该根式即可。</p>"
                r"<p>有利区域面积</p>"
                r"$$S=\int_{4/3}^{5}\sqrt{4x-2-2\sqrt{x^{2}+1}}\,\mathrm{d}x,$$"
                r"<p>样本空间是边长 $5$ 的正方形，面积 $25$。所求概率为 $\dfrac{S}{25}$。</p>"
            ),
            "highlight": ["Plane_ABCD", "Point_P", "Point_M", "Line_PM"],
            "cameraPos": c([6, 7, 5]),
        },
    ],
    pts=pts,
    topo=topo,
    extra_edges=[
        {"a": "P", "b": "M", "color": "aux", "dashed": True},
        {"a": "P", "b": "H", "color": "aux", "dashed": True},
    ],
    extra_spheres=["M", "P", "H"],
    elements={
        "Axis": {"type": "axes", "size": 4},
        "Point_M": {"type": "point", "center": "M"},
        "Point_P": {"type": "point", "center": "P"},
        "Point_H": {"type": "point", "center": "H"},
        "Line_A1D1": {"type": "line", "a": "A1", "b": "D1", "color": "emphasis", "depthTest": False},
        "Line_PM": {"type": "line", "a": "P", "b": "M", "color": "emphasis", "depthTest": False},
        "Len_AB": {"type": "measure", "a": "A", "b": "B", "label": "5"},
        "Len_AA1": {"type": "measure", "a": "A", "b": "A1", "label": "1"},
        "Len_d1": {"type": "measure", "a": "P", "b": "H", "label": r"d_1"},
        "Plane_ABCD": {"type": "plane", "pts": ["A", "B", "C", "D"]},
    },
    ans=ans,
    scale=scale,
)
