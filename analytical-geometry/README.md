# analytical-geometry

把一道高中解析几何题解成**可交互的教学网页**：左侧 MathJax 分步解析，右侧 JSXGraph 平面图（分步高亮；需要时动点可拖）。数值由 sympy 精确计算，答案、坐标、方程、步骤同源。

对照立体几何仓库 stereometry：Three.js 3D 换成 JSXGraph 2D，`body`+`dims` 换成 `curves`+`points`+`frame`，题目列表在仓库根 `index.html`（不是 `problems/index.html`）。**不做随机出题。**

学段范围：直线与圆、圆锥曲线（椭圆、双曲线、抛物线）、参数方程与极坐标。

## 怎么用

在 Cursor 对话里发题目文字，或把题目照片丢进窗口。**一张图里有多道题时，每道题各一个目录、各一个网页。**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

DIR=$(.venv/bin/python engine/scripts/new_problem.py ex2-ellipse-chord)
# 把 problem.json 写进 $DIR 后：
.venv/bin/python engine/scripts/build.py "$DIR/problem.json" "$DIR/index.html"
```

页面用 CDN 加载 MathJax 与 JSXGraph，**需要联网**。无网时公式与画板不可用（第一版不打本地 vendor）。

## 目录约定

```
problems/YYYYMMDD-NN-slug/
  meta.json       # 分配目录时生成
  source.jpg      # 仅拍照题：原图
  problem.json    # 题目结构 + 分步讲解
  index.html      # 成品网页
```

| 段 | 规则 |
|---|---|
| `YYYYMMDD` | 当天日期 |
| `NN` | 当天序号，`01` 起，由 `new_problem.py` 分配 |
| `slug` | 只用英文。书上的题：`ex2-ellipse-chord`（例题 N → `exN`，习题 N → `exerN`）。自拟题：`ellipse-focal-chord` |

不要把成品写进 `engine/`。一张图多道题 → 多个 `problems/…` 目录，不要合页。

## 命令

```bash
.venv/bin/python engine/scripts/new_problem.py <slug> [--source 原图]
.venv/bin/python engine/scripts/build.py problems/.../problem.json problems/.../index.html
.venv/bin/python engine/scripts/solve.py  problems/.../problem.json    # 只看答案
.venv/bin/python engine/scripts/selftest.py                             # 引擎回归
.venv/bin/python engine/scripts/rebuild_index.py                        # 刷新根列表
```

`problem.json` 的 spec / 占位符见 `engine/references/api.md`。Agent 工作流程见 `.cursor/skills/analytic-geometry-lesson/SKILL.md`。
