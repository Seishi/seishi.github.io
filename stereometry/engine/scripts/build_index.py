#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""扫描 problems/*/ 生成题目列表页 problems/index.html。"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from html import unescape
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
PROBLEMS = REPO / "problems"

DIR_RE = re.compile(r"^(\d{8})-(\d{2})-(.+)$")
EX_RE = re.compile(r"^ex(\d+)(?:-|$)", re.I)
EXER_RE = re.compile(r"^exer(\d+)(?:-|$)", re.I)
PRAC_RE = re.compile(r"^prac(\d+)(?:-|$)", re.I)
TAG_RE = re.compile(r"<[^>]+>")
BR_RE = re.compile(r"<br\s*/?>", re.I)


def _strip_html(text: str) -> str:
    text = BR_RE.sub(" ", text or "")
    return unescape(TAG_RE.sub("", text)).strip()


def _label_kind(slug: str) -> tuple[str, str, int]:
    """返回 (显示名, 分组, 排序号)。"""
    m = EXER_RE.match(slug or "")
    if m:
        n = int(m.group(1))
        return f"习题 {n}", "exer", n
    m = PRAC_RE.match(slug or "")
    if m:
        n = int(m.group(1))
        return f"练习 {n}", "prac", n
    m = EX_RE.match(slug or "")
    if m:
        n = int(m.group(1))
        return f"例题 {n}", "ex", n
    return "演示", "demo", 0


