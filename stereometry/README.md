# stereometry

把一道立体几何题解成**可交互的教学网页**：左侧 MathJax 分步解析，右侧 Three.js 3D 模型（分步高亮、切换镜头）。数值由 sympy 精确计算，答案、坐标、步骤同源。

求解引擎移植自 [edulab](https://github.com/wy51ai/edulab) 的 `edu-solid-geometry`（Apache-2.0）。本仓库改成**一题一个目录**存放。

## 怎么用

在 Cursor 对话里发题目文字，或把题目照片丢进窗口。**一张图里有多道题时，每道题各一个目录、各一个网页。**

也可以本地出内置题 / 随机题：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

DIR=$(python3 engine/scripts/new_problem.py ex2-pc-min)
python3 engine/scripts/generate.py pyramid "$DIR/index.html"
```

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
| `slug` | 只用英文。书上的题：`ex2-pc-min`、`ex1-tetra-plane-set`（例题 N → `exN`，习题 N → `exerN`）。自拟题：`pyramid-be-pac` |

不要把成品写进 `engine/`。一张图多道题 → 多个 `problems/…` 目录，不要合页。

## 命令

```bash
.venv/bin/python engine/scripts/new_problem.py <slug> [--source 原图]
.venv/bin/python engine/scripts/build.py problems/.../problem.json problems/.../index.html
.venv/bin/python engine/scripts/solve.py  problems/.../problem.json    # 只看答案
.venv/bin/python engine/scripts/generate.py cube|box|pyramid|random [seed] out.html
.venv/bin/python engine/scripts/selftest.py                             # 引擎回归
```

`problem.json` 的 spec / 占位符见 `engine/references/api.md`。Agent 工作流程见 `.cursor/skills/solid-geometry-lesson/SKILL.md`。
