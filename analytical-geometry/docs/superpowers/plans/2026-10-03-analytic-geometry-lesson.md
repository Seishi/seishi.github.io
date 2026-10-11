# 高中解析几何交互解题页 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 做出与立体几何同构的解析几何引擎：`problem.json` → sympy 精确求解 → 单页 HTML（左 MathJax 分步，右 JSXGraph 高亮/拖动），根目录列表可点进每题。

**Architecture:** Python 内核（`geometry_kernel.py` + `curves.py` + `solve.py`）根据 spec 算出点、方程、`vals`、`answer`；`build.py` 替换占位符、校验、把 JSON 注入 `lesson.html`；浏览器里 JSXGraph 画常驻曲线/点，按 `highlight` 切换强调元素，可选 `draggable` 用 JS 数值刷新读数。成品只写 `problems/` 与根 `index.html`。

**Tech Stack:** Python 3、sympy、MathJax 3 CDN、JSXGraph 1.10 CDN、静态 HTML。测试用 `engine/scripts/selftest.py`（不用 pytest）。对照实现：`/Users/zhangshengzhi/Documents/stereometry`。

**Spec:** `docs/superpowers/specs/2026-10-03-analytic-geometry-lesson-design.md`

---

## File map

| Path | Responsibility |
|---|---|
| `requirements.txt` | `sympy>=1.12` |
| `.gitignore` | `.venv/`, `__pycache__/` |
| `README.md` / `AGENTS.md` | 人/Agent 入口 |
| `.cursor/skills/analytic-geometry-lesson/SKILL.md` | 出题工作流 |
| `engine/lib/geometry_kernel.py` | 2D 向量、距离、角度、TeX |
| `engine/lib/curves.py` | 曲线构造、方程、参数点、交点、plot recipe |
| `engine/scripts/solve.py` | spec → `{answer, mp, eq, vals, math_points, plot_curves}` |
| `engine/scripts/validate.py` | FAIL 条件 1–15 |
| `engine/scripts/build.py` | 求解 + 替换 + 补全 + 渲染 + 刷新列表 |
| `engine/scripts/new_problem.py` | 分配 `problems/YYYYMMDD-NN-slug/` |
| `engine/scripts/rebuild_index.py` | 扫描 problems 写根 `index.html` |
| `engine/scripts/selftest.py` | 回归 |
| `engine/template/lesson.html` | 单题页 |
| `engine/template/index.html` | 列表页壳，`__PROBLEMS_JSON__` |
| `engine/template/ui-en.json` | 英文 UI |
| `engine/references/api.md` | Agent 只读 API |
| `engine/references/problem-schema.md` | lesson/model 字段 |
| `engine/fixtures/` | 校验失败夹具 + 最小 PASS 夹具 |
| `problems/` | 成品题，第一版放椭圆弦长示例 |

常量（全局一致，禁止改名）：

```python
ALLOWED_TAGS = ("line-circle", "ellipse", "hyperbola", "parabola", "parametric-polar")
PLACEHOLDER_RE = r"\{\{([a-zA-Z0-9_.]+)\}\}"
LESSON_PLACEHOLDER = "__LESSON_DATA__"
INDEX_PLACEHOLDER = "__PROBLEMS_JSON__"
JSXGRAPH_JS = "https://cdn.jsdelivr.net/npm/jsxgraph@1.10.1/distrib/jsxgraphcore.js"
JSXGRAPH_CSS = "https://cdn.jsdelivr.net/npm/jsxgraph@1.10.1/distrib/jsxgraph.css"
MATHJAX_JS = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"
THEME_KEY = "analytical-geometry-theme"
```

`solve(spec)` 返回字典键（禁止改名）：`answer`（裸 LaTeX）、`mp`（点名 → 如 `(2, 0)` 或 `\left(\sqrt{2}, 1\right)`）、`eq`（曲线 key → 裸方程 LaTeX）、`vals`（dict，值已是 LaTeX 字符串或可 `str` 的展示串）、`math_points`（点名 → `[x,y]` 的 float，供画板）、`plot_curves`（曲线 key → plot recipe dict）、`frame`（`{xmin,xmax,ymin,ymax}` float）。

plot recipe 形状：

```python
{"type": "ellipse", "cx": 0.0, "cy": 0.0, "rx": 2.0, "ry": 1.0}  # 轴对齐椭圆/圆
{"type": "line", "a": 1.0, "b": -2.0, "c": 0.0}  # ax+by+c=0
{"type": "hyperbola", "cx": 0.0, "cy": 0.0, "a": 2.0, "b": 1.0, "transverse": "x"}
{"type": "parabola", "vx": 0.0, "vy": 0.0, "p": 2.0, "axis": "x", "direction": "+"}
{"type": "parametric", "x": "2*cos(t)", "y": "sin(t)", "tmin": 0.0, "tmax": 6.283185307179586}
{"type": "polar", "r": "2/(1-0.5*cos(theta))", "tmin": 0.0, "tmax": 6.283185307179586}
{"type": "implicit", "expr": "x**2+y**2-1"}  # 纯 ASCII，JS 用 Function
```

---

### Task 1: 仓库骨架

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `problems/.gitkeep`
- Create: `engine/lib/__init__.py`
- Create: `engine/scripts/__init__.py`
- Create: `engine/fixtures/.gitkeep`

- [ ] **Step 1: 写依赖与忽略规则**

`requirements.txt`:

```
sympy>=1.12
```

`.gitignore`:

```
.venv/
__pycache__/
*.pyc
.DS_Store
```

空 `__init__.py` 两个；`problems/.gitkeep`、`engine/fixtures/.gitkeep` 内容为空。

- [ ] **Step 2: 建虚拟环境并安装（先问用户；本计划默认用户已同意，因为没有 sympy 引擎无法测）**

```bash
cd /Users/zhangshengzhi/Documents/analytical-geometry
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -c "import sympy; print(sympy.__version__)"
```

Expected: 打印 `1.12` 或更高。

- [ ] **Step 3: Commit**

```bash
cd /Users/zhangshengzhi/Documents/analytical-geometry
git init
git add requirements.txt .gitignore problems/.gitkeep engine/lib/__init__.py engine/scripts/__init__.py engine/fixtures/.gitkeep docs
git commit -m "chore: scaffold analytic-geometry repo"
```

---

### Task 2: kernel 基础（V2、TeX、点距离）

**Files:**
- Create: `engine/lib/geometry_kernel.py`
- Create: `engine/scripts/selftest.py`

- [ ] **Step 1: 写会失败的 selftest（函数还不存在）**

`engine/scripts/selftest.py`:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_DIR / "scripts"))
sys.path.insert(0, str(SKILL_DIR / "lib"))

import sympy as sp

failures = []


def check(ok, name, detail=""):
    print(("PASS  " if ok else "FAIL  ") + name + (f"   {detail}" if detail else ""))
    if not ok:
        failures.append(name)


