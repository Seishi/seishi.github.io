# API 速查（读这一页就够，不要去读 lib/ 和 scripts/ 的源码）

## 命令

```bash
.venv/bin/python engine/scripts/new_problem.py <slug> [--source <原图>]  # 分配目录，stdout 只有绝对路径
.venv/bin/python engine/scripts/build.py problem.json out.html          # 求解+渲染+自检，一步到位
.venv/bin/python engine/scripts/solve.py  problem.json                  # 可选：只看答案和中间量
.venv/bin/python engine/scripts/selftest.py                             # 引擎回归（解题流程里不要跑）
.venv/bin/python engine/scripts/rebuild_index.py                        # 必要时单独刷新根列表
```

`problem.json` 一个文件搞定，顶层结构是 `{ "spec": {…}, "lesson": {…}, "steps": […], "model": {…} }`：
`spec` 是题目结构（下一节），其余是讲解内容。也可拆成两个文件：
`build.py spec.json lesson.json out.html`。默认工作流只用单文件。

`new_problem.py` stdout **只有**新建目录的绝对路径。先跑这一条，再把 `problem.json` 写进该目录。

`build.py` 成功打印 `PASS 已生成: …` 并刷新仓库根 `index.html`；有问题打印 `FAIL` 并列出每个问题，**不写出文件**。

## spec —— 题目结构

```jsonc
{
  "language": "zh-CN",          // zh-CN | en；en 时英文界面文案自动注入
  "tags": ["ellipse"],          // 必填，取值见下
  "frame": {                    // JSXGraph boundingbox，数学坐标
    "xmin": -6, "xmax": 6, "ymin": -4, "ymax": 4
  },
  "curves": {
    "C": { "type": "ellipse", "a": 2, "b": 1, "center": [0, 0], "axis": "x" }
  },
  "points": {
    "A": [2, 0],
    "B": ["sqrt(2)", 1]
  },
  "givens": [
    { "name": "F", "kind": "focus", "of": "C", "which": "right" },
    { "name": "M", "kind": "midpoint", "of": ["A", "B"] },
    { "name": "P", "kind": "on_curve", "curve": "C", "t": "pi/3" }
  ],
  "lengths": { "AB": ["A", "B"] },
  "vectors": { "AB": ["A", "B"] },
  "query": { "type": "chord_length", "line": ["A", "B"], "curve": "C" }
}
```

坐标与尺寸一律可写数或 sympy 字符串（`"1/2"`、`"sqrt(3)"`、`"pi/3"`）。不要在 spec 里写小数近似值，除非题面就是小数。

`tags` 必填，取值必须是这些之一或多：`line-circle`、`ellipse`、`hyperbola`、`parabola`、`parametric-polar`。缺了或写了别的都会 FAIL。

### 曲线类型（`curves` 的 type）

| type | 必填 | 默认含义 | 自动带出的点（可被 givens/highlight 引用） |
|---|---|---|---|
| `line` | `points` 两点名，或 `a,b,c`（\(ax+by+c=0\)） | 无限直线 | — |
| `circle` | `center`（点名或坐标）, `radius` | \((x-h)^2+(y-k)^2=r^2\) | 圆心若未命名则用曲线 key |
| `ellipse` | `a`, `b`, `center`, `axis`=`x`\|`y` | `a` 是沿 `axis` 方向的半轴长，`b` 是另一方向半轴长，**不要求** \(a>b\)。`axis=x` 时方程 \(\dfrac{(x-h)^2}{a^2}+\dfrac{(y-k)^2}{b^2}=1\) | 顶点、焦点名由 givens 声明，不自动污染点表 |
| `hyperbola` | `a`, `b`, `center`, `transverse`=`x`\|`y` | 标准焦点在对应轴 | 同上 |
| `parabola` | `p`（焦点到准线距离，人教版）, `vertex`, `axis`=`x`\|`y`，`direction`=`+`\|`-` | 顶点在原点、`axis=x`、`direction=+` 时为 \(y^2=2px\)，焦点 \((p/2,0)\)，准线 \(x=-p/2\)。禁止再用 \(y^2=4ax\) 那套 `a` | 同上 |
| `parametric` | `x(t)`, `y(t)` 字符串, `tmin`, `tmax` | 高考参数方程 | — |
| `polar` | `r(theta)` 字符串，可选 `e`, `p` 的圆锥曲线极坐标 | 极点在原点 | — |
| `implicit` | `expr` 字符串 \(F(x,y)=0\) | 逃生：一般二次曲线、轨迹 | — |

平移用 `center` / `vertex`。第一版不做自动转轴；带 \(xy\) 项用 `implicit`。

### givens.kind

| kind | 字段 | 结果 |
|---|---|---|
| `point` | `at`: [x,y] | 显式点（与顶层 `points` 等价，写在 givens 也可以） |
| `midpoint` | `of`: 两点 | 中点 |
| `ratio` | `of`: 两点, `t` | \(P=A+t(B-A)\) |
| `intersection` | `of`: 两条曲线 key，可选 `which` | 交点；多交点必须 `which`（`0`/`1` 或 `left`/`right`/`upper`/`lower`） |
| `foot` | `point`, `line` | 点到直线垂足 |
| `focus` | `of` 曲线, `which`: `left`\|`right`\|`upper`\|`lower` | 焦点 |
| `vertex` | `of` 曲线, `which` | 顶点 |
| `on_curve` | `curve`, `t`，双曲线另需 `which`=`right`\|`left`（默认 `right`） | 圆/椭圆：从 `axis` 正方向起的参数角（弧度）。抛物线：`axis=x` 时 \(t\) 为点的纵坐标，\(x=t^2/(2p),\ y=t\)，再按顶点与 `direction` 平移反射；`axis=y` 时 \(t\) 为横坐标。双曲线（横轴）：右支 \(x=a\cosh t,\ y=b\sinh t\)，左支 \(x=-a\cosh t\)，\(t\in\mathbb{R}\)（不用 \(\sec/\tan\)，避免拖动奇点）。参数方程曲线：用自身 \(t\) |
| `on_line` | `line`（两点或曲线 key）, `t` | 线段参数 \(t\in\mathbb{R}\) |

