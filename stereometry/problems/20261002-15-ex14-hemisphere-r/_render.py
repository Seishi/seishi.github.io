#!/usr/bin/env python3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _kit import cam, centroid, emit
import sympy as sp
import geometry_kernel as gk
import bodies

r2 = sp.Rational(3, 7)
r = sp.sqrt(r2)
d = sp.sqrt(1 - r2)  # sqrt(4/7)
# three poles equally spaced, angular radius α=arcsin r, pole-pole = 2α
# also tangent to equator: poles at colatitude α from north? 
# Equator is the great circle z=0. A small circle tangent to equator:
# the small circle's plane is at distance sqrt(1-r²) from O, and the circle is tangent to z=0 circle.
# The base circle in z=0 has radius 1. Small circle radius r, tangent to it.
# Place poles at z = d, and xy at distance such that they are 120 apart.
# If tangent to equator (great circle in z=0), the angular distance from pole to south... 
# Equator has pole the z-axis. Small circle tangent to equator means |z_pole_angle - π/2| = α, so colatitude = π/2 - α, i.e. pole at z = sin α = r? 
# Pole of small circle: the center of the circle in 3D is d * u_hat, |C|=d=cos α=sqrt(1-r²).
# Tangent to equator: spherical distance between small-circle pole and equator-pole (z-axis) is π/2 - α or π/2+α.
# Angle between u_hat and z-axis = π/2 - α, so u_z = cos(π/2-α)=sin α = r.
# Then |C_z| = d * r? C = d u, C_z = d sin α = sqrt(1-r²)*r.
# Distance from O_xy of C: d cos α wait.
# u_z = r, |u_xy|=sqrt(1-r²)=d.
# C = d u, |C_xy|= d * d = 1-r² = 4/7, C_z = d*r = sqrt(4/7)*sqrt(3/7)=sqrt(12)/7=2√3/7.

cz = 2 * sp.sqrt(3) / 7
rho = sp.Rational(4, 7)
O = gk.V(0, 0, 0)
N = gk.V(0, 0, 1)  # north, unused
# three centers
Cs = []
names = []
for i, name in enumerate(("K1", "K2", "K3")):
    th = 2 * sp.pi * i / 3
    Cs.append(gk.V(rho * sp.cos(th), rho * sp.sin(th), cz))
    names.append(name)
pts = {"O": O, "A": gk.V(1, 0, 0), "B": gk.V(0, 1, 0), "C": gk.V(-1, 0, 0), "D": gk.V(0, -1, 0),
       "Z": gk.V(0, 0, 1)}
for n, v in zip(names, Cs):
    pts[n] = v
ans = gk.tex(sp.sqrt(21) / 7)
scale = 2.4
tp = gk.to_three(pts, scale=scale)
center = centroid(tp)
topo = bodies.round_solid(bottom=("A", "B", "C", "D"), axis=("O", "Z"))

def c(dirc):
    return cam(tp, center, dirc)

emit(
    HERE,
    lesson={
        "language": "zh-CN",
        "meta": "交互解题 · 截面圆半径",
        "title": (
            r"有一个半径为 $1$ 的半球。若 $3$ 个半径为 $r$ 的截面圆两两相切，且均与该半球的底面圆周相切，"
            r"则 $r=$"
        ),
        "answerLabel": r"$r$",
        "answerValue": f"${ans}$",
    },
    steps=[
        {
            "title": "半球与截面圆",
            "content": (
                r"<p>半球半径 $1$，底面为 $z=0$ 的单位圆。截面圆半径 $r$，其平面到球心距离 "
                r"$d=\sqrt{1-r^{2}}$，球心角半径 $\alpha=\arcsin r$。</p>"
            ),
            "highlight": ["Axis", "Sphere_hemi", "Plane_base", "Point_O", "Point_Z"],
            "cameraPos": c([6, 5, 6]),
        },
        {
            "title": "与底面圆周相切",
            "content": (
                r"<p>底面圆周是大圆。小圆与它相切，则小圆极点与 $z$ 轴夹角为 $\dfrac{\pi}{2}-\alpha$，"
                r"极点高度分量 $u_z=\sin\alpha=r$。</p>"
                r"<p>三个小圆两两外切，极点之间的球心角为 $2\alpha$，三极点在同一纬度上成正三角形。</p>"
            ),
            "highlight": ["Point_K1", "Point_K2", "Point_K3", "Circle1", "Circle2", "Circle3",
                          "Plane_base"],
            "cameraPos": c([5, 6, 4]),
        },
        {
            "title": "正三角形边长条件",
            "content": (
                r"<p>与赤道相切推出小圆极点的余纬为 $\dfrac{\pi}{2}-\alpha$，"
                r"即 $u_z=\sin\alpha=r$。三极点在同一纬度、方位角相差 $120^{\circ}$，"
                r"两两相切要求球心角 $2\alpha$，于是</p>"
                r"$$1-2r^{2}=r^{2}-\dfrac{1-r^{2}}{2}\implies r^{2}=\dfrac{3}{7}.$$"
                r"<p>因此 $r=\sqrt{\dfrac{3}{7}}=\dfrac{\sqrt{21}}{7}$。</p>"
            ),
            "highlight": ["Point_K1", "Point_K2", "Point_K3", "Line_K1K2", "Line_K2K3", "Line_K3K1"],
            "cameraPos": c([6, 4, 5]),
        },
    ],
    pts=pts,
    topo=topo,
    extra_edges=[
        {"a": "K1", "b": "K2", "color": "aux", "dashed": True},
        {"a": "K2", "b": "K3", "color": "aux", "dashed": True},
        {"a": "K3", "b": "K1", "color": "aux", "dashed": True},
    ],
    extra_spheres=["K1", "K2", "K3"],
    elements={
        "Axis": {"type": "axes", "size": 2.2},
        "Point_O": {"type": "point", "center": "O"},
        "Point_Z": {"type": "point", "center": "Z"},
        "Point_K1": {"type": "point", "center": "K1"},
        "Point_K2": {"type": "point", "center": "K2"},
        "Point_K3": {"type": "point", "center": "K3"},
        "Line_K1K2": {"type": "line", "a": "K1", "b": "K2", "color": "emphasis", "depthTest": False},
        "Line_K2K3": {"type": "line", "a": "K2", "b": "K3", "color": "emphasis", "depthTest": False},
        "Line_K3K1": {"type": "line", "a": "K3", "b": "K1", "color": "emphasis", "depthTest": False},
        "Plane_base": {"type": "plane", "pts": ["A", "B", "C"]},
        "Sphere_hemi": {"type": "sphere", "center": "O", "radius": 1 * scale, "opacity": 0.08},
        "Circle1": {"type": "sphere", "center": "K1", "radius": float(r * scale), "opacity": 0.15},
        "Circle2": {"type": "sphere", "center": "K2", "radius": float(r * scale), "opacity": 0.15},
        "Circle3": {"type": "sphere", "center": "K3", "radius": float(r * scale), "opacity": 0.15},
    },
    ans=ans,
    scale=scale,
)
