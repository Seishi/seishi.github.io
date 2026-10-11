# lesson.json 数据格式

注入模板 `__LESSON_DATA__` 的对象，分三部分：`lesson` / `steps` / `model`。
题目结构（spec）、占位符、以及哪些字段会被自动补全，见 `api.md`。

```jsonc
{
  "lesson": {
    "meta": "交互解题 · 椭圆弦长",               // 顶部小标签
    "title": "……题面……",                        // 可含 $…$ 与 <br>；小问之间用 <br> 分行
    "answerLabel": "……答案的文字说明……"
    // language / answerValue / ui 由 build.py 自动补全，不用写
  },
  "steps": [
    {
      "title": "步骤标题",
      "content": "<p>HTML 段落，行内公式 $…$，独立公式 $$…$$，数值用 {{vals.x}} 占位</p>",
      "highlight": ["Curve_C", "Seg_AB"],        // 该步要“可见”的可切换元素（绝对集合）
      "boundingbox": [-6, 4, 6, -4]              // 可选；JSXGraph 顺序 [xmin,ymax,xmax,ymin]，覆盖该步视野
    }
  ],
  "model": {
    "elements": {                                // 可切换命名元素，默认隐藏
      "Curve_C":   { "type": "ellipse", "curve": "C", "color": "curve" },
      "Seg_AB":    { "type": "segment", "a": "A", "b": "B", "color": "emphasis" },
      "Point_M":   { "type": "point", "center": "M" },
      "Focus_F":   { "type": "focus", "of": "C", "which": "right" },
      "Dir_C":     { "type": "directrix", "of": "C", "which": "left" },
      "Len_AB":    { "type": "measure", "a": "A", "b": "B", "label": "{{vals.len_AB}}" },
      "Axis":      { "type": "axes" }
    }
    // points / plot_curves / frame 由 build.py 自动补全，不用写
  }
}
```

默认视野用 `spec.frame`。某步需要放大再给 `boundingbox`。

## 答案卡：单问 vs 多问

答案卡只有一个大号数值位。**`answerValue` 只放一个简短的值**（如 `$\dfrac{\sqrt{10}}{2}$`），
build.py 会自动填好，通常你不用写。

题面含 `(1)(2)(3)` 等多个小问时，**必须改用 `lesson.answers` 逐问列出**，否则校验不通过：

```jsonc
"lesson": {
  "title": "已知椭圆 $C$……<br>(1) 求离心率；<br>(2) 求弦 $AB$ 长。",
  "answerLabel": "两问结论",
  "answers": [
    { "label": "(1) 离心率", "value": "${{vals.e}}$" },
    { "label": "(2) 弦长",   "value": "${{answer}}$" }
  ]
}
```

> ⚠️ **占位符不自带 `$`**：`{{answer}}` / `{{vals.x}}` / `{{mp.A}}` / `{{eq.C}}` 展开出来是裸 LaTeX。
> 必须自己包上定界符——写 `"${{answer}}$"`，不是 `"{{answer}}"`。漏了就会原样显示成
> `\dfrac{\sqrt{10}}{2}`。校验会检查每个字段里落在 `$…$` 之外的 LaTeX 命令并拦下。
> （唯一例外是 `measure` 元素的 `label`，模板会自动补 `$`，那里**不要**写 `$`。）

给了 `answers` 就不要再写 `answerValue`。把多个答案用 `；` 串进 `answerValue`
会把答案卡撑变形，校验会直接拦下。

题面长度不受限：过长自动缩小字号，最多占三成屏高后可滚动，不会把下方解析区压扁。

## 元素类型（model.elements[*].type）

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

`measure.label`：长度 LaTeX（**不带 `$`**），用 `{{vals.len_XX}}` 取值（需在 spec 的 `lengths` 里声明）。
题面给出了线段长度就加一个 `measure`，并把 key 放进「建系」那步的 `highlight`。
存在任一 `measure` 时，画板左上自动出现「长度标注：开/关」，无需额外数据。

## 常驻 vs 可切换

绘制分两层：

- **常驻**：坐标网格、`spec.curves` 里的已知曲线（浅色、细线）、`spec.points` 里的命名点（小圆点）。不必写入 `highlight`。
- **可切换**：只来自 `model.elements`。被当前步 `highlight` 点名则显示（强调色/加粗/焦点准线/弦/标注）；未点名则隐藏。

因此：椭圆本身会一直在；要「点亮这条椭圆」时，再在 `elements` 里放一个同曲线的强调副本（例如 `Curve_C`），把它列入该步 `highlight`。

坐标网格：一格 = 数学坐标 1 个单位，便于读点。画板 `keepaspectratio`，横纵单位相等，圆不会被拉成椭圆。

非题面原有的直线/线段/准线/方向箭头默认虚线；`spec.curves` 里的已知曲线及对应 `elements`（带 `curve`）保持实线。`color: "aux"` 一律虚线；显式 `dashed: true/false` 优先。

## 颜色语义名（COLORS）

`frame`(骨架灰) · `aux`(辅助浅灰) · `emphasis`(强调蓝) · `normal`(法/方向蓝) · `curve`(圆锥曲线主色) · `point`(顶点深蓝)

渲染取色：

- 所求直线/弦：`emphasis`
- 辅助线：`aux` + `dashed`
- 已知圆锥曲线：常驻或按步显示，主色 `curve`
- 坐标轴：`axes`，一般只在建系那步显示

## highlight 规则

每步的 `highlight` 是该步**应可见的可切换元素的完整列表**（绝对集合，不是增量）。
常驻网格、已知曲线浅线、命名点小圆不必列入。

**每一步必须高亮该步讲解里用到的点、线、曲线**，不要空 `highlight`：
- 直线、弦、焦点、准线、长度标注、强调曲线：对应 `elements` 键
- 本步关键点（中点、垂足、交点）：`type: "point"`，键名如 `Point_E`
- 拼错的键会被模板静默忽略——`build.py` 会当成错误拦下来

步骤数跟推理走，常见 3～7 步，**不要默认四步**，也不要为了整齐再加一个只重复答案的「写出 xxx」步。
分类讨论、两种斜率、两种焦弦：每种构型有自己的点/线/曲线，单独成步，`highlight` 只点亮该款。不要只画「其中一种」然后用文字带过其它情况。

最后一步按钮「完成」会展开全部步骤（按顺序、紧凑，就是已有讲解，不要再写一篇综述），并点亮各步用过的可切换元素之并集。算出答案（或列完所有情形）的那一步就是最后一步。

建系步必须出现：坐标轴元素、关键点 `{{mp.*}}`、已知曲线 `{{eq.*}}`、题面给出的长度 `measure`。

## 动点拖拽 + 实时数值（model.draggable，可选）

让一个动点沿曲线或线段拖动，联动依赖点与图元，并实时显示真实几何量（在**数学坐标**下计算，小数最多 4 位）。
`model.mathPoints` 与标准位参数由 build.py 自动补全。

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

- 拖动只改 JSXGraph 图形与读数；靠近标准位（参数相对误差 < 2%）显示「标准位 ✓」
- 左侧步骤始终对应标准位精确值，文案不随拖动改写
- readout `type` 第一版：`length`、`distance_point_line`、`eccentricity`、`area_triangle`、`chord_length`
- 无 `draggable` 的题：画板纯展示 + 切步高亮，不出现滑条区
