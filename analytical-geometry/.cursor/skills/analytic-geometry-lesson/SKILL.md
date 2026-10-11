---
name: analytic-geometry-lesson
description: >-
  把一道高中解析几何题解成自包含交互教学网页：左侧 MathJax 分步解析，右侧 JSXGraph
  平面图（分步高亮；需要时动点可拖、参数可滑）。支持文字题目、题目照片识别。
  覆盖直线与圆、椭圆、双曲线、抛物线、参数方程与极坐标上的离心率、弦长、
  焦点准线、点线距等，统一「建系+坐标/方程法」，sympy 精确计算（答案、坐标、
  方程、步骤数值同源）。触发词：解析几何, 椭圆, 双曲线, 抛物线, 直线与圆,
  离心率, 弦长, 焦点, 准线, 极坐标, 参数方程, 扫题, 拍照解题; analytic geometry,
  ellipse, hyperbola, parabola.
---

# 解析几何解题 → 交互网页（一题一目录）

产出可直接用浏览器打开的单页 HTML：左题面/答案/分步解析（MathJax），
右平面图（JSXGraph，可平移缩放，分步高亮）。题目列表在仓库根 `index.html`。

引擎在仓库 `engine/`。成品一律写到 `problems/`，**绝不写进 `engine/`**。
解释器优先用 `.venv/bin/python`（没有虚拟环境再用 `python3`）。
不做随机出题，没有 `generate.py`。

## 只读这两个文件

- `engine/references/api.md` —— spec 格式、曲线类型、query 题型、占位符、命令。**开工前读它。**
- `engine/references/problem-schema.md` —— lesson.json 的字段与元素类型。写讲解时读它。

**不要读** `engine/template/lesson.html`、`engine/lib/*.py`、`engine/scripts/*.py`——
`api.md` 全都写清楚了。英文界面文案会自动注入。

## 目录与命名

```
problems/YYYYMMDD-NN-slug/
  meta.json       # 分配目录时自动生成
  source.jpg      # 仅拍照题：原图（扩展名随原文件）
  problem.json    # 你写的 spec + 讲解
  index.html      # build.py 生成
```

- `YYYYMMDD`：当天日期（本地时区）
- `NN`：当天序号，从 `01` 起，由脚本分配，不要手填
- `slug`：**只用英文**（小写字母、数字、短横线），≤64 字符。
  书上有编号：`例题N` → `exN`，`习题N` → `exerN`，再接对象+所求。
  例：`ex2-ellipse-chord`、`exer3-hyperbola`。
  无编号的自拟/演示题：`ellipse-focal-chord`。

分配目录（有原图就带上 `--source`）：

```bash
.venv/bin/python engine/scripts/new_problem.py <slug> [--source <原图路径>]
```

stdout 只有新建目录的绝对路径。先跑这一条，再把 `problem.json` 写进该目录。

## 流程

### 0. 两种入口归一到 spec

- **文字题目**：直接抽取。多道题同样一题一目录。
- **图片 / 对话窗口照片**：**一张图经常有多道题**（例题1、例题2、习题…）。必须：
  1. 按题号拆开（例题 / 习题 / （1）（2）若是独立大题也拆；同一大题的小问留在同一页，用 `answers`），把每一道的题面 / 曲线 / 尺寸 / 所求**逐条回显**给用户确认；
  2. 确认后**每一道单独一个目录**，slug 带 `ex1` / `ex2` / `exer3` 等编号；
  3. 同一张原图对每道题都传 `--source`（各目录各存一份 `source`）；
  4. 逐题写 `problem.json` 并出图，不要把多道题塞进同一个 HTML，也不要只解其中一道就停。

输出语言跟随提示词：英文提示则 spec 里 `"language": "en"`，`title` / `steps` 用英文写。

### 建系：坐标轴、方程、关键点

建系步必须出现：

