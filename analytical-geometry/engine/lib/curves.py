# -*- coding: utf-8 -*-
import sympy as sp
import geometry_kernel as gk

x_sym, y_sym, t_sym, theta_sym = sp.symbols("x y t theta")


def _named_xy(spec, points, key, default=None):
    if default is None:
        default = [0, 0]
    c = spec.get(key, default)
    if isinstance(c, str):
        if c not in points:
            raise ValueError(f"{key} 点 {c} 不存在")
        return points[c]
    return gk.parse_xy(c)


def _center(spec, points):
    return _named_xy(spec, points, "center")


class Curve:
    def __init__(self, key, spec, points):
        self.key = key
        self.spec = spec
        self.type = spec["type"]
        self.points = points

    def equation_latex(self) -> str:
        raise NotImplementedError

    def implicit(self):
        raise NotImplementedError

    def point_at(self, t, which=None):
        raise NotImplementedError

    def eccentricity(self):
        raise NotImplementedError(self.type)

    def focus(self, which):
        raise NotImplementedError(self.type)

    def vertex(self, which=None):
        raise NotImplementedError(self.type)

    def abc(self):
        raise NotImplementedError(self.type)

    def plot_recipe(self) -> dict:
        raise NotImplementedError

    def directrix_abc(self):
        raise NotImplementedError(self.type)


class LineCurve(Curve):
    def abc(self):
        if "a" in self.spec:
            return tuple(sp.sympify(self.spec[k]) for k in ("a", "b", "c"))
        names = self.spec["points"]
        return gk.line_abc_from_points(self.points[names[0]], self.points[names[1]])

    def implicit(self):
        a, b, c = self.abc()
        return a * x_sym + b * y_sym + c

    def equation_latex(self):
        a, b, c = self.abc()
        return gk.tex(a * x_sym + b * y_sym + c) + "=0"

    def plot_recipe(self):
        a, b, c = self.abc()
        return {"type": "line", "a": gk.unitless_float(a), "b": gk.unitless_float(b),
                "c": gk.unitless_float(c)}

    def point_at(self, t, which=None):
        t = sp.sympify(t)
        if "points" in self.spec:
            A = self.points[self.spec["points"][0]]
            B = self.points[self.spec["points"][1]]
            return sp.simplify(A + t * (B - A))
        a, b, c = self.abc()
        if b == 0:
            x0 = sp.simplify(-c / a)
            return gk.V2(x0, t)
        x0 = sp.Integer(0)
        y0 = sp.simplify(-c / b)
        return gk.V2(x0, y0) + t * gk.V2(b, -a)


class CircleCurve(Curve):
    def _cr(self):
        return _center(self.spec, self.points), sp.sympify(self.spec["radius"])

    def implicit(self):
        O, r = self._cr()
        return (x_sym - O[0]) ** 2 + (y_sym - O[1]) ** 2 - r ** 2

    def equation_latex(self):
        return gk.tex(self.implicit()) + "=0"

    def point_at(self, t, which=None):
        O, r = self._cr()
        t = sp.sympify(t)
        return gk.V2(O[0] + r * sp.cos(t), O[1] + r * sp.sin(t))

    def eccentricity(self):
        return sp.Integer(0)

    def plot_recipe(self):
        O, r = self._cr()
        return {"type": "ellipse", "cx": gk.unitless_float(O[0]), "cy": gk.unitless_float(O[1]),
                "rx": gk.unitless_float(r), "ry": gk.unitless_float(r)}


