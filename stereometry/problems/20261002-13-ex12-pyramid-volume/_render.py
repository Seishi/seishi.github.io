#!/usr/bin/env python3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _kit import cam, centroid, emit
import sympy as sp
import geometry_kernel as gk
import bodies

h = 2 * sp.sqrt(33) / 3
Rb = 4 * sp.sqrt(3) / 3
A = gk.V(Rb, 0, 0)
B = gk.V(-Rb / 2, Rb * sp.sqrt(3) / 2, 0)
C = gk.V(-Rb / 2, -Rb * sp.sqrt(3) / 2, 0)
S = gk.V(0, 0, h)
Ap = gk.simplify_vec((S + A) / 2)
Bp = gk.simplify_vec((S + B) / 2)
Cp = gk.simplify_vec((S + C) / 2)
Dpt = gk.simplify_vec((Ap + Bp) / 2)
# circumcenter of S,A,B,C'  (C' = Cp)
u, v, w = A - S, B - S, Cp - S
from sympy import Matrix
M = Matrix([[2 * u[0], 2 * u[1], 2 * u[2]],
            [2 * v[0], 2 * v[1], 2 * v[2]],
            [2 * w[0], 2 * w[1], 2 * w[2]]])
rhs = Matrix([u.dot(u), v.dot(v), w.dot(w)])
O = S + M.inv() * rhs
O = gk.V(*[sp.simplify(O[i]) for i in range(3)])
ans = gk.tex(8 * sp.sqrt(11) / 3)
pts = {"A": A, "B": B, "C": C, "S": S, "Ap": Ap, "Bp": Bp, "Cp": Cp, "D": Dpt, "O": O}
scale = 0.7
tp = gk.to_three(pts, scale=scale)
center = centroid(tp)
topo = bodies.tri_pyramid("S", ("A", "B", "C"))

def c(d):
    return cam(tp, center, d)

mp = {k: gk.tex_vec(pts[k]) for k in ("A", "S", "O", "D")}
emit(
    HERE,
    lesson={
        "language": "zh-CN",
        "meta": "交互解题 · 体积",
        "title": (
            r"正三棱锥 $S$-$ABC$ 中，底边长为 $4$，$SA$、$SB$、$SC$ 的中点分别为 $A'、B'、C'$，"
            r"$A'B'$ 的中点为 $D$。若三棱锥 $S$-$ABC'$ 的外接球球心为 $O$，满足 $OC^{2}-OD^{2}=AB^{2}$，"
            r"则三棱锥 $S$-$ABC$ 的体积为"
        ),
        "answerLabel": r"三棱锥 $S$-$ABC$ 的体积",
        "answerValue": f"${ans}$",
    },
    steps=[
        {
            "title": "正三棱锥建系",
            "content": (
                r"<p>底面 $ABC$ 在 $z=0$，中心为原点，边长 $4$，外接半径 $\dfrac{4\sqrt{3}}{3}$，"
                r"顶点 $S=(0,0,h)$，$h>0$。</p>"
                r"<p>$A'、B'、C'$ 分别为 $SA、SB、SC$ 中点，$D$ 为 $A'B'$ 中点。</p>"
            ),
            "highlight": ["Axis", "Plane_ABC", "Point_S", "Len_AB", "Point_Ap", "Point_Bp",
                          "Point_Cp", "Point_D"],
            "cameraPos": c([7, 6, 5]),
        },
        {
            "title": "$S$-$ABC'$ 的外接球心",
            "content": (
                r"<p>$O$ 到 $S$、$A$、$B$、$C'$ 等距。以 $S$ 为基点解线性方程组，得 $O$ 的坐标"
                r"（含参数 $h$）。再写 $OC^{2}-OD^{2}=16$。</p>"
            ),
            "highlight": ["Point_O", "Sphere_circ", "Point_S", "Point_A", "Point_B",
                          "Point_Cp", "Point_C", "Point_D"],
            "cameraPos": c([5, 6, 4]),
        },
        {
            "title": "解出高并求体积",
            "content": (
                r"<p>化简后方程成为 $\dfrac{3}{4}h^{2}-11=0$，正根</p>"
                r"$$h=\dfrac{2\sqrt{33}}{3}.$$"
                r"<p>底面积 $4\sqrt{3}$，体积 $V=\dfrac{1}{3}\cdot 4\sqrt{3}\cdot h=" + ans + r"$。</p>"
            ),
            "highlight": ["Point_S", "Plane_ABC", "Len_AB", "Point_O"],
            "cameraPos": c([6, 5, 5]),
        },
    ],
    pts=pts,
    topo=topo,
    extra_edges=[
        {"a": "Ap", "b": "Bp", "color": "aux", "dashed": True},
        {"a": "O", "b": "C", "color": "aux", "dashed": True},
        {"a": "O", "b": "D", "color": "aux", "dashed": True},
    ],
    extra_spheres=["Ap", "Bp", "Cp", "D", "O"],
    elements={
        "Axis": {"type": "axes", "size": 4},
        "Point_S": {"type": "point", "center": "S"},
        "Point_A": {"type": "point", "center": "A"},
        "Point_B": {"type": "point", "center": "B"},
        "Point_C": {"type": "point", "center": "C"},
        "Point_Ap": {"type": "point", "center": "Ap"},
        "Point_Bp": {"type": "point", "center": "Bp"},
        "Point_Cp": {"type": "point", "center": "Cp"},
        "Point_D": {"type": "point", "center": "D"},
        "Point_O": {"type": "point", "center": "O"},
        "Len_AB": {"type": "measure", "a": "A", "b": "B", "label": "4"},
        "Plane_ABC": {"type": "plane", "pts": ["A", "B", "C"]},
        "Sphere_circ": {
            "type": "sphere", "center": "O",
            "radius": float(sp.N((O - S).norm() * scale)),
            "opacity": 0.1,
        },
    },
    ans=ans,
    scale=scale,
)
