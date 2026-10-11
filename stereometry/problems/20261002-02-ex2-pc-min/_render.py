#!/usr/bin/env python3
"""Escape hatch: PC 最小值不是 5 类 query，用 kernel 精确算完再注入模板。"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "engine" / "lib"), str(ROOT / "engine" / "scripts")]

import sympy as sp
import geometry_kernel as gk
import bodies
from generate import render_html
from validate import validate, fit_camera

s2 = (95 - 7 * sp.sqrt(57)) / 38
s = sp.sqrt(s2)
h = sp.sqrt(1 - s2 / 4)
rho = sp.sqrt(2 * (s2 - 1))
pc = sp.sqrt(3 * (9 - sp.sqrt(57)) / 8)
ans = gk.tex(pc)

A = gk.V(-sp.sqrt(3), 0, 0)
B = gk.V(sp.sqrt(3), 0, 0)
F = gk.V(s, 0, 0)
C = gk.V(s, rho, 0)
P = gk.V(s, h / 2, h * sp.sqrt(3) / 2)
assert sp.simplify(C[2]) == 0 and bool(sp.simplify(P[2]).is_positive)
pts = {"A": A, "B": B, "C": C, "P": P, "F": F}

scale = 2.0
tp = gk.to_three(pts, scale=scale)
topo = bodies.tri_pyramid("P", ("A", "B", "C"))
topo["spheres"] = ["A", "B", "C", "P", "F"]
center = [sum(tp[k][i] for k in tp) / len(tp) for i in range(3)]

def cam(direction):
    x, y, z = fit_camera(tp, center, direction)
    return {"x": round(x, 2), "y": round(y, 2), "z": round(z, 2)}

mp = {k: gk.tex_vec(v) for k, v in pts.items()}

data = {
    "lesson": {
        "language": "zh-CN",
        "meta": "交互解题 · 最短距离",
        "title": (
            "三棱锥 $P$-$ABC$ 满足 $AB=2\\sqrt{3}$，二面角 $P$-$AB$-$C=\\dfrac{\\pi}{3}$，"
            "已知 $PC\\perp AB$，$PA+PB=4$，$CA-CB=2$，求 $PC$ 长度的最小值"
        ),
        "answerLabel": "$PC$ 长度的最小值",
        "answerValue": f"${ans}$",
    },
    "steps": [
        {
            "title": "建系并把条件翻译成轨迹",
            "content": (
                r"<p>把底面 $ABC$ 放在水平面 $z=0$，以 $AB$ 为 $x$ 轴、中点为原点：</p>"
                r"$$A" + mp["A"] + r",\quad B" + mp["B"] + r",\quad AB=2\sqrt{3}.$$"
                r"<p>$PC\perp AB$，故 $P$、$C$ 横坐标同为 $s$。$C$ 在底面 $z=0$ 上，"
                r"$P$ 在 $z>0$。$P$、$C$ 到 $AB$ 的垂足同为 $F(s,0,0)$。</p>"
                r"<p>$A$、$B$ 为焦点，$PA+PB=4$，故 $P$ 在以 $AB$ 为轴的旋转椭圆上：</p>"
                r"$$\dfrac{s^2}{4}+d_P^2=1\quad(|s|<2).$$"
                r"<p>$CA-CB=2$，故 $C$ 在以 $A$、$B$ 为焦点、靠近 $B$ 的双曲线上：</p>"
                r"$$s^2-\dfrac{d_C^2}{2}=1\quad(s>1).$$"
                r"<p>两轨迹同时成立要求 $s\in(1,2]$。</p>"
            ),
            "highlight": [
                "Axis", "Len_AB", "Plane_ABC", "Line_PC",
                "Point_F", "Point_P", "Point_C",
            ],
            "cameraPos": cam([6, 5, 7]),
        },
        {
            "title": "二面角化为垂面内的夹角",
            "content": (
                r"<p>垂直于棱 $AB$ 的平面上，二面角 $P$-$AB$-$C$ 等于 $\angle PFC=\dfrac{\pi}{3}$。</p>"
                r"<p>在 $\triangle PFC$ 中，$PF=d_P$，$CF=d_C$，$\angle PFC=\dfrac{\pi}{3}$，余弦定理得</p>"
                r"$$PC^2=d_P^2+d_C^2-d_P d_C.$$"
                r"<p>把椭圆、双曲线代入：</p>"
                r"$$d_P=\sqrt{1-\dfrac{s^2}{4}},\qquad d_C=\sqrt{2(s^2-1)},$$"
                r"$$PC^2=\dfrac{7}{4}s^2-1-\dfrac{\sqrt{2}}{2}\sqrt{4-s^2}\sqrt{s^2-1}.$$"
            ),
            "highlight": [
                "Plane_PAB", "Plane_CAB", "Plane_PFC", "Line_PC",
                "Point_F", "Point_P", "Point_C", "Len_PF", "Len_CF",
            ],
            "cameraPos": cam([8, 3, 2]),
        },
        {
            "title": "对参数 $s$ 求最小值",
            "content": (
                r"<p>令 $f(s)=PC^2$，$s\in(1,2]$。求导并令 $f'(s)=0$，得唯一驻点</p>"
                r"$$s^2=\dfrac{95-7\sqrt{57}}{38}\in(1,4).$$"
                r"<p>该点满足 $7\,d_P d_C=5-2s^2$。代回 $f(s)$ 并化简：</p>"
                r"$$PC^2=\dfrac{3(9-\sqrt{57})}{8}.$$"
                r"<p>端点处：$s\to 1^+$ 时四面体退化；$s=2$ 时 $PC=\sqrt{6}$ 更大。故驻点给出最小值。</p>"
                r"<p>因此 $PC_{\min}=\sqrt{\dfrac{3(9-\sqrt{57})}{8}}=" + ans + r"$。</p>"
            ),
            "highlight": ["Line_PC", "Point_P", "Point_C", "Point_F", "Len_PF", "Len_CF"],
            "cameraPos": cam([5, 6, 5]),
        },
    ],
    "model": {
        "scale": scale,
        "target": center,
        "initialCamera": fit_camera(tp, center, [6, 5, 7]),
        "points": tp,
        "spheres": topo["spheres"],
        "edges": topo["edges"] + [
            {"a": "P", "b": "F", "color": "aux", "dashed": True},
            {"a": "C", "b": "F", "color": "aux", "dashed": True},
        ],
        "elements": {
            "Axis": {"type": "axes", "size": 3.2},
            "Point_F": {"type": "point", "center": "F"},
            "Point_P": {"type": "point", "center": "P"},
            "Point_C": {"type": "point", "center": "C"},
            "Line_PC": {"type": "line", "a": "P", "b": "C", "color": "emphasis", "depthTest": False},
            "Plane_ABC": {"type": "plane", "pts": ["A", "B", "C"]},
            "Plane_PAB": {"type": "plane", "pts": ["P", "A", "B"]},
            "Plane_CAB": {"type": "plane", "pts": ["C", "A", "B"]},
            "Plane_PFC": {"type": "plane", "pts": ["P", "F", "C"]},
            "Len_AB": {"type": "measure", "a": "A", "b": "B", "label": r"2\sqrt{3}"},
            "Len_PF": {"type": "measure", "a": "P", "b": "F", "label": r"d_P"},
            "Len_CF": {"type": "measure", "a": "C", "b": "F", "label": r"d_C"},
        },
    },
}

here = Path(__file__).resolve().parent
spec_doc = {
    "spec": {
        "language": "zh-CN",
        "body": "custom",
        "scale": scale,
        "points": {
            "A": [str(-sp.sqrt(3)), 0, 0],
            "B": [str(sp.sqrt(3)), 0, 0],
            "F": [str(s), 0, 0],
            "C": [str(s), str(rho), 0],
            "P": [str(s), str(h / 2), str(h * sp.sqrt(3) / 2)],
        },
        "topo": topo,
        "lengths": {"AB": ["A", "B"], "PC": ["P", "C"]},
        "query": {"type": "point_plane_distance", "point": "P", "plane": ["A", "B", "C"]},
        "_note": "所求是 PC 最小值，不属于 5 类 query；index.html 由本脚本按精确最小值渲染，query 仅作存档。",
    },
    "lesson": data["lesson"],
    "steps": data["steps"],
    "model": {"elements": data["model"]["elements"]},
    "_answer": ans,
}
(here / "problem.json").write_text(
    json.dumps(spec_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

errs = validate(data, answer=ans)
if errs:
    print("FAIL")
    for e in errs:
        print(" -", e)
    sys.exit(1)

out = here / "index.html"
render_html(data, out)
print(f"PASS  已生成: {out}  (答案 {ans})")