def collect() -> list[dict]:
    rows = []
    if not PROBLEMS.is_dir():
        return rows
    for d in PROBLEMS.iterdir():
        if not d.is_dir() or d.name.startswith("_") or d.name.startswith("."):
            continue
        m = DIR_RE.match(d.name)
        if not m:
            continue
        if not (d / "index.html").is_file():
            continue
        day, seq, slug = m.group(1), m.group(2), m.group(3)
        meta = {}
        mp = d / "meta.json"
        if mp.is_file():
            try:
                meta = json.loads(mp.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                meta = {}
        doc = {}
        pj = d / "problem.json"
        if pj.is_file():
            try:
                doc = json.loads(pj.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                doc = {}
        lesson = doc.get("lesson") or {}
        display, kind, num = _label_kind(meta.get("slug") or slug)
        created = meta.get("created") or ""
        date_label = f"{day[0:4]}-{day[4:6]}-{day[6:8]}"
        rows.append({
            "id": d.name,
            "href": f"{d.name}/index.html",
            "slug": meta.get("slug") or slug,
            "label": display,
            "kind": kind,
            "num": num,
            "seq": int(seq),
            "day": day,
            "date": date_label,
            "created": created,
            "meta": _strip_html(lesson.get("meta") or ""),
            "title": _strip_html(lesson.get("title") or d.name),
            "source": bool(meta.get("source_file") or (d / "source.jpg").is_file()),
        })
    rows.sort(key=lambda r: (r["day"], r["kind"] != "ex", r["num"] or 10**6, r["seq"]))
    return rows


def write_index(out: Path | None = None) -> Path:
    rows = collect()
    out = out or (PROBLEMS / "index.html")
    payload = json.dumps(rows, ensure_ascii=False)
    html = TEMPLATE.replace("__PROBLEMS__", payload).replace("__COUNT__", str(len(rows)))
    html = html.replace("__STAMP__", datetime.now().astimezone().strftime("%Y-%m-%d %H:%M"))
    out.write_text(html, encoding="utf-8")
    return out


TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script>
    (function () {
      try {
        var t = localStorage.getItem('stereometry-theme');
        document.documentElement.setAttribute('data-theme', t === 'dark' ? 'dark' : 'light');
      } catch (e) {
        document.documentElement.setAttribute('data-theme', 'light');
      }
    })();
  </script>
  <title>题目列表 · 立体几何</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&family=Noto+Sans+SC:wght@400;500;700&display=swap">
  <style>
    :root {
      color-scheme: light;
      --bg: #F3F5F8;
      --panel: #FFFFFF;
      --inset: #F7F8FA;
      --line: #E2E7EE;
      --line-2: #D3DAE3;
      --text: #1A2330;
      --text-2: #3D4A5C;
      --muted: #6B7787;
      --faint: #98A2AE;
      --accent: #2563EB;
      --accent-dark: #1D4ED8;
      --accent-soft: rgba(37, 99, 235, 0.12);
      --on-accent: #FFFFFF;
      --shadow: 0 1px 2px rgba(26, 35, 48, 0.06), 0 8px 24px rgba(26, 35, 48, 0.04);
      --font-body: 'Instrument Sans', 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
      --font-mono: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
    }
    html[data-theme="dark"] {
      color-scheme: dark;
      --bg: #0A0D12;
      --panel: #0E131A;
      --inset: #0B1016;
      --line: #1F2731;
      --line-2: #243040;
      --text: #E7ECF2;
      --text-2: #B8C1CC;
      --muted: #8B96A5;
      --faint: #4E5A69;
      --accent: #60A5FA;
      --accent-dark: #3B82F6;
      --accent-soft: rgba(96, 165, 250, 0.16);
      --on-accent: #0A1628;
      --shadow: 0 1px 2px rgba(0, 0, 0, 0.35), 0 8px 24px rgba(0, 0, 0, 0.25);
    }
    * { box-sizing: border-box; }
    html, body { margin: 0; background: var(--bg); color: var(--text); font-family: var(--font-body); }
    body { min-height: 100vh; }
    a { color: inherit; }
    header {
      position: sticky; top: 0; z-index: 10;
      background: color-mix(in srgb, var(--bg) 86%, transparent);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--line);
    }
    .bar {
      max-width: 980px; margin: 0 auto; padding: 16px 20px 14px;
      display: flex; flex-wrap: wrap; gap: 12px 16px; align-items: center;
    }
    .brand { flex: 1 1 180px; min-width: 0; }
    .brand h1 {
      margin: 0; font-size: 18px; font-weight: 600; letter-spacing: 0.02em;
    }
    .brand p {
      margin: 4px 0 0; color: var(--muted); font-size: 12px;
      font-family: var(--font-mono);
    }
    .search {
      flex: 2 1 240px;
      position: relative;
    }
    .search input {
      width: 100%; height: 38px; padding: 0 12px 0 34px;
      border: 1px solid var(--line-2); border-radius: 8px;
      background: var(--panel); color: var(--text);
      font: 14px/1 var(--font-body); outline: none;
    }
    .search input:focus { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-soft); }
    .search svg {
      position: absolute; left: 10px; top: 10px; width: 16px; height: 16px;
      color: var(--faint);
    }
    .theme {
      width: 38px; height: 38px; border-radius: 8px;
      border: 1px solid var(--line-2); background: var(--panel); color: var(--text-2);
      cursor: pointer; display: grid; place-items: center;
    }
    .theme:hover { border-color: var(--accent); color: var(--accent); }
    .filters {
      max-width: 980px; margin: 0 auto; padding: 0 20px 14px;
      display: flex; gap: 8px; flex-wrap: wrap;
    }
    .chip {
      border: 1px solid var(--line-2); background: var(--panel); color: var(--text-2);
      border-radius: 999px; padding: 5px 12px; font-size: 13px; cursor: pointer;
    }
    .chip.is-on { background: var(--accent); border-color: var(--accent); color: var(--on-accent); }
    main { max-width: 980px; margin: 0 auto; padding: 18px 20px 48px; }
    .grid { display: grid; gap: 12px; }
    .card {
      display: grid; grid-template-columns: auto 1fr auto; gap: 12px 16px;
      align-items: start;
      background: var(--panel); border: 1px solid var(--line); border-radius: 12px;
      padding: 16px 18px; text-decoration: none; box-shadow: var(--shadow);
      transition: border-color .15s ease, transform .15s ease;
    }
    .card:hover { border-color: var(--accent); transform: translateY(-1px); }
    .badge {
      font-family: var(--font-mono); font-size: 12px; font-weight: 500;
      padding: 4px 8px; border-radius: 999px; background: var(--accent-soft);
      color: var(--accent-dark); white-space: nowrap;
    }
    html[data-theme="dark"] .badge { color: var(--accent); }
    .body { min-width: 0; }
    .kicker {
      display: flex; gap: 10px; flex-wrap: wrap; align-items: center;
      color: var(--muted); font-size: 12px; font-family: var(--font-mono);
      margin-bottom: 6px;
    }
    .title {
      margin: 0; font-size: 15px; font-weight: 500; line-height: 1.55; color: var(--text);
    }
    .go {
      align-self: center; color: var(--faint); font-size: 13px; white-space: nowrap;
      font-family: var(--font-mono);
    }
    .card:hover .go { color: var(--accent); }
    .empty { text-align: center; color: var(--muted); padding: 48px 12px; }
    @media (max-width: 640px) {
      .card { grid-template-columns: auto 1fr; }
      .go { display: none; }
    }
  </style>
