# 10 - Subtle, generic & product UI references (15+ curated)

Focus: **less flashy, non-thematic, reusable, production-grade UI** — micro-interactions, navigation, forms, drawers, toasts, command menus, SaaS shells, and restraint-first motion.

## 15 References (verified via search)

### Micro-interaction & motion-craft galleries
1. **Design Spells** (`designspells.com`) — Dedicated to micro-interactions, subtle animations, and small tactile UI details rather than loud agency effects.
2. **Details Matter** (`detailsmatter.co`) — Hover states, smooth transitions, feedback loops, and functional UI polish.
3. **animations.dev** (Emil Kowalski) — Interactive course/reference teaching exact easing curves, numbers, and restraint (e.g. *You Don't Need Animations* for frequent actions).
4. **Rauno Freiberg / `ui.wtf` & `cmdk`** — Benchmark for invisible interaction polish: spatial consistency, instant `⌘K` menus, and web interface guidelines.

### Minimalist & functional web galleries
5. **Dead Simple Sites** (`deadsimplesites.com`) — Extreme minimalism, quiet content-first typography, generous whitespace, zero scroll-jacking.
6. **Seesaw** (`seesaw.website`) — Hand-picked modern functional websites balancing clean aesthetics with real-world usability.
7. **Layers** (`layers.to`) — Curated gallery of contemporary digital products, layouts, and clean interface components.

### Real SaaS & shipped product UI archives
8. **SaaSUI** (`saasui.design`) — Real SaaS app screenshots organized by screen type (dashboards, settings, command bars, onboarding, billing).
9. **SaaSFrame** (`saasframe.io`) / **SaaSPO** (`saaspo.com`) — SaaS marketing pages, pricing tables, and clean product UI blocks.
10. **Page Flows** (`pageflows.com`) — Recorded user flows and micro-interaction sequences from shipped software products.
11. **Vercel Geist** (`vercel.com/geist`) — Monochromatic/zinc token design system, micro-borders, crisp typography scales, and technical clarity.

### Generic, reusable open-source component registries
12. **Origin UI** — Clean, pragmatic, production-ready form controls, inputs, selects, toggles, and search bars (`shadcn` compatible).
13. **Kibo UI** — Composable application components for dashboards & SaaS (data tables, file dropzones, kanban, chat primitives).
14. **SmoothUI** — Lightweight, minimalist React + Tailwind components without visual bloat.
15. **Motion Primitives** — Subtle physics-based UI transitions (morphing dialogs, sliding tab indicators, smooth dropdowns).

### Plus foundational headless/craft tools
- **Sonner** (stacked/swipeable toasts) & **Vaul** (iOS-like spring drawer/sheet) by Emil Kowalski.
- **Headless exit-transition patterns:** Radix (`forceMount` + `data-state`), Base UI (`keepMounted` + `data-ending-style`), React Aria (`isEntering` / `isExiting`), Ariakit (`data-enter` / `data-leave`).

---

## Principles for subtle, generic components
1. **Frequency-based motion:** High-frequency actions (`⌘K`, dropdowns, tabs used 50x/day) should be **instant or <= 150ms**; never add slow dramatic springs to everyday controls.
2. **Spatial consistency:** Elements enter from and exit toward their logical origin (popovers scale `0.96 -> 1` from trigger; drawers slide from their edge).
3. **Neutral, adaptable tokens:** Use `zinc`/`slate` surfaces, `1px` subtle borders (`rgba(0,0,0,0.08)` / `rgba(255,255,255,0.1)`), and 1 restrained accent so components drop into any brand without looking "templated".
4. **CSS-first where possible:** Prefer `grid-template-rows: 0fr -> 1fr`, `transform`, `opacity`, and CSS transitions over heavy JS timelines for simple UI state.
5. **Keyboard & focus first:** Every generic component (tabs, command palette, accordion, drawer, tooltip) must work cleanly with `Tab`, `Enter`, `Esc`, and arrow keys.
