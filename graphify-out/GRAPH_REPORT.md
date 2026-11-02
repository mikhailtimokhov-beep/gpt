# Graph Report - gpt  (2026-11-02)

## Corpus Check
- 15 files · ~24,408 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 3)

## Summary
- 71 nodes · 110 edges · 11 communities (7 shown, 4 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a40637ce`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- numpy
- install-claude-tools.ps1
- grade.py
- gen_vo.py
- Дизайн сайтов: как работать
- render.js
- music.py
- music3.py
- playwright

## God Nodes (most connected - your core abstractions)
1. `Install-ClaudeTools()` - 10 edges
2. `synth()` - 8 edges
3. `process()` - 6 edges
4. `Дизайн сайтов: как работать` - 6 edges
5. `Install-Plugin()` - 4 edges
6. `load()` - 4 edges
7. `grade()` - 4 edges
8. `trim()` - 4 edges
9. `load_clip()` - 4 edges
10. `playwright` - 3 edges

## Surprising Connections (you probably didn't know these)
- `load()` --calls--> `numpy`  [EXTRACTED]
  yulia-cartier/video/grade.py →   _Bridges community 2 → community 0_
- `add()` --calls--> `numpy`  [EXTRACTED]
  yulia-cartier/video/music.py →   _Bridges community 6 → community 0_
- `add()` --calls--> `numpy`  [EXTRACTED]
  yulia-cartier/video/music3.py →   _Bridges community 7 → community 0_

## Import Cycles
- None detected.

## Communities (11 total, 4 thin omitted)

### Community 0 - "numpy"
Cohesion: 0.35
Nodes (6): load_clip(), male(), piper(), soften(), synth(), trim()

### Community 1 - "install-claude-tools.ps1"
Cohesion: 0.40
Nodes (10): Add-UserPath(), Install-ClaudeTools(), Install-Plugin(), Invoke-Download(), Ok(), Step(), Test-Command(), Test-Winget() (+2 more)

### Community 2 - "grade.py"
Cohesion: 0.42
Nodes (4): grade(), load(), process(), upscale()

### Community 4 - "Дизайн сайтов: как работать"
Cohesion: 0.29
Nodes (6): 1. Направление и система, 2. Сборка, 3. Движение, 4. Проверка (обязательно), graphify, Дизайн сайтов: как работать

### Community 5 - "render.js"
Cohesion: 0.29
Nodes (3): { chromium }, path, { spawn }

### Community 6 - "music.py"
Cohesion: 0.38
Nodes (4): add(), f(), add(), f()

### Community 8 - "playwright"
Cohesion: 0.50
Nodes (3): npx, playwright, @playwright/mcp

## Knowledge Gaps
- **2 isolated node(s):** `npx`, `@playwright/mcp`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 26 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `process()` connect `grade.py` to `numpy`?**
  _High betweenness centrality (0.007) - this node is a cross-community bridge._
- **What connects `npx`, `@playwright/mcp` to the rest of the system?**
  _2 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Why does `add()` connect `music.py` to `numpy`?**
  _High betweenness centrality (0.007) - this node is a cross-community bridge._