</head>
<body>
  <header>
    <div class="bar">
      <div class="brand">
        <h1>立体几何题目</h1>
        <p><span id="count">__COUNT__</span> 题 · 更新 __STAMP__</p>
      </div>
      <label class="search">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/>
        </svg>
        <input id="q" type="search" placeholder="搜索题号或题面" autocomplete="off">
      </label>
      <button class="theme" id="theme" type="button" title="切换亮/暗色" aria-label="切换主题">◐</button>
    </div>
    <div class="filters" id="filters"></div>
  </header>
  <main>
    <div class="grid" id="list"></div>
    <p class="empty" id="empty" hidden>没有匹配的题目</p>
  </main>
  <script>
    window.MathJax = {
      tex: { inlineMath: [['$', '$']], displayMath: [['$$', '$$']], processEscapes: true },
      options: { skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre'] }
    };
  </script>
  <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
  <script>
    const PROBLEMS = __PROBLEMS__;
    const KINDS = [
      { id: 'all', label: '全部' },
      { id: 'ex', label: '例题' },
      { id: 'exer', label: '习题' },
      { id: 'demo', label: '演示' }
    ];
    let kind = 'all';
    const list = document.getElementById('list');
    const empty = document.getElementById('empty');
    const q = document.getElementById('q');
    const filters = document.getElementById('filters');
    const countEl = document.getElementById('count');

    KINDS.forEach((k) => {
      const n = k.id === 'all' ? PROBLEMS.length : PROBLEMS.filter((p) => p.kind === k.id).length;
      if (k.id !== 'all' && n === 0) return;
      const b = document.createElement('button');
      b.className = 'chip' + (k.id === 'all' ? ' is-on' : '');
      b.type = 'button';
      b.dataset.kind = k.id;
      b.textContent = k.label + ' ' + n;
      b.addEventListener('click', () => {
        kind = k.id;
        filters.querySelectorAll('.chip').forEach((c) => c.classList.toggle('is-on', c.dataset.kind === kind));
        render();
      });
      filters.appendChild(b);
    });

    function hay(p) {
      return [p.label, p.slug, p.title, p.meta, p.date].join(' ').toLowerCase();
    }
    function visible() {
      const s = (q.value || '').trim().toLowerCase();
      return PROBLEMS.filter((p) => (kind === 'all' || p.kind === kind) && (!s || hay(p).includes(s)));
    }
    function render() {
      const rows = visible();
      list.innerHTML = '';
      empty.hidden = rows.length > 0;
      countEl.textContent = String(rows.length);
      rows.forEach((p) => {
        const a = document.createElement('a');
        a.className = 'card';
        a.href = p.href;
        a.innerHTML =
          '<span class="badge">' + p.label + '</span>' +
          '<div class="body">' +
            '<div class="kicker">' +
              (p.meta ? '<span>' + p.meta + '</span>' : '') +
              '<span>' + p.date + '</span>' +
              (p.source ? '<span>原图</span>' : '') +
            '</div>' +
            '<p class="title">' + p.title + '</p>' +
          '</div>' +
          '<span class="go">打开 →</span>';
        list.appendChild(a);
      });
      if (window.MathJax && window.MathJax.typesetPromise) {
        MathJax.typesetPromise([list]).catch(() => {});
      }
    }
    q.addEventListener('input', render);
    document.getElementById('theme').addEventListener('click', () => {
      const next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      try { localStorage.setItem('stereometry-theme', next); } catch (e) {}
    });
    document.addEventListener('keydown', (e) => {
      if (e.key === '/' && document.activeElement !== q) {
        e.preventDefault();
        q.focus();
      }
    });
    render();
    const wait = setInterval(() => {
      if (window.MathJax && window.MathJax.typesetPromise) {
        clearInterval(wait);
        MathJax.typesetPromise([list]).catch(() => {});
      }
    }, 80);
  </script>
</body>
</html>
"""


def main():
    out = write_index()
    print(f"PASS  已生成: {out}  ({len(collect())} 题)")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"FAIL  {e}", file=sys.stderr)
        sys.exit(1)
