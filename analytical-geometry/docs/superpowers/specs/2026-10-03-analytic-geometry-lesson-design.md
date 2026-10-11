# 高中解析几何交互解题页

日期：2026-10-03  
状态：待用户审阅  
对照：`/Users/zhangshengzhi/Documents/stereometry`（立体几何同构产品，3D/Three.js 换成 2D/JSXGraph）

## 1. 目标

把一道高中解析几何题做成可直接用浏览器打开的单页 HTML：

- 左：MathJax 分步解析（精确符号，sympy 计算）
- 右：JSXGraph 平面图（分步高亮；需要时动点可拖、参数可滑，实时小数读数）

题目来源：对话里的文字，或题目照片。一张图多道题时，每道题各一个目录、各一个网页。

学段范围（第一版只做这些）：

- 直线与圆
- 圆锥曲线（椭圆、双曲线、抛物线）
- 参数方程、极坐标

## 2. 非目标（第一版明确不做）

- 不嵌 GeoGebra
- 不自绘 Canvas/SVG 几何引擎
- 不做随机出题 / `generate.py`
- 不做大学空间解析几何、二次曲面、一般二次型理论
- 不提供空白画板式「自己加点线」
- 不做完整的带 \(xy\) 项旋转二次曲线引擎（这类题用方程字符串 + `query: custom` 逃生）

## 3. 目录

```
analytical-geometry/
  index.html                          # 根目录题目列表
  README.md
  AGENTS.md
  requirements.txt                    # sympy 等
  .cursor/skills/analytic-geometry-lesson/SKILL.md
  docs/superpowers/specs/             # 本设计
  engine/
    references/api.md                 # Agent 开工只读这个 + schema
    references/problem-schema.md
    template/lesson.html              # 左讲解 + 右 JSXGraph
    template/ui-en.json              # 仅英文界面；中文写在模板里
    lib/geometry_kernel.py            # 2D sympy
    lib/curves.py                     # 曲线对象与拓扑/默认点
    scripts/new_problem.py
    scripts/build.py
    scripts/solve.py
    scripts/validate.py
    scripts/selftest.py
    scripts/rebuild_index.py          # 扫描 problems/ 写根 index.html
  problems/YYYYMMDD-NN-slug/
    meta.json
    source.jpg                        # 仅拍照题，扩展名随原文件
    problem.json
    index.html
```

约定：

- 成品只写 `problems/` 与根 `index.html`，绝不写进 `engine/`
- `YYYYMMDD`：当天本地日期
- `NN`：当天序号，从 `01` 起，由 `new_problem.py` 分配，禁止手填
- `slug`：小写英文、数字、短横线，≤64 字符
  - 书上有编号：例题 N → `exN`，习题 N → `exerN`，再接对象+所求，如 `ex2-ellipse-chord`
  - 无编号自拟题：`ellipse-focal-chord`

## 4. 技术栈

| 层 | 选择 | 理由 |
|---|---|---|
| 讲解排版 | MathJax 3（CDN） | 与立体几何一致 |
| 2D 画板 | JSXGraph（CDN） | 点/直线/圆锥曲线/滑条/轨迹/拖动现成，步骤联动用 JS API |
| 精确计算 | Python 3 + sympy | 书面步骤与坐标同源 |
| 拖动读数 | 浏览器内数值计算（JS） | 只刷新图和读数，不改左侧步骤 |
| 成品形态 | 单页静态 HTML | 双击打开，不占端口 |

解释器优先 `.venv/bin/python`；没有虚拟环境再用 `python3`。缺 sympy 时先询问用户是否安装，同意后再在仓库根目录建 `.venv` 并 `pip install -r requirements.txt`。

## 5. 数据：`problem.json`

一个文件，顶层：

```jsonc
{
  "spec": { /* 题目结构，见 §6 */ },
  "lesson": { /* meta / title / answerLabel / 可选 answers */ },
  "steps": [ /* title / content / highlight / 可选 boundingbox */ ],
  "model": { /* elements / 可选 draggable */ }
}
```

也可拆成 `spec.json` + `lesson.json` 交给 `build.py`，默认工作流只用单文件。

`build.py` 自动补全、Agent **不要手写**的字段：

- `lesson.language`、`lesson.answerValue`（单问时 = `${{answer}}$`）、`lesson.ui`
- `model.points`（画板坐标）、`model.frame`、曲线的数值方程系数
- 有 `draggable` 时补 `model.mathPoints` 与标准位参数

Agent **必须手写**：`lesson.meta/title/answerLabel`、`steps[*]`、`model.elements`；多问再写 `lesson.answers`。

## 6. spec（题目结构）