def main():
    import geometry_kernel as gk

    p = gk.V2(3, 4)
    check(list(p) == [sp.Integer(3), sp.Integer(4)], "V2(3,4)")
    check(gk.tex(sp.Rational(1, 2)) == r"\dfrac{1}{2}", "tex 1/2 uses dfrac", gk.tex(sp.Rational(1, 2)))
    check(gk.tex_point(gk.V2(sp.sqrt(2), 1)) == r"\left(\sqrt{2}, 1\right)",
          "tex_point sqrt2", gk.tex_point(gk.V2(sp.sqrt(2), 1)))
    m = gk.midpoint(gk.V2(0, 0), gk.V2(2, 4))
    check(list(m) == [sp.Integer(1), sp.Integer(2)], "midpoint")
    d = gk.dist(gk.V2(0, 0), gk.V2(3, 4))
    check(sp.simplify(d - 5) == 0, "dist 3-4-5")
    if failures:
        print(f"\n{len(failures)} failed")
        sys.exit(1)
    print("\nall passed")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 跑测试，确认失败**

```bash
.venv/bin/python engine/scripts/selftest.py
```

Expected: `ModuleNotFoundError: geometry_kernel` 或 `AttributeError`。

- [ ] **Step 3: 最小实现 `engine/lib/geometry_kernel.py`**

```python
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
```

- [ ] **Step 4: 再跑 selftest**

```bash
.venv/bin/python engine/scripts/selftest.py
```

Expected: `all passed`。`tex_point` 若实际是 `( \sqrt{2}, 1 )` 而不是 `\left(...\right)`，改测试为接受 `sp.latex` 的真实输出，或在 `tex_point` 里强制 `\left(`；以 selftest 里那条字符串为准，实现必须产出它。

- [ ] **Step 5: Commit**

```bash
git add engine/lib/geometry_kernel.py engine/scripts/selftest.py
git commit -m "feat: add 2D sympy kernel primitives"
```

---

### Task 3: 曲线对象（直线、圆、椭圆）+ 焦点/参数点

**Files:**
- Create: `engine/lib/curves.py`
- Modify: `engine/scripts/selftest.py`

- [ ] **Step 1: 在 `selftest.py` 的 `main()` 末尾、`if failures` 之前追加**

```python
    import curves as cv

    E = cv.make_curve("C", {
        "type": "ellipse", "a": 2, "b": 1, "center": [0, 0], "axis": "x"
    }, {})
    check(E.equation_latex().replace(" ", "") == r"\dfrac{x^{2}}{4}+y^{2}=1".replace(" ", "")
          or "x^{2}" in E.equation_latex(),
          "ellipse equation", E.equation_latex())
    check(sp.simplify(E.eccentricity() - sp.sqrt(3) / 2) == 0, "ellipse e")
    F = E.focus("right")
    check(sp.simplify(F[0] - sp.sqrt(3)) == 0 and F[1] == 0, "ellipse right focus", F)
    P = E.point_at(sp.pi / 3)
    check(sp.simplify(P[0] - 1) == 0 and sp.simplify(P[1] - sp.sqrt(3) / 2) == 0,
          "ellipse point_at pi/3", P)
    circ = cv.make_curve("O", {"type": "circle", "center": [0, 0], "radius": 2}, {})
    Q = circ.point_at(0)
    check(sp.simplify(Q[0] - 2) == 0 and Q[1] == 0, "circle point_at 0")
    ln = cv.make_curve("l", {"type": "line", "a": 1, "b": -2, "c": 0}, {})
    abc = ln.abc()
    check(abc[0] != 0 or abc[1] != 0, "line abc")
```

- [ ] **Step 2: 跑测试，确认失败**

```bash
.venv/bin/python engine/scripts/selftest.py
```

Expected: `ModuleNotFoundError: curves`。

- [ ] **Step 3: 实现 `engine/lib/curves.py`（直线/圆/椭圆部分；其它 type 先 `raise ValueError`）**

```python
# -*- coding: utf-8 -*-
import sympy as sp
import geometry_kernel as gk

x_sym, y_sym, t_sym = sp.symbols("x y t")


def _center(spec, points):
    c = spec.get("center", [0, 0])
    if isinstance(c, str):
        if c not in points:
            raise ValueError(f"center 点 {c} 不存在")
        return points[c]
    return gk.parse_xy(c)


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
        c, a, b, O, axis = self._c()
        major_x = (axis == "x" and a >= b) or (axis == "y" and a < b)
        if which in ("right", "left"):
            s = 1 if which == "right" else -1
            if major_x:
                return gk.V2(O[0] + s * c, O[1])
            return gk.V2(O[0], O[1] + s * c)
        if which in ("upper", "lower"):
            s = 1 if which == "upper" else -1
            if major_x:
                return gk.V2(O[0], O[1] + s * c)
            return gk.V2(O[0] + s * c, O[1])
        raise ValueError(f"focus.which={which}")

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


MAKERS = {
    "line": LineCurve,
    "circle": CircleCurve,
    "ellipse": EllipseCurve,
}


def make_curve(key, spec, points) -> Curve:
    t = spec.get("type")
    if t not in MAKERS:
        raise ValueError(f"未知曲线类型 {t!r}，可选 {sorted(MAKERS)}")
    return MAKERS[t](key, spec, points)
```

椭圆方程 LaTeX 以 selftest 宽松断言为准；若 `equation_latex` 含 `x^{2}` 且含 `=1` 即过。

- [ ] **Step 4: 跑 selftest，必须 `all passed`**

```bash
.venv/bin/python engine/scripts/selftest.py
```

- [ ] **Step 5: Commit**

```bash
git add engine/lib/curves.py engine/scripts/selftest.py
git commit -m "feat: add line, circle, ellipse curve objects"
```

---

### Task 4: 双曲线、抛物线、参数、极坐标、隐式

**Files:**
- Modify: `engine/lib/curves.py`
- Modify: `engine/scripts/selftest.py`

- [ ] **Step 1: selftest 追加**

```python
    H = cv.make_curve("H", {
        "type": "hyperbola", "a": 2, "b": 1, "center": [0, 0], "transverse": "x"
    }, {})
    check(sp.simplify(H.eccentricity() - sp.sqrt(5) / 2) == 0, "hyperbola e")
    Pr = H.point_at(0, which="right")
    check(sp.simplify(Pr[0] - 2) == 0 and Pr[1] == 0, "hyperbola right t=0", Pr)
    Par = cv.make_curve("P", {
        "type": "parabola", "p": 2, "vertex": [0, 0], "axis": "x", "direction": "+"
    }, {})
    Fpar = Par.focus("right")
    check(sp.simplify(Fpar[0] - 1) == 0 and Fpar[1] == 0, "parabola focus p/2")
    Pt = Par.point_at(2)
    check(sp.simplify(Pt[0] - 1) == 0 and sp.simplify(Pt[1] - 2) == 0, "parabola point_at", Pt)
    Parab_e = Par.eccentricity()
    check(sp.simplify(Parab_e - 1) == 0, "parabola e=1")
    Param = cv.make_curve("R", {
        "type": "parametric", "x(t)": "2*cos(t)", "y(t)": "sin(t)", "tmin": 0, "tmax": "2*pi"
    }, {})
    Pp = Param.point_at(0)
    check(sp.simplify(Pp[0] - 2) == 0 and Pp[1] == 0, "parametric t=0")
    Polar = cv.make_curve("K", {
        "type": "polar", "r(theta)": "2", "tmin": 0, "tmax": "2*pi"
    }, {})
    Pk = Polar.point_at(0)
    check(sp.simplify(Pk[0] - 2) == 0 and Pk[1] == 0, "polar r=2")
    Imp = cv.make_curve("I", {"type": "implicit", "expr": "x**2 + y**2 - 1"}, {})
    check("x" in Imp.equation_latex(), "implicit eq")
```

