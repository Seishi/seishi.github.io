# 几何

解析几何与立体几何合在一个站点里。首页进入对应题库；每道题仍是独立的交互页：左侧分步解析，右侧图形。

| 路径 | 内容 |
| --- | --- |
| `index.html` | 总首页 |
| `analytical-geometry/` | 解析几何题库与求解引擎（JSXGraph） |
| `stereometry/` | 立体几何题库与求解引擎（Three.js） |

页面用 CDN 加载 MathJax、JSXGraph 和 Three.js，打开时需要联网。

本地继续出题时，在对应子目录里使用原来的引擎：

```bash
cd analytical-geometry
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
.venv/bin/python engine/scripts/build.py problems/.../problem.json problems/.../index.html
.venv/bin/python engine/scripts/rebuild_index.py

cd ../stereometry
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
.venv/bin/python engine/scripts/build.py problems/.../problem.json problems/.../index.html
.venv/bin/python engine/scripts/build_index.py
```