class EllipseCurve(Curve):
    def _abO(self):
        a, b = sp.sympify(self.spec["a"]), sp.sympify(self.spec["b"])
        if a <= 0 or b <= 0:
            raise ValueError(f"椭圆 {self.key} 的 a,b 必须为正")
        axis = self.spec.get("axis", "x")
        return a, b, _center(self.spec, self.points), axis

    def implicit(self):
        a, b, O, axis = self._abO()
        X, Y = x_sym - O[0], y_sym - O[1]
        if axis == "x":
            return X ** 2 / a ** 2 + Y ** 2 / b ** 2 - 1
        return X ** 2 / b ** 2 + Y ** 2 / a ** 2 - 1

    def equation_latex(self):
        a, b, O, axis = self._abO()
        if O[0] == 0 and O[1] == 0 and axis == "x":
            return rf"\dfrac{{x^{{2}}}}{{{gk.tex(a ** 2)}}}+\dfrac{{y^{{2}}}}{{{gk.tex(b ** 2)}}}=1"
        return gk.tex(self.implicit()) + "=0"

    def point_at(self, t, which=None):
        a, b, O, axis = self._abO()
        t = sp.sympify(t)
        if axis == "x":
            return gk.V2(O[0] + a * sp.cos(t), O[1] + b * sp.sin(t))
        return gk.V2(O[0] + b * sp.cos(t), O[1] + a * sp.sin(t))

    def eccentricity(self):
        a, b, O, axis = self._abO()
        A = sp.Max(a, b)
        c2 = sp.Abs(a ** 2 - b ** 2)
        return sp.simplify(sp.sqrt(c2) / A)

    def _c(self):
        a, b, O, axis = self._abO()
        return sp.sqrt(sp.Abs(a ** 2 - b ** 2)), a, b, O, axis

    def focus(self, which):
        if which not in ("right", "left", "upper", "lower"):
            raise ValueError(f"focus.which={which}")
        c, a, b, O, axis = self._c()
        if axis == "x":
            major_x = a >= b
        else:
            major_x = a < b
        if major_x:
            if which in ("upper", "lower"):
                raise ValueError(f"focus.which={which}")
            s = 1 if which == "right" else -1
            return gk.V2(O[0] + s * c, O[1])
        if which in ("left", "right"):
            raise ValueError(f"focus.which={which}")
        s = 1 if which == "upper" else -1
        return gk.V2(O[0], O[1] + s * c)

    def vertex(self, which):
        a, b, O, axis = self._abO()
        table = {
            "right": gk.V2(O[0] + (a if axis == "x" else b), O[1]),
            "left": gk.V2(O[0] - (a if axis == "x" else b), O[1]),
            "upper": gk.V2(O[0], O[1] + (b if axis == "x" else a)),
            "lower": gk.V2(O[0], O[1] - (b if axis == "x" else a)),
        }
        if which not in table:
            raise ValueError(f"vertex.which={which}")
        return table[which]

    def plot_recipe(self):
        a, b, O, axis = self._abO()
        rx, ry = (a, b) if axis == "x" else (b, a)
        return {"type": "ellipse", "cx": gk.unitless_float(O[0]), "cy": gk.unitless_float(O[1]),
                "rx": gk.unitless_float(rx), "ry": gk.unitless_float(ry)}


class HyperbolaCurve(Curve):
    def _abO(self):
        a, b = sp.sympify(self.spec["a"]), sp.sympify(self.spec["b"])
        if a <= 0 or b <= 0:
            raise ValueError(f"双曲线 {self.key} 的 a,b 必须为正")
        trans = self.spec.get("transverse", "x")
        return a, b, _center(self.spec, self.points), trans

    def implicit(self):
        a, b, O, trans = self._abO()
        X, Y = x_sym - O[0], y_sym - O[1]
        if trans == "x":
            return X ** 2 / a ** 2 - Y ** 2 / b ** 2 - 1
        return Y ** 2 / a ** 2 - X ** 2 / b ** 2 - 1

    def equation_latex(self):
        return gk.tex(self.implicit()) + "=0"

    def eccentricity(self):
        a, b, O, trans = self._abO()
        return sp.simplify(sp.sqrt(a ** 2 + b ** 2) / a)

    def _c(self):
        a, b, O, trans = self._abO()
        return sp.sqrt(a ** 2 + b ** 2), a, b, O, trans

    def focus(self, which):
        c, a, b, O, trans = self._c()
        if trans == "x":
            if which not in ("right", "left"):
                raise ValueError(f"focus.which={which}")
            s = 1 if which == "right" else -1
            return gk.V2(O[0] + s * c, O[1])
        if which not in ("upper", "lower"):
            raise ValueError(f"focus.which={which}")
        s = 1 if which == "upper" else -1
        return gk.V2(O[0], O[1] + s * c)

    def point_at(self, t, which=None):
        a, b, O, trans = self._abO()
        t = sp.sympify(t)
        if trans == "x":
            if which is None:
                which = "right"
            if which not in ("right", "left"):
                raise ValueError(f"point_at.which={which}")
            s = 1 if which == "right" else -1
            return gk.V2(O[0] + s * a * sp.cosh(t), O[1] + b * sp.sinh(t))
        if which is None:
            which = "upper"
        if which not in ("upper", "lower"):
            raise ValueError(f"point_at.which={which}")
        s = 1 if which == "upper" else -1
        return gk.V2(O[0] + b * sp.sinh(t), O[1] + s * a * sp.cosh(t))

    def plot_recipe(self):
        a, b, O, trans = self._abO()
        return {"type": "hyperbola", "cx": gk.unitless_float(O[0]), "cy": gk.unitless_float(O[1]),
                "a": gk.unitless_float(a), "b": gk.unitless_float(b), "transverse": trans}