### query.type 与它产出的 `vals` 键

统一走「建系 + 坐标/方程法」。**不要心算任何数值**，全部用占位符引用下表的 `vals`。

| type | 必填字段 | 答案 | 主要 vals |
|---|---|---|---|
| `point_line_distance` | `point`, `line`（两点或 a,b,c） | 距离 | `a,b,c,dist` |
| `line_line_angle` | `line1`, `line2` | 锐角的正弦或余弦（题面要什么写什么，字段 `output`: `sin`\|`cos`\|`tan`\|`degree`，默认 `cos`） | `d1,d2,dot,cos,…` |
| `chord_length` | `line`, `curve` | 弦长 | `k` 或方向, `delta`, `len` |
| `eccentricity` | `curve` | \(e\) | `a,b,c,e` |
| `focal_radius` | `curve`, `point` | 焦半径 | `r` |
| `area_triangle` | `pts` 三点 | 面积 | `S` |
| `intersection` | `curve1`, `curve2` | 交点坐标（单点或用 `answers` 列出） | `pts` |
| `custom` | `expr`（sympy 字符串）或 `vals` 对象（命名表达式） | `expr` 的化简结果 | 自定义键 |

多问题目：`query` 仍可只表达「主问」给 `{{answer}}`；其余小问用 `custom.vals` 或 `lesson.answers` 里写死占位符（占位符必须来自 `vals`，不能手填数字）。多问更干净的做法：`query.type = "custom"` 且 `vals` 里列出每问表达式，`answers[].value` 引用它们。

## lesson / steps / model —— 讲解内容

字段含义见 `problem-schema.md`。**所有数值一律用占位符**，不要自己算、也不要抄：

| 占位符 | 内容 |
|---|---|
| `{{answer}}` | 最终答案的 LaTeX（**不带** `$`） |
| `{{mp.A}}` | 点 A 的数学坐标，如 `(2, 0)` 或 `\left(\sqrt{2}, 1\right)` |
| `{{eq.C}}` | 曲线 C 的方程 LaTeX，不带 `$` |
| `{{vals.x}}` | query / lengths / vectors / custom 产出的量 |
| `{{vals.len_AB}}` / `{{vals.vec_AB}}` | spec 里 `lengths` / `vectors` 声明的量 |

行内替换（`"$C: {{eq.C}}$"`），整串就是一个占位符时会还原成原始对象。占位符拼错会直接报错并列出可用键。

> ⚠️ **占位符展开的是裸 LaTeX，不带 `$`。** 自己把定界符写上：`"${{answer}}$"`，
> 不是 `"{{answer}}"`——后者会原样显示成 `\dfrac{\sqrt{2}}{2}`。
> 任何字段里落在 `$…$` / `$$…$$` 之外的 LaTeX 命令都会被校验拦下。
> 例外：`measure` 元素的 `label` 由模板自动补 `$`，那里写 `"{{vals.len_AB}}"` 即可。
> 分数一律 `\dfrac`，禁止 `\frac` / `\tfrac`。

### build.py 自动补全的字段（**能省则省，不要手写**）

`model.points`（画板坐标）、`model.plot_curves`（曲线的数值方程系数）、`model.frame`、
`lesson.language`、`lesson.answerValue`（单问时 = `${{answer}}$`）、英文 `lesson.ui`；
有 `model.draggable` 时还会补 `model.mathPoints` 与标准位参数。

你**必须**手写的只有：`lesson.meta/title/answerLabel`、`steps[*]`（title/content/highlight、可选 boundingbox）、
`model.elements`。多问再写 `lesson.answers`。

**不要手写** `model.points`、`model.plot_curves`、`model.frame`、`lesson.answerValue`。
`spec.points` / `spec.frame` / `spec.curves` 照常写——那是题目结构，不是画板模型。

**每一步 `highlight` 必须点亮该步正文里的关键点、直线、曲线**（绝对集合，不能空）。
中点/垂足/交点等要点用 `{"type":"point","center":"E"}`，键名 `Point_E`。详见 `problem-schema.md`。
最后一步点「完成」由模板展开全部步骤；算出答案的那一步就是最后一步，不要再加「写出答案」凑步数。
步骤数跟推理走，**不要默认四步**。分类讨论的每一种构型都要有自己的点线曲线，并单独成步、单独高亮。

## 逃生通道：spec 表达不了的题

**先试 `curves` 里的标准类型。** 一般二次曲线、带 \(xy\) 项、轨迹：曲线用
`"type": "implicit", "expr": "x**2 + x*y + y**2 - 1"`。
所求不属于上表 8 类 query 时，用 `"query": {"type": "custom", "expr": "…"}`，
或多问 `"query": {"type": "custom", "vals": {"q1": "…", "q2": "…"}}`。
**不要为此去写 Python**，也不要手填数字。