抛物线 `y^2=2px`、`p=2` ⇒ `y^2=4x`，`t=y=2` ⇒ `x=t^2/(2p)=4/4=1`。焦点 `(p/2,0)=(1,0)`。

- [ ] **Step 2: 跑测试，确认新断言 FAIL**

```bash
.venv/bin/python engine/scripts/selftest.py
```

Expected: `未知曲线类型 'hyperbola'`。

- [ ] **Step 3: 在 `curves.py` 增加四类并注册进 `MAKERS`**

`HyperbolaCurve`：`transverse=x` 时 \((x-h)^2/a^2-(y-k)^2/b^2=1\)；`e=\sqrt{a^2+b^2}/a`；`focus(right/left)` 为 \((h\pm c,k)\)，`c=\sqrt{a^2+b^2}`；`point_at(t, which)` 默认 `right`：\(x=h\pm a\cosh t,\ y=k+b\sinh t\)。

`ParabolaCurve`：顶点 `vertex`（点名或坐标）；`axis=x` 且 `direction=+`：\( (y-k)^2 = 2p(x-h) \)；`point_at(t)`：`axis=x` 时 \(x=h+t^2/(2p),\ y=k+t\)（`direction=-` 则 \(x=h-t^2/(2p)\)）；`axis=y` 时对调，`t` 为横坐标；`focus`：沿轴正向距顶点 `p/2`；`directrix_abc`：轴负向距顶点 `p/2` 的直线；`eccentricity=1`。

`ParametricCurve`：读 `x(t)`、`y(t)`（也接受键 `x`/`y`）；`point_at` 用 `sp.sympify` 代入 `t`；`plot_recipe` 的 `x`/`y` 用 `str(sp.sympify(...))` ASCII；`tmin`/`tmax` 转 float。

`PolarCurve`：`r(theta)`，点 \(r\cos\theta, r\sin\theta\)；`plot_recipe` type `polar`，键 `r`。

`ImplicitCurve`：`expr` 字符串；`implicit()` = `sp.sympify(expr)`；`plot_recipe` type `implicit`；`point_at` 直接 `raise ValueError("implicit 曲线不能 on_curve，请显式给点")`。

把它们放进 `MAKERS`。

- [ ] **Step 4: selftest 全绿**

```bash
.venv/bin/python engine/scripts/selftest.py
```

- [ ] **Step 5: Commit**

```bash
git add engine/lib/curves.py engine/scripts/selftest.py
git commit -m "feat: add hyperbola, parabola, parametric, polar, implicit"
```

---

### Task 5: 交点与弦长

**Files:**
- Modify: `engine/lib/curves.py`
- Modify: `engine/lib/geometry_kernel.py`
- Modify: `engine/scripts/selftest.py`

- [ ] **Step 1: selftest 追加（直线 \(y=x/2\) 截椭圆 \(x^2/4+y^2=1\)，弦长 \(\sqrt{10}\)）**

```python
    pts = {}
    E = cv.make_curve("C", {"type": "ellipse", "a": 2, "b": 1, "center": [0, 0], "axis": "x"}, pts)
    L = cv.make_curve("l", {"type": "line", "a": 1, "b": -2, "c": 0}, pts)
    hits = cv.intersect(E, L)
    check(len(hits) == 2, "line-ellipse 2 hits", hits)
    length = cv.chord_length(E, L)
    check(sp.simplify(length - sp.sqrt(10)) == 0, "chord length sqrt(10)", length)
```

- [ ] **Step 2: 跑测试，确认 FAIL（没有 `intersect`）**

```bash
.venv/bin/python engine/scripts/selftest.py
```

- [ ] **Step 3: 实现交点与弦长**

在 `curves.py`：

```python
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
```

`LineCurve.implicit` 已有。椭圆+过原点直线可解。

- [ ] **Step 4: selftest 全绿**

```bash
.venv/bin/python engine/scripts/selftest.py
```

- [ ] **Step 5: Commit**

```bash
git add engine/lib/curves.py engine/scripts/selftest.py
git commit -m "feat: intersect curves and compute chord length"
```

---

### Task 6: `solve.py`（场景、givens、全部 query）

**Files:**
- Create: `engine/scripts/solve.py`
- Modify: `engine/scripts/selftest.py`

- [ ] **Step 1: selftest 追加求解用例**

```python
    from solve import solve

    spec = {
        "language": "zh-CN",
        "tags": ["ellipse"],
        "frame": {"xmin": -6, "xmax": 6, "ymin": -4, "ymax": 4},
        "curves": {
            "C": {"type": "ellipse", "a": 2, "b": 1, "center": [0, 0], "axis": "x"},
            "l": {"type": "line", "a": 1, "b": -2, "c": 0},
        },
        "points": {},
        "givens": [
            {"name": "F", "kind": "focus", "of": "C", "which": "right"},
            {"name": "A", "kind": "intersection", "of": ["C", "l"], "which": "right"},
            {"name": "B", "kind": "intersection", "of": ["C", "l"], "which": "left"},
            {"name": "P", "kind": "on_curve", "curve": "C", "t": "pi/3"},
        ],
        "lengths": {"AB": ["A", "B"]},
        "query": {"type": "chord_length", "line": "l", "curve": "C"},
    }
    sol = solve(spec)
    check(sol["answer"] == r"\sqrt{10}" or "sqrt{10}" in sol["answer"].replace(" ", ""),
          "solve chord answer", sol["answer"])
    check("F" in sol["mp"] and "A" in sol["mp"] and "P" in sol["mp"], "mp keys")
    check("C" in sol["eq"], "eq.C")
    check("len" in sol["vals"] or "len_AB" in sol["vals"], "vals chord", sol["vals"].keys())
    check(abs(sol["math_points"]["P"][0] - 1) < 1e-9, "math_points P")

    dspec = {
        "tags": ["line-circle"],
        "curves": {"l": {"type": "line", "a": 3, "b": 4, "c": -6}},
        "points": {"P": [0, 0]},
        "query": {"type": "point_line_distance", "point": "P", "line": "l"},
    }
    dsol = solve(dspec)
    check("dfrac{6}{5}" in dsol["answer"].replace(" ", "") or dsol["answer"] in (r"\dfrac{6}{5}", "6/5"),
          "point-line dist 6/5", dsol["answer"])

    cspec = {
        "tags": ["ellipse"],
        "curves": {"C": {"type": "ellipse", "a": 2, "b": 1, "center": [0, 0], "axis": "x"}},
        "query": {"type": "eccentricity", "curve": "C"},
    }
    check("sqrt{3}" in solve(cspec)["answer"], "e=sqrt3/2", solve(cspec)["answer"])
```

再追加：`line_line_angle`、`area_triangle`、`focal_radius`、`intersection`、`custom` 各一条，期望值写死：

- 水平线 `y=0` (`a=0,b=1,c=0`) 与 `x=0` (`a=1,b=0,c=0`)，`output=cos` → `0`
- 三点 `(0,0),(2,0),(0,2)` 面积 `2`
- 椭圆右焦点到右顶点 `(2,0)` 的焦半径：`a-c=2-\sqrt{3}`（`focal_radius` 用点到指定焦点的距离；query 字段 `point` + `curve`，焦点默认 `which=right`）
- `intersection` 返回两点 LaTeX 串进 `vals.pts`
- `custom`：`{"type":"custom","expr":"sqrt(4)"}` → `2`

