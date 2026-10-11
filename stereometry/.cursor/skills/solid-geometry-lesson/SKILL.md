---
name: solid-geometry-lesson
description: >-
  把一道立体几何题解成自包含交互教学网页：左侧 MathJax 分步解析，右侧 Three.js
  可交互 3D 模型（分步高亮 + 镜头切换）。支持文字题目、题目照片识别、随机出题。
  覆盖正方体/长方体、棱锥/棱柱、圆柱/圆锥上的线面角、二面角、异面直线夹角、
  点到平面距离、体积等，统一「建系+向量法」，sympy 精确计算（答案、3D 坐标、
  步骤数值同源）。触发词：立体几何, 线面角, 二面角, 异面直线, 点到平面距离,
  正四棱锥, 正方体求角, 解这道几何题, 随机出一道立体几何题, 这张图里的立体几何题,
  扫题, 拍照解题; solid geometry, line-plane angle, dihedral angle.
---

# 立体几何解题 → 交互网页（一题一目录）

产出可直接用浏览器打开的单页 HTML：左题面/答案/分步解析（MathJax），
右 3D 模型（Three.js，可旋转缩放，分步高亮 + 切镜头）。

引擎在仓库 `engine/`。成品一律写到 `problems/`，**绝不写进 `engine/`**。
解释器优先用 `.venv/bin/python`（没有虚拟环境再用 `python3`）。

## 只读这两个文件

- `engine/references/api.md` —— spec 格式、query 题型、占位符、命令。**开工前读它。**
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
  书上有编号：`例题N` → `exN`，`习题N` → `exerN`，再接几何体+所求。
  例：`ex2-pc-min`、`ex1-tetra-plane-set`、`exer3-dihedral`。
  无编号的自拟/演示题：`pyramid-be-pac`。

分配目录（有原图就带上 `--source`）：

```bash
.venv/bin/python engine/scripts/new_problem.py <slug> [--source <原图路径>]
```

stdout 只有新建目录的绝对路径。先跑这一条，再把 `problem.json` 写进该目录。

## 流程

### 0. 三种入口归一到 spec

- **文字题目**：直接抽取。多道题同样一题一目录。
- **图片 / 对话窗口照片**：**一张图经常有多道题**（例题1、例题2、习题…）。必须：
  1. 按题号拆开，把每一道的题面 / 几何体 / 尺寸 / 所求**逐条回显**给用户确认；
  2. 确认后**每一道单独一个目录**，slug 带 `ex1` / `ex2` / `exer3` 等编号；
  3. 同一张原图对每道题都传 `--source`（各目录各存一份 `source`）；
  4. 逐题写 `problem.json` 并出图，不要把多道题塞进同一个 HTML，也不要只解其中一道就停。
- **随机出题**：分配目录后一条命令出图，流程到此结束：

```bash
DIR=$(.venv/bin/python engine/scripts/new_problem.py random --type random)
.venv/bin/python engine/scripts/generate.py random <seed> "$DIR/index.html"
```

输出语言跟随提示词：英文提示则 spec 里 `"language": "en"`，`title` / `steps` 用英文写。

### 建系：棱锥底面必须水平

遇到 $P$-$ABC$、$P$-$ABCD$ 这类棱锥（四面体 $ABCD$ 看成 $D$-$ABC$）：

- **底面**（$ABC$ / $ABCD$）放在数学坐标的水平面 $z=0$
- **顶点**在 $z>0$
- 尽量让一条底棱沿 $x$ 轴，便于读坐标

内置 `regular_pyramid` / `regular_quad_pyramid` / `cone` 已是这样。`body: "custom"` 手写坐标时必须自己摆成这样，不要把底面竖着放。

### 每步高亮点、线、面

每一步的 `highlight` **必须**点亮该步正文里出现的关键点、直线、平面（绝对集合，不能空）。
- 线 / 面 / 法向量 / 长度：写进 `model.elements` 再列入 `highlight`
- 中点、垂足、截面交点等要点：`{ "type": "point", "center": "E" }`，键名 `Point_E`
- 骨架和普通顶点本来就在，不必整副骨架都列；本步新用到的对象一定要亮

### 步骤数跟推理走，不要凑成固定步数

讲解有几步由题目本身决定，常见是 3～7 步，**禁止为了整齐而默认写成四步**。
- 该拆就拆：分类讨论、第二种构型、另一种截法，各自独立成步。
- 不该凑就不凑：算出答案的那一步就是最后一步，**不要再加一个只重复「所以答案是 …」的「写出 xxx」步**。
- 内置线面角例题恰好四步（建系 / 方向向量 / 法向量 / 代公式）是题型使然，不是模板。

### 多种情况都要画出来

答案是「或」、取值范围、所有可能值，或推理里出现 1–3 / 2–2、直角在 $A$ 或在 $B$ 这类分款时：

- **每一种构型在 `model.points` 里都有自己的点**（如 $N_1$/$N_2$、$E$/$E'$），并配齐线、面
- **每一种构型单独一步**，`highlight` 只点亮该款的点线面，镜头切到能看清这一款
- 不要只画「其中一种」然后用文字带过其它情况

### 完成：展开完整过程

最后一步按钮是「完成」。点下去后左侧按顺序、紧凑展开全部步骤（就是已有讲解，不要再写一篇综述），右侧同时点亮各步用过的点线面。最后一步就是算出答案（或列完所有情形）的那一步，不要再抄一遍前面的讲解。

### 1. 写 `problem.json`

顶层四个键：`spec` + `lesson` / `steps` / `model`。格式见 `api.md`。

- 所有数值用占位符（`{{answer}}` / `{{vals.sin}}` / `{{mp.A}}`），不要心算、不要手抄。
- `points` / `spheres` / `edges` / `target` / `initialCamera` / `answerValue` **不用写**。
- 多问题目：小问之间用 `<br>` 分行，答案用 `lesson.answers` 逐问列出。
- 题面给出线段长度：spec 的 `lengths` 声明，再加 `measure` 元素，放进「建系」那步的 `highlight`。
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
不要留下占用端口的本地服务。

## 维护

加题型/几何体：改 `engine/lib/geometry_kernel.py` 与 `engine/scripts/solve.py` 的
`BODIES` / `QUERIES`，并更新 `engine/references/api.md`。改完跑
`.venv/bin/python engine/scripts/selftest.py`（解题流程里不要跑）。