解析几何没有立体几何那种单一「几何体」，场景是：坐标框 + 曲线 + 点。

```jsonc
{
  "language": "zh-CN",          // zh-CN | en；en 时注入英文 UI
  "tags": ["ellipse"],
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

### 6.1 曲线类型

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

### 6.2 givens.kind

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

### 6.3 query.type → `{{answer}}` 与 `vals`

统一建系 + 坐标/方程法。禁止心算，全部占位符。

| type | 必填 | 答案 | 主要 vals |
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

## 7. 占位符

| 占位符 | 内容 |
|---|---|
| `{{answer}}` | 最终答案 LaTeX，**不带** `$` |
| `{{mp.A}}` | 点 A 数学坐标，如 `(2, 0)` 或 `\left(\sqrt{2}, 1\right)` |
| `{{eq.C}}` | 曲线 C 的方程 LaTeX，不带 `$` |
| `{{vals.x}}` | query / lengths / vectors / custom 产出的量 |
| `{{vals.len_AB}}` / `{{vals.vec_AB}}` | spec 里声明的长度/向量 |

规则（与立体几何相同，校验强制）：

- 占位符不自带 `$`。步骤里写 `"${{answer}}$"`。
- 任何字段里落在 `$…$` / `$$…$$` 之外的 LaTeX 命令（`\dfrac` 等）直接 FAIL。
- 唯一例外：`measure.label` 由模板补 `$`，那里不要写 `$`。
- 分数一律 `\dfrac`，禁止 `\frac` / `\tfrac`。
- 占位符拼错：FAIL，并列出可用键。

## 8. 讲解与画板模型

字段细节落在 `engine/references/problem-schema.md`，此处锁行为。

### 8.1 lesson

- `meta`：顶部小标签，如 `交互解题 · 椭圆弦长`
- `title`：题面，可含 `$…$` 与 `<br>`；小问之间用 `<br>` 分行
- `answerLabel`：答案卡说明
- 多问必须 `answers: [{label, value}, …]`，此时不要写 `answerValue`
- 单问不要把多个结论用 `；` 塞进 `answerValue`（校验拦截）

### 8.2 steps

每步：`title`, `content`（HTML 段落）, `highlight`（字符串数组，绝对集合，不能空）, 可选 `boundingbox` `[xmin,ymax,xmax,ymin]`（JSXGraph 顺序，覆盖该步视野；默认用 `spec.frame`）。

步骤规则：

- 步数跟推理走，常见 3～7 步。禁止为整齐默认写成四步。
- 算出答案（或列完所有情形）的那一步就是最后一步。禁止再加只重复答案的「写出 xxx」步。
- 分类讨论、两种斜率、两种焦弦：每种构型有自己的点/线/曲线，单独成步，`highlight` 只点亮该款。
- 最后一步按钮文案是「完成」：左侧按顺序紧凑展开已有步骤（不另写综述），右侧点亮各步用过的可切换元素之并集。

建系步必须出现：坐标轴元素、关键点 `{{mp.*}}`、已知曲线 `{{eq.*}}`、题面给出的长度 `measure`。

### 8.3 model.elements 类型

| type | 字段 | 用途 |
|---|---|---|
| `point` | `center` 点名 | 强调点球（中点、垂足、交点） |
| `line` | `a`,`b` 点名，或 `curve` 引用无穷直线 | 弦、切线、辅助线 |
| `segment` | `a`,`b` | 有限线段 |
| `circle` / `ellipse` / `hyperbola` / `parabola` / `implicit` | 引用 `curves` 的 key，或内联参数 | 已知曲线 / 轨迹 |
| `polar` / `parametric` | 同上 | 参数/极坐标曲线 |
| `axes` | `size` 或跟随 frame | 一般只在建系步 highlight |
| `focus` / `directrix` | `of` 曲线, `which` | 焦点、准线 |
| `arrow` | `origin`, `dir`, `length` | 向量 |
| `measure` | `a`,`b`, `label` | 长度标注 |
| `locus` | `point`, `mover` | 动点轨迹（可选，有拖动时） |

颜色语义名与立体几何对齐：`frame` · `aux` · `emphasis` · `normal` · `curve`（圆锥曲线主色）· `point`。

所求直线/弦：`emphasis`。辅助线：`aux` + `dashed`。已知圆锥曲线：常驻或按步显示，主色 `curve`。

`highlight` 拼错的键：`build.py` FAIL（模板不得静默忽略）。

绘制分两层，对标立体几何的「骨架 vs 可切换元素」：

- **常驻**：坐标网格、`spec.curves` 里的已知曲线（浅色、细线）、`spec.points` 里的命名点（小圆点）。不必写入 `highlight`。
- **可切换**：只来自 `model.elements`。被当前步 `highlight` 点名则显示（强调色/加粗/焦点准线/弦/标注）；未点名则隐藏。

因此：椭圆本身会一直在；要「点亮这条椭圆」时，再在 `elements` 里放一个同曲线的强调副本（例如 `Curve_C`），把它列入该步 `highlight`。

### 8.4 动点与滑条

```jsonc
"draggable": {
  "point": "P",
  "on": "C",                 // 曲线 key 或两点线段
  "t": "pi/3",               // 标准位
  "standardLabel": "标准位 t=π/3",
  "sliders": [
    { "name": "k", "min": -5, "max": 5, "value": 1, "label": "斜率 k" }
  ],
  "dependent": [
    { "name": "M", "kind": "midpoint", "of": ["A", "P"] }
  ],
  "readouts": [
    { "label": "弦长 AB", "type": "length", "pts": ["A", "B"] },
    { "label": "离心率", "type": "eccentricity", "curve": "C" }
  ]
}
```

- 拖动只改 JSXGraph 图形与读数（小数，最多 4 位，能化成短小数的用短小数）
- 靠近标准位（参数相对误差 &lt; 2%）显示「标准位 ✓」
- 左侧步骤始终对应标准位精确值，文案不随拖动改写
- readout `type` 第一版：`length`、`distance_point_line`、`eccentricity`、`area_triangle`、`chord_length`
- 无 `draggable` 的题：画板纯展示 + 切步高亮，不出现滑条区

## 9. 页面行为

### 9.1 单题页

- 视觉：沿用立体几何的浅色/深色主题、字体（Instrument Sans + Noto Sans SC + JetBrains Mono）、答案卡、步骤按钮
- 左栏：题面（过长缩小字号，最多约三成屏高后滚动）→ 答案卡 → 当前步骤；「完成」后按序展开全部步骤
- 右栏：JSXGraph；可平移、滚轮缩放、复位视野
- 存在任一 `measure` 时，画板左上「长度标注：开/关」
- 坐标网格：一格 = 数学坐标 1 个单位，便于读点
- 不做绕飞镜头；切步至多改 `boundingbox`
- 窄屏：左上右下，画板固定高度（约 50vh），不被步骤挤没

CDN：MathJax 与 JSXGraph 用稳定 CDN。无网时页面公式与画板不可用，第一版不打本地 vendor（在 README 注明）。

### 9.2 根目录列表

路径固定为仓库根 `index.html`（不是 `problems/index.html`）。

每张卡片：日期序号、题型标签、题面摘要、答案（MathJax）、链到该题 `index.html`。

- 搜索：题面、slug、标签
- 筛选芯片：全部 / 直线与圆 / 椭圆 / 双曲线 / 抛物线 / 参数与极坐标
- 题型标签来自 `spec.tags`（字符串数组，取值必须是：`line-circle`、`ellipse`、`hyperbola`、`parabola`、`parametric-polar` 之一或多）。`new_problem.py` 生成的 meta 里 `tags` 为空；`build.py` 把 `spec.tags`、题面纯文本、答案写入 meta 供列表使用。缺 `spec.tags` 则 FAIL。

`build.py` 成功后调用 `rebuild_index.py` 扫描全部 `problems/*/meta.json` + 已生成的答案摘要，重写根列表。删题目录后再跑 rebuild 即可，不手改列表 HTML。

`meta.json` 字段：

```jsonc
{
  "id": "20261003-01-ex2-ellipse-chord",
  "slug": "ex2-ellipse-chord",
  "created": "2026-10-03T19:00:00+08:00",
  "source_type": "text" | "image",
  "source_file": "source.jpg" | null,
  "tags": ["ellipse"],
  "title": "……纯文本摘要……",
  "answer": "……纯文本或轻量 LaTeX……"
}
```

`title` / `answer` / `tags` 在 build 成功时写入，供列表使用。

## 10. Agent 工作流

入口归一到 spec。输出语言跟随用户：英文提示则 `"language": "en"`，title/steps 用英文。

### 10.1 文字题

抽取曲线、点、尺寸、所求 → 分配目录 → 写 `problem.json` → build。多道题同样拆目录。

### 10.2 照片

1. 按题号拆开（例题 / 习题 / （1）（2）若是独立大题也拆；同一大题的小问留在同一页，用 `answers`）
2. 每道把题面、曲线、尺寸、所求**逐条回显**给用户确认
3. 确认后每道单独 `new_problem.py <slug> --source <原图>`
4. 逐题写 `problem.json` 并 build，不得合页，不得只做其中一题就停

### 10.3 命令

```bash
.venv/bin/python engine/scripts/new_problem.py <slug> [--source <原图>]
.venv/bin/python engine/scripts/build.py "$DIR/problem.json" "$DIR/index.html"
.venv/bin/python engine/scripts/solve.py  "$DIR/problem.json"     # 只看答案
.venv/bin/python engine/scripts/selftest.py                       # 引擎回归
.venv/bin/python engine/scripts/rebuild_index.py                  # 必要时单独刷新列表
```

`new_problem.py` stdout **只有**新建目录的绝对路径。

`build.py`：求解 + 渲染 + 自检。`PASS 已生成: …` 才写文件并刷新列表；`FAIL` 列出全部问题，不写 HTML。

Agent 只读 `engine/references/api.md` 与 `problem-schema.md`，不要读 `template/` 与 `lib/`、`scripts/` 源码来「猜」格式。维护内核时才改 Python，改完跑 selftest，解题流程里不跑 selftest。

缺依赖：先问用户，同意再装。交付：报每题 `problems/…/index.html` 路径。不要留下占用端口的本地服务。

## 11. 校验（FAIL 条件）

`validate.py` 在写出 HTML 前跑，问题全部列出：

1. JSON 结构缺 `spec` / `lesson` / `steps` / `model`
2. `steps` 为空，或任一步缺 `title`/`content`/`highlight`
3. 任一步 `highlight` 为空数组
4. `highlight` 中的键在 `model.elements` 中不存在
5. 占位符未知键
6. 定界符外的 LaTeX 命令
7. 使用 `\frac` / `\tfrac`
8. 题面含多个小问编号但没有 `lesson.answers`
9. 同时存在 `answers` 与过长的 `answerValue`
10. `query.type` 未知且不是 `custom`
11. `custom` 缺少 `expr` 与 `vals`
12. 曲线参数不合法（椭圆 \(a,b\le 0\) 等）
13. 交点 `which` 在多解时缺失
14. `draggable.point` 不在点表，或 `on` 无法参数化
15. 缺少 `spec.tags`，或含有未允许的标签

selftest 覆盖：每种曲线至少一题能 `solve` 出干净 sympy 答案；`build` 对内置夹具 `PASS`；占位符拼错与空 highlight 必须 FAIL。夹具放 `engine/fixtures/`，不放进 `problems/`（避免污染列表）。

## 12. 错误处理

- 求解失败（无交点、方程无解）：`build.py` FAIL，说明哪条曲线/哪条 query，不生成「空白图」
- JSXGraph 运行时错误：单题页捕获后在画板区显示简短中文错误，不白屏
- 列表扫描遇到缺 `index.html` 的目录：跳过并在控制台警告，不把坏卡片写进列表

## 13. 与立体几何的对应关系

| 立体几何 | 本项目 |
|---|---|
| Three.js 3D | JSXGraph 2D |
| `body` + `dims` | `curves` + `points` + `frame` |
| `cameraPos` | 可选 `boundingbox` |
| 地平面网格 | 坐标网格（1 格 = 1 单位） |
| 5 种空间 query | §6.3 的平面 query + `custom` |
| `problems/index.html` | 仓库根 `index.html` |
| 随机出题 | 不做 |

Agent 技能名：`analytic-geometry-lesson`。触发词包括：解析几何、椭圆、双曲线、抛物线、直线与圆、离心率、弦长、焦点、准线、极坐标、参数方程、扫题、拍照解题。

## 14. 实现顺序（供计划拆分，不是本 spec 的验收范围）

1. 仓库骨架、skill、api/schema 空文档、requirements
2. 内核：点、直线、圆、椭圆 + 2～3 个 query + 占位符
3. 模板：左栏 + JSXGraph 切步高亮
4. `new_problem.py` / `build.py` / `validate.py` / 根列表
5. 双曲线、抛物线、参数/极坐标、`custom`
6. `draggable` + readouts
7. selftest 夹具与一道示例题（椭圆弦长）写入 `problems/`，证明端到端

第一版验收（计划执行完毕时）：

- §6.1 全部曲线类型与 §6.3 全部 query 能在 selftest 里 `solve` 出干净符号答案
- 至少一道完整椭圆弦长示例写入 `problems/`：`build.py` PASS，根列表可点进该题
- 该示例含 `draggable`：动点在椭圆上，读出弦长，标准位有标记
- 用户之后只发照片/文字即可按 skill 加题，不必再改引擎

引擎未完成前不要接收生产题目；示例题由实现计划最后一步写入，不在本设计阶段手造。
