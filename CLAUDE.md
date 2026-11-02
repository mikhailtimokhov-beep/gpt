# Дизайн сайтов: как работать

Цель: креативные, нешаблонные сайты. Работай сам, без лишних вопросов, по этому порядку.

## 1. Направление и система
- `taste-skill` — арт-дирекция, уход от «AI-шаблонного» вида. Начинай с него для любой публичной страницы.
- `frontend-design` — смелое, осознанное визуальное решение (типографика, композиция).
- `ui-ux-pro-max` — подбор стиля, палитры, шрифтов: `python3 .claude/skills/ui-ux-pro-max/scripts/search.py "<описание>" --design-system`.
- `design-system`, `brand`, `theme-factory` — токены, бренд, темы.

## 2. Сборка
- `ui-styling`, `pick-ui-library` — компоненты и код.
- `prototype` — быстрые прототипы.
- Только для React/Vue/Remotion, вызываются вручную через `/имя` (скрыты из контекста ради экономии): `vercel-composition-patterns`, `vercel-react-best-practices`, `vercel-react-view-transitions`, `gsap-react`, `gsap-frameworks`, `web-artifacts-builder`, `video-shotcraft`.
- `canvas-design`, `algorithmic-art`, `banner-design` — графика, постеры, генеративные фоны, баннеры.

## 3. Движение
- `animate`, `emil-design-eng`, `apple-design`, `animation-vocabulary` — микро-взаимодействия.
- `gsap-*` (core, timeline, scrolltrigger, plugins, utils, performance) — анимации при прокрутке и сложные сцены.
- Переходы между страницами: View Transitions API в CSS/JS; для React — `/vercel-react-view-transitions`.
- `find-animation-opportunities`, `animation-performance` — где добавить движение и как не тормозить.
- `cast` (genjutsu) — оживить UI: тезис взаимодействия, подбор техник, реализация. `motion-design` — тайминги, кривые, хореография.
- 3D: `threejs-fundamentals` — вход; остальные `threejs-*` читать по пути из него.
- `design-dna` — разобрать референс (скриншот/URL) в JSON-стиль и собрать по нему.
- Вручную, дорого или дублирует: `/paint` (полный дизайн-конвейер genjutsu), `/bunshin` (сайт целиком параллельными агентами).

## 4. Проверка (обязательно)
- Открой результат через Playwright MCP (`.mcp.json`) или `webapp-testing`, сделай скриншоты 390px и 1440px.
- `impeccable` (audit / polish), `web-design-guidelines`, `userinterface-wiki`, `break-ui`, `review-animations`, `improve-animations` — найди и исправь проблемы, повтори скриншоты.
- Учитывай `prefers-reduced-motion`, контраст и мобильную версию.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- When graphify-out/graph.json exists, run `graphify query "<question>"` before your first grep, search or source-file read for a codebase question, and put this rule in every subagent prompt that explores code. Read raw files only for lines the graph or an earlier read already located. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
- A committed graphify-out/graph.json is rewritten whole on every build, so a large diff to it in a pull request is expected. Do not flag it as churn or suggest skipping the graph rebuild or its hooks.