class ParabolaCurve(Curve):
    def _pV(self):
        p = sp.sympify(self.spec["p"])
        if p <= 0:
            raise ValueError(f"抛物线 {self.key} 的 p 必须为正")
        V = _named_xy(self.spec, self.points, "vertex")
        axis = self.spec.get("axis", "x")
        direction = self.spec.get("direction", "+")
        return p, V, axis, direction

    def implicit(self):
        p, V, axis, direction = self._pV()
        s = 1 if direction == "+" else -1
        X, Y = x_sym - V[0], y_sym - V[1]
        if axis == "x":
            return Y ** 2 - 2 * p * s * X
        return X ** 2 - 2 * p * s * Y

    def equation_latex(self):
        return gk.tex(self.implicit()) + "=0"

    def eccentricity(self):
        return sp.Integer(1)

    def focus(self, which):
        p, V, axis, direction = self._pV()
        s = 1 if direction == "+" else -1
        d = p / 2
        if axis == "x":
            return gk.V2(V[0] + s * d, V[1])
        return gk.V2(V[0], V[1] + s * d)

    def point_at(self, t, which=None):
        p, V, axis, direction = self._pV()
        t = sp.sympify(t)
        s = 1 if direction == "+" else -1
        if axis == "x":
            return gk.V2(V[0] + s * t ** 2 / (2 * p), V[1] + t)
        return gk.V2(V[0] + t, V[1] + s * t ** 2 / (2 * p))

    def directrix_abc(self):
        p, V, axis, direction = self._pV()
        s = 1 if direction == "+" else -1
        d = p / 2
        if axis == "x":
            x0 = V[0] - s * d
            return (sp.Integer(1), sp.Integer(0), sp.simplify(-x0))
        y0 = V[1] - s * d
        return (sp.Integer(0), sp.Integer(1), sp.simplify(-y0))

    def plot_recipe(self):
        p, V, axis, direction = self._pV()
        return {"type": "parabola", "vx": gk.unitless_float(V[0]), "vy": gk.unitless_float(V[1]),
                "p": gk.unitless_float(p), "axis": axis, "direction": direction}


class ParametricCurve(Curve):
    def _xy_expr(self):
        xs = self.spec.get("x(t)", self.spec.get("x"))
        ys = self.spec.get("y(t)", self.spec.get("y"))
        return sp.sympify(xs), sp.sympify(ys)

    def point_at(self, t, which=None):
        t = sp.sympify(t)
        xe, ye = self._xy_expr()
        return gk.V2(xe.subs(t_sym, t), ye.subs(t_sym, t))

    def plot_recipe(self):
        xe, ye = self._xy_expr()
        tmin = gk.unitless_float(sp.sympify(self.spec.get("tmin", 0)))
        tmax = gk.unitless_float(sp.sympify(self.spec.get("tmax", 2 * sp.pi)))
        return {"type": "parametric", "x": str(xe), "y": str(ye),
                "tmin": tmin, "tmax": tmax}


class PolarCurve(Curve):
    def _r_expr(self):
        src = self.spec.get("r(theta)", self.spec.get("r"))
        return sp.sympify(src)

    def point_at(self, t, which=None):
        t = sp.sympify(t)
        r = self._r_expr().subs({t_sym: t, theta_sym: t})
        return gk.V2(r * sp.cos(t), r * sp.sin(t))

    def plot_recipe(self):
        tmin = gk.unitless_float(sp.sympify(self.spec.get("tmin", 0)))
        tmax = gk.unitless_float(sp.sympify(self.spec.get("tmax", 2 * sp.pi)))
        return {"type": "polar", "r": str(self._r_expr()),
                "tmin": tmin, "tmax": tmax}


class ImplicitCurve(Curve):
    def implicit(self):
        return sp.sympify(self.spec["expr"])

    def equation_latex(self):
        return gk.tex(self.implicit()) + "=0"

    def point_at(self, t, which=None):
        raise ValueError("implicit 曲线不能 on_curve，请显式给点")

    def plot_recipe(self):
        return {"type": "implicit", "expr": str(self.implicit())}


MAKERS = {
    "line": LineCurve,
    "circle": CircleCurve,
    "ellipse": EllipseCurve,
    "hyperbola": HyperbolaCurve,
    "parabola": ParabolaCurve,
    "parametric": ParametricCurve,
    "polar": PolarCurve,
    "implicit": ImplicitCurve,
}


def make_curve(key, spec, points) -> Curve:
    t = spec.get("type")
    if t not in MAKERS:
        raise ValueError(f"未知曲线类型 {t!r}，可选 {sorted(MAKERS)}")
    return MAKERS[t](key, spec, points)


def intersect(c1: Curve, c2: Curve):
    f = sp.simplify(c1.implicit())
    g = sp.simplify(c2.implicit())
    sols = sp.solve([f, g], [x_sym, y_sym], dict=True)
    if not sols:
        raise ValueError(f"{c1.key} 与 {c2.key} 无交点")
    pts = []
    for s in sols:
        pts.append(gk.V2(sp.simplify(s[x_sym]), sp.simplify(s[y_sym])))
    return pts


def pick_intersection(pts, which):
    if which is None:
        if len(pts) != 1:
            raise ValueError(f"多个交点必须提供 which（0/1 或 left/right/upper/lower），得到 {len(pts)} 个")
        return pts[0]
    if which in (0, 1, "0", "1"):
        return pts[int(which)]
    xs = sorted(pts, key=lambda p: (sp.N(p[0]), sp.N(p[1])))
    ys = sorted(pts, key=lambda p: (sp.N(p[1]), sp.N(p[0])))
    table = {"left": xs[0], "right": xs[-1], "lower": ys[0], "upper": ys[-1]}
    if which not in table:
        raise ValueError(f"which={which!r}")
    return table[which]


def chord_length(curve: Curve, line: Curve):
    hits = intersect(curve, line)
    if len(hits) != 2:
        raise ValueError(f"弦需要 2 个交点，得到 {len(hits)}")
    return gk.dist(hits[0], hits[1])