- [ ] **Step 2: 跑测试，确认 FAIL**

```bash
.venv/bin/python engine/scripts/selftest.py
```

- [ ] **Step 3: 实现 `engine/scripts/solve.py`**

结构：

1. `build_points(spec)`：先放入 `spec.points`（`gk.parse_xy`），再按顺序处理 `givens`：
   - `point` / `midpoint` / `ratio` / `on_line`：用已有点
   - `focus` / `vertex`：`make_curve` 后调用
   - `on_curve`：`curve.point_at(sp.sympify(t), which=...)`
   - `foot`：点到直线垂足。直线由曲线 key 或两点名给出。垂足公式：从 \(ax+by+c=0\)，\(P\) 到线投影。
   - `intersection`：`cv.intersect` + `cv.pick_intersection`
2. `build_curves(spec, points)`：对 `spec.curves` 每条 `make_curve`
3. `run_query(query, curves, points)` → `(answer_expr, vals_dict_of_sympy)`
   - `point_line_distance`：`line` 可以是曲线 key 或两点名列表
   - `line_line_angle`：两方向向量，夹角锐化（`Abs(dot)/(|d1||d2|)`），再按 `output` 取 sin/cos/tan 或 `degree`
   - `chord_length`：`cv.chord_length`；`vals` 含 `len`
   - `eccentricity`：`curve.eccentricity()`；vals `a,b,c,e`（抛物线 `e=1`，圆 `e=0`）
   - `focal_radius`：默认焦点 `which=right`（抛物线/椭圆）；`r = dist(P, F)`
   - `area_triangle`：`gk.area_triangle`
   - `intersection`：交点列表，`answer` 用 `;` 连接 `tex_point`
   - `custom`：若有 `expr`，`answer=sympify(expr)`（可用点坐标名？第一版只允许纯表达式 + `vals` 对象里每个值 `sympify`）。`vals` 键原样保留。
4. `solve(spec)` 组装：
   - `mp[name] = gk.tex_point(P)`
   - `eq[key] = curve.equation_latex()`
   - `vals`：query 的键用 `gk.tex`；`lengths` → `len_AB`；`vectors` → `vec_AB` 用 `tex_point` 差向量写成 `(x, y)`
   - `answer = gk.tex(answer_expr)`（intersection/custom 字符串则已经是 LaTeX 时不要再 `sp.latex` 一层）
   - `math_points`：`[gk.unitless_float(P[0]), gk.unitless_float(P[1])]`
   - `plot_curves`：`curve.plot_recipe()`
   - `frame` 缺省 `xmin=-8,xmax=8,ymin=-5,ymax=5`，转 float
5. CLI：`python solve.py problem.json` 读顶层 `spec` 或整份 spec，打印 JSON（`answer/mp/eq/vals`）。缺 sympy 时 `sys.exit("缺少 sympy。请先征得用户同意再安装：python3 -m pip install sympy")`。

垂足实现：

```python
def foot_of_perp(P, a, b, c):
    d = a ** 2 + b ** 2
    x = (b * (b * P[0] - a * P[1]) - a * c) / d
    y = (a * (-b * P[0] + a * P[1]) - b * c) / d
    return gk.V2(sp.simplify(x), sp.simplify(y))
```

- [ ] **Step 4: selftest 全绿**

```bash
.venv/bin/python engine/scripts/selftest.py
```

若 `tex` 输出 `\frac` 已被 `use_dfrac` 换成 `\dfrac`。答案字符串用 `in` 断言，避免 latex 空格差。

- [ ] **Step 5: Commit**

```bash
git add engine/scripts/solve.py engine/scripts/selftest.py engine/lib
git commit -m "feat: solve spec into answer, points, and vals"
```

---

### Task 7: `validate.py`

**Files:**
- Create: `engine/scripts/validate.py`
- Create: `engine/fixtures/bad-empty-highlight.json`
- Create: `engine/fixtures/bad-unknown-placeholder.json`
- Modify: `engine/scripts/selftest.py`

- [ ] **Step 1: 写两份坏夹具（不经 solve，直接喂 validate 的 data 形态）**

`engine/fixtures/bad-empty-highlight.json`：最小 data，`steps:[{title, content:"<p>$1$</p>", highlight:[]}]`，`model.elements` 有 `Axis`，`lesson.title` 有公式。

`engine/fixtures/bad-unknown-placeholder.json`：content 含 `{{vals.nope}}` 且 `model.elements.Axis={type:axes}`，highlight `["Axis"]`。validate 要在 **替换之前** 或 **替换之后** 抓未知键？规格是 build 在 substitute 时抛 KeyError。validate 抓：空 highlight、未知 highlight 键、缺 tags、`\frac`、定界符外 `\dfrac`、缺 answers 的多问标题。

selftest 追加：对合成 `data` 调 `validate(data)`。

```python
    from validate import validate
    ALLOWED = ("line-circle", "ellipse", "hyperbola", "parabola", "parametric-polar")

    def base_data(**kw):
        d = {
            "lesson": {"meta": "t", "title": "椭圆 $C$", "answerLabel": "弦长", "answerValue": r"$\sqrt{10}$"},
            "steps": [{"title": "建系", "content": "<p>$C$</p>", "highlight": ["Axis"]}],
            "model": {
                "points": {"O": [0, 0]},
                "frame": {"xmin": -4, "xmax": 4, "ymin": -3, "ymax": 3},
                "elements": {"Axis": {"type": "axes"}},
                "plot_curves": {},
            },
            "spec_tags": ["ellipse"],
        }
        d.update(kw)
        return d

    errs = validate(base_data(steps=[{"title": "a", "content": "<p>$1$</p>", "highlight": []}]))
    check(any("highlight" in e for e in errs), "empty highlight FAIL", errs)

    errs = validate(base_data(steps=[{"title": "a", "content": "<p>$1$</p>", "highlight": ["Nope"]}]))
    check(any("Nope" in e for e in errs), "unknown highlight FAIL", errs)

    errs = validate(base_data())
    # 需要把 spec.tags 传进 validate：validate(data, tags=..., placeholders_ok=...)
    check(errs == [], "good data PASS", errs)
```

`validate` 签名定为：

```python
def validate(data, *, tags=None, answer=None) -> list[str]:
```

`tags` 缺省读 `data["lesson"]` 不行，读 `data.get("_tags")`。build 在 validate 前设置 `data["_tags"]=spec["tags"]`，validate 完删掉。或 `validate(data, tags=spec.get("tags"))`。用后者。

校验清单（每条都要有对应 `errs.append` 文案）：

1. 缺 `lesson`/`steps`/`model` 或 steps 空  
2. 步缺 `title`/`content`/`highlight`  
3. `highlight` 空  
4. highlight 键 ∉ `model.elements`  
5. 占位符：若 content 里仍有 `{{`（未替换完）→ FAIL「未替换占位符」  
6. 用正则找不在 `$...$` / `$$...$$` 内的 `\[a-zA-Z]+`  
7. 全文出现 `\frac` 或 `\tfrac`（`measure.label` 除外可在 elements 里单独允许无 `$`，但仍禁止 `\frac`）  
8. title 含 `(1)`/`（1）`/`(2)` 且无 `lesson.answers`  
9. 有 `answers` 且 `answerValue` 长度 > 40  
10. tags 空或不在 `ALLOWED_TAGS`  
11. elements type 不在允许集合：`point,line,segment,circle,ellipse,hyperbola,parabola,implicit,polar,parametric,axes,focus,directrix,arrow,measure,locus`  
12. 各 type 缺必填字段（对照 spec §8.3）  
13. 点名引用不在 `model.points`  
14. `draggable.point` 不在 points；`on` 既不是曲线 key（`plot_curves`）也不是两点名  
15. `$` 个数为奇数  