- 坐标轴元素（`axes`）
- 关键点坐标 `{{mp.*}}`
- 已知曲线方程 `{{eq.*}}`
- 题面给出的长度：spec 的 `lengths` 声明，再加 `measure` 元素，放进建系步的 `highlight`

抛物线用人口教版 \(y^2=2px\)（字段 `p`），不要写成 \(y^2=4ax\)。
椭圆的 `a` 是沿 `axis` 方向的半轴长，**不要求** \(a>b\)。

### 每步高亮点、线、曲线

每一步的 `highlight` **必须**点亮该步正文里出现的关键点、直线、曲线（绝对集合，不能空）。
- 线 / 弦 / 焦点 / 准线 / 长度 / 强调曲线：写进 `model.elements` 再列入 `highlight`
- 中点、垂足、交点等要点：`{ "type": "point", "center": "E" }`，键名 `Point_E`
- 网格、已知曲线浅线、命名点小圆本来就在（常驻），不必整副坐标系都列；本步新用到的对象一定要亮
- 要「点亮这条椭圆」时，在 `elements` 里放一个同曲线的强调副本（如 `Curve_C`）再列入 `highlight`

### 步骤数跟推理走，不要凑成固定步数

讲解有几步由题目本身决定，常见是 3～7 步，**禁止为了整齐而默认写成四步**。
- 该拆就拆：分类讨论、两种斜率、两种焦弦，各自独立成步。
- 不该凑就不凑：算出答案的那一步就是最后一步，**不要再加一个只重复「所以答案是 …」的「写出 xxx」步**。

### 多种情况都要画出来

答案是「或」、取值范围、所有可能值，或推理里出现两种斜率、两种焦弦这类分款时：

- **每一种构型都有自己的点/线/曲线**（如 \(k_1\)/\(k_2\)、\(M\)/\(M'\)），并配齐元素
- **每一种构型单独一步**，`highlight` 只点亮该款
- 不要只画「其中一种」然后用文字带过其它情况

### 完成：展开完整过程

最后一步按钮是「完成」。点下去后左侧按顺序、紧凑展开全部步骤（就是已有讲解，不要再写一篇综述），右侧同时点亮各步用过的可切换元素。最后一步就是算出答案（或列完所有情形）的那一步，不要再抄一遍前面的讲解。

### 1. 写 `problem.json`

顶层四个键：`spec` + `lesson` / `steps` / `model`。格式见 `api.md`。

- 所有数值用占位符（`{{answer}}` / `{{vals.len}}` / `{{mp.A}}` / `{{eq.C}}`），不要心算、不要手抄。
- `model.points` / `model.plot_curves` / `model.frame` / `lesson.answerValue` **不用写**。
- 多问题目：小问之间用 `<br>` 分行，答案用 `lesson.answers` 逐问列出。
- 占位符不自带 `$`：写成 `"${{answer}}$"`。`measure.label` 例外，不要写 `$`。
- 分数、分式一律 `\dfrac{…}{…}`，不要 `\frac` / `\tfrac`。

### 2. 出图 + 自检

```bash
.venv/bin/python engine/scripts/build.py "$DIR/problem.json" "$DIR/index.html"
```

打印 `PASS` 即通过；`FAIL` 时按列出的问题改 `problem.json` 重跑，不要起服务截图排查。

缺 `sympy` 时**先询问用户是否安装**，同意后再在仓库根目录建 `.venv` 并 `pip install -r requirements.txt`。

### 3. 交付

告诉用户每一道题的 `problems/YYYYMMDD-NN-slug/index.html` 路径，可直接用浏览器打开。
根列表是仓库根 `index.html`（`build.py` 成功后会刷新）。不要留下占用端口的本地服务。

## 维护

加曲线类型 / query：改 `engine/lib/` 与 `engine/scripts/solve.py`，并更新
`engine/references/api.md`。改完跑
`.venv/bin/python engine/scripts/selftest.py`（解题流程里不要跑）。
