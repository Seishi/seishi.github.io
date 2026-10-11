# stereometry

用户发来立体几何题（文字、照片、或「随机出题」）时，必须遵循
`.cursor/skills/solid-geometry-lesson/SKILL.md`：识别题面 → 写 `problem.json` →
`engine/scripts/build.py` 生成该题目录下的交互网页。

一题一个目录。**一张照片里有多道题时，每道题单独建目录**（slug 一律英文，例题 N → `exN`、习题 N → `exerN`），同一张原图复制到各目录。命名与落盘规则见该 skill。不要把成品写进 `engine/`。

每一步必须高亮该步讲解里的关键点、直线、平面（`highlight` 不能空；要点用 `type: "point"`）。
棱锥底面放在水平面 $z=0$。最后一步点「完成」展开全部步骤，不要另写综述。
步骤数跟推理走，不要凑成固定步数（尤其不要默认四步）；分类讨论的每一种构型都要在 3D 里画出来，并单独成步。