把立体几何 `validate.py` 的 LaTeX 定界扫描逻辑移植过来（读 `/Users/zhangshengzhi/Documents/stereometry/engine/scripts/validate.py` 里 title/content 扫描那一段，改成 2D 元素表）。**不要**检查 `cameraPos`。

- [ ] **Step 2: 跑测试 FAIL（无 validate 模块）**

```bash
.venv/bin/python engine/scripts/selftest.py
```

- [ ] **Step 3: 实现 `validate.py`，selftest 全绿**

```bash
.venv/bin/python engine/scripts/selftest.py
```

- [ ] **Step 4: Commit**

```bash
git add engine/scripts/validate.py engine/scripts/selftest.py engine/fixtures
git commit -m "feat: validate lesson data before writing HTML"
```

---

### Task 8: `build.py` 占位符替换与补全（先不依赖完整模板）

**Files:**
- Create: `engine/scripts/build.py`（含 `substitute`、`fill_defaults`、`lookup`；`render_html` 先写临时模板检测）
- Create: `engine/template/lesson.html` 最小版：整页只有 `<script id="lesson-data" type="application/json">__LESSON_DATA__</script>`
- Modify: `engine/scripts/selftest.py`

- [ ] **Step 1: selftest 追加**

```python
    from build import substitute, fill_defaults, build
    import tempfile, json

    ctx = {"answer": r"\sqrt{10}", "mp": {"A": r"\left(\sqrt{2}, \dfrac{1}{2}\right)"},
           "vals": {"len": r"\sqrt{10}"}, "eq": {"C": r"\dfrac{x^{2}}{4}+y^{2}=1"}}
    s = substitute("弦长 ${{vals.len}}$ 点 $A{{mp.A}}$", ctx)
    check(r"\sqrt{10}" in s and "mp.A" not in s, "substitute", s)
    try:
        substitute("{{vals.nope}}", ctx)
        check(False, "unknown placeholder should raise")
    except KeyError:
        check(True, "unknown placeholder raises")

    lesson = {
        "lesson": {"meta": "交互解题 · 椭圆弦长", "title": "椭圆 ${{eq.C}}$ 被直线所截弦长",
                   "answerLabel": "弦长"},
        "steps": [{"title": "建系", "content": "<p>方程 ${{eq.C}}$</p>", "highlight": ["Axis"]}],
        "model": {"elements": {"Axis": {"type": "axes"}}},
    }
    filled = fill_defaults(substitute(lesson, ctx), {
        "math_points": {"A": [1.41, 0.5]},
        "plot_curves": {"C": {"type": "ellipse", "cx": 0, "cy": 0, "rx": 2, "ry": 1}},
        "frame": {"xmin": -6, "xmax": 6, "ymin": -4, "ymax": 4},
        "answer": r"\sqrt{10}",
    }, {"language": "zh-CN", "tags": ["ellipse"]})
    check(filled["model"]["points"]["A"][0] > 1, "fill points")
    check(filled["lesson"].get("answerValue") == r"$\sqrt{10}$", "answerValue wrapped")
```

- [ ] **Step 2: 跑 FAIL**

```bash
.venv/bin/python engine/scripts/selftest.py
```

- [ ] **Step 3: 实现 substitute / fill_defaults（从立体几何 `build.py` 原样搬 `PLACEHOLDER_RE`/`lookup`/`substitute`，改 fill）**

`fill_defaults(data, sol, spec)`：

```python
model = data.setdefault("model", {})
model.setdefault("points", sol["math_points"])
model.setdefault("plot_curves", sol["plot_curves"])
model.setdefault("frame", sol["frame"])
if model.get("draggable"):
    model.setdefault("mathPoints", sol["math_points"])
    dr = model["draggable"]
    dr.setdefault("t0", dr.get("t"))
lesson = data.setdefault("lesson", {})
lesson.setdefault("language", spec.get("language", "zh-CN"))
if spec.get("language") == "en":
    import json
    from pathlib import Path
    ui = json.loads((Path(__file__).resolve().parent.parent / "template" / "ui-en.json").read_text())
    lesson.setdefault("ui", ui)
if not lesson.get("answers"):
    lesson.setdefault("answerValue", f"${sol['answer']}$")
return data
```

`build(spec, lesson_data, out_path)`：solve → ctx=`answer,mp,vals,eq` → substitute → fill_defaults → `gk.dfrac_tree` → `validate(..., tags=spec.get("tags"))` → FAIL 则 stderr 列出且 `sys.exit(1)` 且不写文件 → `render_html` 替换 `__LESSON_DATA__` → print `PASS  已生成: ...` → 调用 `rebuild_index.write_index()`，模块不存在则忽略。

CLI 与立体几何相同：2 参数单文件（`doc.pop("spec")`），3 参数拆分。

此时 `render_html` 读 `engine/template/lesson.html`。先放最小模板，Task 9 再换成完整页。

- [ ] **Step 4: selftest 全绿；再对 Task 6 的 chord spec 配最小 lesson 调 `build` 到临时文件，文件里要有 `\sqrt{10}`**

```python
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "out.html"
        doc_spec = {**spec}  # Task 6 那个 ellipse chord spec
        lesson_min = {
            "lesson": {"meta": "m", "title": "求弦长", "answerLabel": "弦长"},
            "steps": [{"title": "代入", "content": "<p>弦长为 ${{answer}}$</p>",
                       "highlight": ["Axis"]}],
            "model": {"elements": {"Axis": {"type": "axes"}}},
        }
        build(doc_spec, lesson_min, out)
        html = out.read_text()
        check("__LESSON_DATA__" not in html, "placeholder replaced")
        check("sqrt{10}" in html.replace(" ", ""), "html has answer")
```

`spec` 必须含 `tags`。validate 对 title「求弦长」无小问编号。

- [ ] **Step 5: Commit**

```bash
git add engine/scripts/build.py engine/template/lesson.html engine/scripts/selftest.py
git commit -m "feat: build problem.json into HTML via placeholders"
```

---

### Task 9: 完整单题模板（左栏 + JSXGraph 切步高亮）

**Files:**
- Modify: `engine/template/lesson.html`（整文件替换）
- Create: `engine/template/ui-en.json`

- [ ] **Step 1: 写 `ui-en.json`**

