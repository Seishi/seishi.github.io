# -*- coding: utf-8 -*-
import re
import sympy as sp

FRAC_RE = re.compile(r"\\frac")


def use_dfrac(s: str) -> str:
    return FRAC_RE.sub(r"\\dfrac", s)


def dfrac_tree(obj):
    if isinstance(obj, str):
        return use_dfrac(obj)
    if isinstance(obj, list):
        return [dfrac_tree(x) for x in obj]
    if isinstance(obj, dict):
        return {k: dfrac_tree(v) for k, v in obj.items()}
    return obj


def V2(x, y=None):
    if y is None and isinstance(x, (list, tuple)) and len(x) == 2:
        x, y = x
    return sp.Matrix([sp.sympify(x), sp.sympify(y)])


def parse_xy(value):
    if isinstance(value, sp.Matrix):
        return value
    if isinstance(value, (list, tuple)) and len(value) == 2:
        return V2(value[0], value[1])
    raise TypeError(f"需要 [x,y]，得到 {value!r}")


def midpoint(a, b):
    return (a + b) / 2


def dist(a, b):
    return sp.simplify((a - b).norm())


def tex(expr) -> str:
    return use_dfrac(sp.latex(sp.simplify(expr)))


def tex_point(p) -> str:
    return r"\left(" + ", ".join(tex(c) for c in p) + r"\right)"


def line_abc_from_points(A, B):
    a = sp.simplify(A[1] - B[1])
    b = sp.simplify(B[0] - A[0])
    c = sp.simplify(A[0] * B[1] - B[0] * A[1])
    return a, b, c


def point_line_distance(P, a, b, c):
    return sp.simplify(sp.Abs(a * P[0] + b * P[1] + c) / sp.sqrt(a ** 2 + b ** 2))


def area_triangle(A, B, C):
    return sp.simplify(sp.Abs((B - A)[0] * (C - A)[1] - (B - A)[1] * (C - A)[0]) / 2)


def unitless_float(expr) -> float:
    return float(sp.N(sp.simplify(expr)))
