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