```json
{
  "skipToSteps": "Skip to solution steps",
  "backToList": "← All problems",
  "sidebarLabel": "Analytic geometry solution panel",
  "answerCardLabel": "Final answer",
  "answerTitle": "Final Answer",
  "solutionCardLabel": "Solution steps",
  "sceneLabel": "Interactive 2D figure",
  "interactionTip": "Drag to pan · Scroll to zoom",
  "previous": "Previous",
  "next": "Next",
  "finish": "Finish",
  "finished": "Done",
  "stepTemplate": "Step {current} / {total}",
  "reviewLabel": "Full solution",
  "finishAria": "Show the complete solution",
  "finishedAria": "Solution complete; all steps are shown",
  "collapseAria": "Collapse the full solution",
  "nextAriaTemplate": "Go to step {step}",
  "previousAriaTemplate": "Back to step {step}",
  "firstStepAria": "Already at the first step",
  "measureToggleOn": "Lengths: on",
  "measureToggleOff": "Lengths: off",
  "gridUnit": "1 grid square = 1 unit",
  "themeLight": "Light",
  "themeDark": "Dark",
  "themeToggle": "Switch light / dark theme",
  "resetView": "Reset view",
  "standardMark": "standard position",
  "boardError": "The figure failed to load."
}
```

中文默认写在模板 JS 的 `UI_ZH` 对象里，键与上面相同。`language==en` 时用 `lesson.ui`。

- [ ] **Step 2: 写完整 `lesson.html`**

布局从 `/Users/zhangshengzhi/Documents/stereometry/engine/template/lesson.html` **复制 CSS 变量、顶栏、左栏题面/答案卡/步骤按钮结构**（含完成展开全部步骤）。改动：

- `localStorage` 键改为 `analytical-geometry-theme`
- 返回链接 `../../index.html`（题在 `problems/id/`，列表在仓库根）。若打不开（file 协议层级），同时提供 `../index.html` 不合理；根列表 href 用相对 `problems/id/index.html`，题页返回 `../../index.html` 对 `file:///.../analytical-geometry/problems/id/index.html` 是对的。
- 右栏不要 Three.js，放：

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/jsxgraph@1.10.1/distrib/jsxgraph.css">
<script src="https://cdn.jsdelivr.net/npm/jsxgraph@1.10.1/distrib/jsxgraphcore.js"></script>
<div id="jxgbox" role="img" aria-label="解析几何画板" style="width:100%;height:100%;"></div>
<div id="board-error" hidden></div>
<div id="readouts" hidden></div>
<button type="button" id="reset-view">复位视野</button>
<button type="button" id="measure-toggle" hidden>长度标注：开</button>
```

- 数据：`<script id="lesson-data" type="application/json">__LESSON_DATA__</script>`
- MathJax CDN 与立体几何相同

**JS 画板逻辑（必须按此实现，不要另造 API）：**

```javascript
const COLORS = {
  frame: '#98A2AE', aux: '#8B96A5', emphasis: '#2563EB',
  normal: '#3B82F6', curve: '#2563EB', point: '#1D4ED8'
};
function frameBB(f) {
  f = f || {};
  return [f.xmin ?? -8, f.ymax ?? 5, f.xmax ?? 8, f.ymin ?? -5];
}
function drawPlot(board, recipe, opts) {
  const vis = opts.visible !== false;
  const col = opts.color || COLORS.curve;
  const w = opts.strokeWidth || 1.5;
  if (recipe.type === 'ellipse') {
    return board.create('ellipse', [
      [recipe.cx - recipe.rx, recipe.cy],
      [recipe.cx + recipe.rx, recipe.cy],
      [recipe.cx, recipe.cy + recipe.ry]
    ], { visible: vis, strokeColor: col, strokeWidth: w, fillOpacity: 0, highlight: false });
  }
  if (recipe.type === 'line') {
    const {a, b, c} = recipe;
    return board.create('line', [a, b, c], {
      visible: vis, strokeColor: col, strokeWidth: w, highlight: false
    });
  }
  if (recipe.type === 'hyperbola') {
    const s = recipe.transverse === 'y' ? -1 : 1;
    const f = (t) => recipe.cx + s * recipe.a * Math.cosh(t);
    const g = (t) => recipe.cy + recipe.b * Math.sinh(t);
    const left = board.create('curve', [(t) => recipe.cx - recipe.a * Math.cosh(t), g, board, -2.5, 2.5],
      { visible: vis, strokeColor: col, strokeWidth: w, highlight: false });
    const right = board.create('curve', [f, g, board, -2.5, 2.5],
      { visible: vis, strokeColor: col, strokeWidth: w, highlight: false });
    return { setAttribute(o) { left.setAttribute(o); right.setAttribute(o); } };
  }
  if (recipe.type === 'parabola') {
    const p = recipe.p, vx = recipe.vx, vy = recipe.vy;
    const axis = recipe.axis, dir = recipe.direction === '-' ? -1 : 1;
    return board.create('curve', [
      function (t) { return axis === 'x' ? vx + dir * t * t / (2 * p) : vx + t; },
      function (t) { return axis === 'x' ? vy + t : vy + dir * t * t / (2 * p); },
      board, -8, 8
    ], { visible: vis, strokeColor: col, strokeWidth: w, highlight: false });
  }
  if (recipe.type === 'parametric') {
    const xf = new Function('t', 'return (' + recipe.x + ');');
    const yf = new Function('t', 'return (' + recipe.y + ');');
    return board.create('curve', [(t) => xf(t), (t) => yf(t), board, recipe.tmin, recipe.tmax],
      { visible: vis, strokeColor: col, strokeWidth: w, highlight: false });
  }
  if (recipe.type === 'polar') {
    const rf = new Function('theta', 'return (' + recipe.r + ');');
    return board.create('curve', [
      (t) => rf(t) * Math.cos(t), (t) => rf(t) * Math.sin(t), board, recipe.tmin, recipe.tmax
    ], { visible: vis, strokeColor: col, strokeWidth: w, highlight: false });
  }
  if (recipe.type === 'implicit') {
    return board.create('implicitcurve', [recipe.expr], {
      visible: vis, strokeColor: col, strokeWidth: w, highlight: false
    });
  }
}
```

初始化：

1. `try/catch` 包住整个 board；失败则显示 `board-error`（中文「图形加载失败」，en 用 ui.boardError）
2. `JXG.JSXGraph.initBoard('jxgbox', { boundingbox: frameBB(model.frame), axis: true, grid: true, showCopyright: false, showNavigation: true, pan: {enabled:true}, zoom: {enabled:true} })`
3. 常驻：对 `model.plot_curves` 每条 `drawPlot(..., {strokeWidth:1, color: COLORS.frame, visible:true})`
4. 常驻点：`model.points` 每个 `board.create('point', [x,y], {name, size:2, strokeColor: COLORS.point, fillColor: COLORS.point, fixed:true, label:{fontSize:14}})`
5. 可切换：遍历 `model.elements`，按 type 创建，**默认 `visible:false`**，存进 `switchable[key]`
   - `point`：更大强调球 `center` 点名
   - `line`：两点或 `curve` 引用 `plot_curves`
   - `segment`：`segment`
   - `circle/ellipse/...`：用 `el.curve` 指向 plot_curves key，强调色粗线
   - `axes`：可创建一个空 group，或忽略（board 已有 axis）；仍要在 switchable 里放 `{setAttribute({visible})}` 以免 highlight 校验过了 JS 找不到
   - `focus`：点
   - `directrix`：直线
   - `arrow`：`arrow` from origin along dir
   - `measure`：中点标签，受总开关控制
   - `locus`：第一版可创建空对象（拖动任务再接）
6. `applyHighlight(keys)`：所有 switchable `visible=false`，再对 keys `visible=true`
7. 切步：左栏只显示当前 step 的 title/content；`applyHighlight(step.highlight)`；若有 `step.boundingbox` 则 `board.setBoundingBox`
8. 最后一步按钮文案「完成」：展开全部 `steps` 的 content，highlight = 各步 highlight 并集
9. 复位视野：回到 `model.frame`
10. 有任意 `type==measure` 才显示长度开关
11. 窄屏 CSS：`@media (max-width: 800px) { body 改为上讲解下画板；#jxgbox 高度 50vh }`

**不要实现拖动**（Task 12）。无 `draggable` 时隐藏 `#readouts`。

- [ ] **Step 3: 用 Task 8 的临时文件 build 流程生成 HTML，确认含 `jsxgraph` 和 `__LESSON_DATA__` 已替换**

```bash
.venv/bin/python engine/scripts/selftest.py
```

Expected: 全绿。用 Python 打开生成的 HTML，`check('jsxgraphcore.js' in html)` 加到 selftest。

- [ ] **Step 4: Commit**

```bash
git add engine/template/lesson.html engine/template/ui-en.json engine/scripts/selftest.py
git commit -m "feat: lesson template with JSXGraph step highlights"
```

---

### Task 10: `new_problem.py` + 根列表

**Files:**
- Create: `engine/scripts/new_problem.py`
- Create: `engine/scripts/rebuild_index.py`
- Create: `engine/template/index.html`
- Create: `index.html`（空列表初始）
- Modify: `engine/scripts/build.py`（成功后调用 write_index）
- Modify: `engine/scripts/selftest.py`

- [ ] **Step 1: `new_problem.py` 从 `/Users/zhangshengzhi/Documents/stereometry/engine/scripts/new_problem.py` 复制，删除 `--type random` 选项；`meta.json` 增加 `"tags": []`, `"title": null`, `"answer": null`。stdout 仍然只打印目录绝对路径。**

- [ ] **Step 2: selftest 在临时目录测 slug（把 `new_problem.PROBLEMS` 指向 tmp 不现实的话，测 `slugify` 纯函数）**

把 `slugify` / `next_id` 做成可 import。selftest：

```python
    from new_problem import slugify
    check(slugify("ex2-ellipse-chord") == "ex2-ellipse-chord", "slug ok")
    try:
        slugify("椭圆弦长")
        check(False, "zh slug should exit")
    except SystemExit:
        check(True, "zh slug rejected")
```

`slugify` 里用 `raise SystemExit(...)` 与立体几何一致。

跑 FAIL（无模块）→ 实现 → 绿。

- [ ] **Step 3: `rebuild_index.py`**

- `collect()`：扫描 `REPO/problems/*/meta.json`，目录名匹配 `^(\d{8})-(\d{2})-(.+)$`
- 若同目录无 `index.html`：`print("skip ... 无 index.html", file=sys.stderr)` 并 continue
- 读 meta 的 `id, slug, tags, title, answer, created, source_file`
- `label`：slug `exN` → `例题 N`，`exerN` → `习题 N`，否则 `演示`
- `href`: `problems/{id}/index.html`
- `write_index()`：读 `engine/template/index.html`，替换 `__PROBLEMS_JSON__` 为 `json.dumps(rows, ensure_ascii=False)`，写到 `REPO/index.html`
- 列表页从立体几何 `problems/index.html` 复制 CSS/结构，改标题为「解析几何题目」，`localStorage` 键 `analytical-geometry-theme`，筛选芯片：

```javascript
const KINDS = [
  { id: 'all', label: '全部' },
  { id: 'line-circle', label: '直线与圆' },
  { id: 'ellipse', label: '椭圆' },
  { id: 'hyperbola', label: '双曲线' },
  { id: 'parabola', label: '抛物线' },
  { id: 'parametric-polar', label: '参数与极坐标' }
];
```

过滤：`kind==='all' || (p.tags||[]).includes(kind)`。搜索 title/slug/answer/label。卡片上 `badge` 用 `label`，kicker 显示 tags 中文。

build 成功后：

```python
from rebuild_index import write_index
write_index()
```

并回写该题 `meta.json` 的 `tags=spec["tags"]`、`title`=去掉 HTML 的 lesson.title、`answer`=answerValue 或 answers 拼接。

- [ ] **Step 4: selftest：临时 REPO 不好做；改为 `collect` 在当前仓库能跑不抛错**

```python
    from rebuild_index import collect, write_index
    rows = collect()
    check(isinstance(rows, list), "collect list")
    write_index()
    root = (Path(__file__).resolve().parent.parent.parent / "index.html").read_text()
    check("__PROBLEMS_JSON__" not in root, "index placeholder filled")
    check("解析几何" in root, "index title")
```

此时 problems 可能为空，列表是 `[]`，仍然合法。

- [ ] **Step 5: Commit**

```bash
git add engine/scripts/new_problem.py engine/scripts/rebuild_index.py engine/template/index.html engine/scripts/build.py engine/scripts/selftest.py index.html
git commit -m "feat: allocate problem dirs and rebuild root index"
```

---

### Task 11: 文档与 Agent skill

**Files:**
- Create: `engine/references/api.md`
- Create: `engine/references/problem-schema.md`
- Create: `.cursor/skills/analytic-geometry-lesson/SKILL.md`
- Create: `AGENTS.md`
- Create: `README.md`

- [ ] **Step 1: 写 `api.md`**

必须包含：全部命令（new_problem / build / solve / selftest / rebuild_index）、单文件 `problem.json` 顶层四键、spec 全字段、§6.1 曲线表、§6.2 givens 表、§6.3 query 表、占位符表、`{{answer}}` 必须自带 `$`、自动补全字段列表、Agent 禁止手写 `model.points/plot_curves/frame/answerValue`、逃生 `implicit`+`custom`。从 spec 抄表，改成「读这一页就够」口吻，对标立体几何 `api.md`。命令写成：

```bash
.venv/bin/python engine/scripts/build.py problem.json out.html
```

- [ ] **Step 2: 写 `problem-schema.md`**

对标立体几何 schema：lesson/steps/model.elements 类型、颜色名、highlight 绝对集合、完成按钮、常驻 vs 可切换两层、`draggable` JSON、measure 例外、多问 `answers`、禁止默认四步、分类讨论分步。

- [ ] **Step 3: 写 skill + AGENTS.md + README**

skill 名称 `analytic-geometry-lesson`，description 含触发词：解析几何, 椭圆, 双曲线, 抛物线, 直线与圆, 离心率, 弦长, 焦点, 准线, 极坐标, 参数方程, 扫题, 拍照解题。

正文结构照抄立体几何 skill，替换 Three.js→JSXGraph、body→curves、cameraPos→boundingbox、禁止随机出题、根列表是仓库 `index.html`、缺 sympy 先问再装、只读 api.md 与 problem-schema.md。

`AGENTS.md` 四段：发题必须走 skill；一题一目录；照片多题拆开；highlight 不能空。

`README.md`：做什么、目录约定、命令、CDN 需联网、对照 stereometry。

- [ ] **Step 4: Commit**

```bash
git add engine/references .cursor/skills/analytic-geometry-lesson/SKILL.md AGENTS.md README.md
git commit -m "docs: add agent skill and kernel API reference"
```

---

### Task 12: 拖动与读数

**Files:**
- Modify: `engine/template/lesson.html`
- Modify: `engine/scripts/validate.py`（若 Task 7 已含 draggable 检查则跳过）
- Modify: `engine/scripts/selftest.py`

- [ ] **Step 1: 在模板 JS 中，当 `model.draggable` 存在：**

- 把 `draggable.point` 对应 JSXGraph 点改为 `fixed:false`
- `on` 是 `plot_curves` 的 key：用 `glider` 吸附到常驻曲线对象（初始化时给每条 plot_curves 存引用 `resident[key]`）
- `on` 是两点名 `[A,B]`：glider 在线段上
- 初始位置：用 `t0`（椭圆：`setPosition(1, [cx+rx*cos(t), cy+ry*sin(t)])`）。椭圆/圆用 `t` 为弧度；其它曲线用 `point_at` 的数学坐标（build 已把标准位写进 `math_points`）
- `sliders`：每个 `board.create('slider', [[xmin+0.5,ymax-0.6-i*0.5],[xmin+3, ymax-0.6-i*0.5], [min,value,max]])`，`name` 写入 `board.sliderValues`
- `dependent`：第一版只实现 `midpoint` 与 `ratio`（和 givens 相同），每次 `update` 重设坐标
- `readouts` 显示在 `#readouts`（取消 hidden）：
  - `length`：两点距离
  - `distance_point_line`：数值点到直线（直线两点或 abc）
  - `eccentricity`：从 `plot_curves[curve]` 的 rx,ry 算 `sqrt(|rx^2-ry^2|)/max(rx,ry)`
  - `area_triangle`：三点叉积一半绝对值
  - `chord_length`：若给了 `pts` 两点则用距离；若给 `line`+`curve` 第一版退化为当前 `A,B` 两点距离（示例题用 `pts`）
- 小数：`formatNum(x)` → 最多 4 位，能整除则短写
- `|t - t0| / max(1,|t0|) < 0.02` 时在读数区显示「标准位 ✓」（en：`standardMark`）
- **不**改左侧 innerHTML

椭圆 glider 的参数角用 `Math.atan2((y-cy)/ry,(x-cx)/rx)` 与 `t0` 比较。

- [ ] **Step 2: validate 已拒绝坏 draggable；selftest 加一条：build 带 draggable 的最小 spec，HTML 含 `draggable` 与 `readouts`**

用 Task 6 的 ellipse spec，`model.draggable = {point:"P", on:"C", t:"pi/3", standardLabel:"标准位 t=π/3", readouts:[{label:"弦长 AB", type:"length", pts:["A","B"]}]}`，elements 加 `Point_P`。

- [ ] **Step 3: selftest 全绿**

```bash
.venv/bin/python engine/scripts/selftest.py
```

- [ ] **Step 4: Commit**

```bash
git add engine/template/lesson.html engine/scripts/validate.py engine/scripts/selftest.py
git commit -m "feat: draggable points and live numeric readouts"
```

---

### Task 13: 椭圆弦长示例题 + 端到端验收

**Files:**
- Create: `problems/` 下由脚本分配的目录 + `problem.json`
- Modify: `engine/scripts/selftest.py`（可保持，不强制夹具进 problems）
- Modify: `engine/fixtures/pass-ellipse-chord.json`（build 用的完整 problem，供 selftest 不依赖日期目录）

- [ ] **Step 1: 写夹具 `engine/fixtures/pass-ellipse-chord.json`**

完整 `problem.json`（单文件）：

spec：`tags:["ellipse"]`，frame `[-6,6]×[-4,4]`，曲线 `C` 椭圆 a=2,b=1，直线 `l`：`a=1,b=-2,c=0`（即 \(x-2y=0\)），givens：`F` 右焦点，`A`/`B` 为 C∩l 的 right/left，`P` on_curve t=pi/3，`M` midpoint A,B；`lengths.AB`；query `chord_length` line=`l` curve=`C`。

lesson.meta：`交互解题 · 椭圆弦长`  
title：`椭圆 $\dfrac{x^{2}}{4}+y^{2}=1$ 与直线 $x-2y=0$ 交于 $A$、$B$，求弦 $AB$ 的长`  
answerLabel：`弦 $AB$ 的长`

steps（4 步，这是题型使然不是模板）：

1. 建系：内容含 `{{eq.C}}`、`{{mp.A}}`、`{{mp.B}}`；highlight `["Axis","Curve_C","Len_AB"]`  
2. 联立：直线方程 + 椭圆；highlight `["Line_AB","Point_A","Point_B"]`  
3. 弦长公式：`{{vals.len}}`；highlight `["Line_AB","Curve_C","Point_A","Point_B"]`  
4. 代入得 `${{answer}}$`；highlight 同 3（最后一步就是答案，不要第五步「写出答案」）

elements：`Axis` axes；`Curve_C` ellipse 引用 curve `C`；`Line_AB` line A,B emphasis；`Point_A/B/F/P/M`；`Len_AB` measure label `{{vals.len_AB}}`。

draggable：point `P` on `C`，t `pi/3`，readouts 弦长 AB。

- [ ] **Step 2: selftest build 该夹具到 tempfile，必须打印路径且 PASS；再 `new_problem.py ellipse-chord` + 把夹具复制为该目录 `problem.json` + build 到该目录 `index.html`**

```bash
DIR=$(.venv/bin/python engine/scripts/new_problem.py ellipse-chord)
cp engine/fixtures/pass-ellipse-chord.json "$DIR/problem.json"
.venv/bin/python engine/scripts/build.py "$DIR/problem.json" "$DIR/index.html"
```

Expected stdout 含 `PASS  已生成`，根 `index.html` 含 `ellipse-chord` 与 `\sqrt{10}`。

用浏览器打开 `$DIR/index.html`：切步高亮变化；拖 `P`；完成展开四步。若无浏览器工具，至少用 Python 断言 HTML 含 `jxgbox`、`\sqrt{10}`、`draggable`。

- [ ] **Step 3: `selftest.py` 增加：每种曲线 `make_curve` + 对应该 query 的 `solve` 一条（圆点线距、双曲线 e、抛物线 e=1、参数点、极坐标点、implicit 方程）。全部要绿。**

```bash
.venv/bin/python engine/scripts/selftest.py
```

Expected: `all passed`。

- [ ] **Step 4: Commit**

```bash
git add engine/fixtures/pass-ellipse-chord.json problems engine/scripts/selftest.py index.html
git commit -m "feat: add ellipse chord demo problem"
```

---

## Self-review vs spec

| Spec 节 | Task |
|---|---|
| 目标 / 非目标 | 全文；无 GeoGebra、无随机、无自绘引擎 |
| 目录与命名 | T1, T10 |
| 技术栈 | T1, T9 |
| problem.json 四键 | T8 |
| 曲线类型 8 种 | T3–T4, T13 补测 |
| givens | T6 |
| query 8 种 | T6, T13 |
| 占位符与 `$` / `\dfrac` | T2, T7, T8 |
| 常驻 vs highlight | T9 |
| draggable + 读数 + 标准位 | T12, T13 |
| 完成展开、不凑步 | T9, T13 示例 |
| 根列表筛选 | T10 |
| 照片拆题工作流 | T11 skill（实现期不拍照） |
| validate 15 条 | T7 |
| 求解失败不写文件 | T8 |
| 示例椭圆弦长 + 拖动 | T13 |
| api/schema/skill | T11 |

无 TBD。函数名全程：`solve` / `make_curve` / `intersect` / `chord_length` / `substitute` / `fill_defaults` / `build` / `validate` / `write_index` / `slugify`。
