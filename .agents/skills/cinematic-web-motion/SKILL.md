---
name: cinematic-web-motion
description: Build award-style, scroll-driven landing pages with cinematic animation, scrollytelling, scrubbed video/frame sequences, 3D (Three.js/R3F/Spline), editorial typography, tilt cards, marquees and configurators. Use when the user wants a "premium", "animated", "3D", "scrollytelling" or "Awwwards-like" website, a product reveal site, concept/brand site, or says "make a site like this reel".
---

# Cinematic Web Motion

Recreates the look of viral "one prompt, $8k site" reels: a single product/place told as ONE continuous scroll journey, bold type, a strong 2-3 color palette, and one signature interaction.

## Workflow (follow in order)
1. **Pick the concept & archetype** -> `references/06-case-studies.md`. Choose ONE signature moment (e.g. layers stacking, camera through glass, pour transition, configurator). Everything else supports it.
2. **Write a design brief / DESIGN.md** (palette, fonts, radii, motion language) -> `references/05-design-system.md`. Never leave defaults (no generic purple gradient, no Inter-only look).
3. **Choose the hero technique** with the decision table below.
4. **Produce assets** (AI images/video, transparent PNG layers, GLB model) -> `references/02-scroll-video-pipeline.md`, `03-3d-webgl.md`.
5. **Build**: scaffold, smooth scroll (Lenis) synced to GSAP ScrollTrigger, sections, UI effects (`04-ui-effects.md`).
6. **Polish**: performance, reduced-motion, mobile fallback, loader -> `08-performance-a11y.md`.
7. **Verify** in a browser at 1440x900 and 390x844: scroll through top to bottom, check no jank, no layout shift, console clean.

## Hero technique decision table
| Need | Use | Reference |
|---|---|---|
| Product assembles/pours/transforms as user scrolls | Scroll-scrubbed frame sequence on `<canvas>` (frames from AI video) | 02 |
| Few layered objects dropping in (cookie layers) | Sticky stage + transparent PNG/WebP layers animated by GSAP timeline `scrub` | 02, example `26-sticky-layers-scrollytelling.html` |
| Real 3D object reacting to scroll/mouse | React Three Fiber / Three.js + GLB, or Spline embed | 03 |
| Walk-through/space tour | Frame sequence per room (clip A->B), click triggers play-through; or gaussian splat | 02, 06 |
| Cards/hover polish | CSS 3D tilt, spotlight, marquee, stagger text | 04 |
| Quick, no-build | Single HTML + CDN GSAP/Lenis (see examples) | examples/ |

## Default stack
- Static/single page: HTML + CSS + vanilla JS, GSAP 3 + ScrollTrigger + Lenis via CDN.
- App: Vite/Next.js + React + Tailwind + GSAP (`@gsap/react` `useGSAP`) or Framer/Motion + `@react-three/fiber` + `@react-three/drei`.
- Components: shadcn registry (Spell UI, Magic UI, Aceternity, 21st.dev) -> `07-resources.md`.

## Non-negotiable rules
- One signature interaction, 2-3 colors + 1 accent, 2 font families max (display + UI), big type (clamp 4rem-14rem).
- Section copy is short: eyebrow + 2-4 word headline + 1 sentence + pill CTA.
- Alternate section background colors in the same palette family to mark chapters.
- Easing: `cubic-bezier(.2,.7,.2,1)` for reveals; `power3.out`/`expo.out` in GSAP; scrub smoothing 0.5-1.
- Always add `prefers-reduced-motion` fallback, `loading` state, mobile fallback (lighter frames or static).
- Never use copyrighted brand assets for real clients; concept sites must carry a disclaimer (as in the Oakberry reel).
- Check licenses of copied components (dotmira lists author+license).

## Prompting an AI agent with this skill (template)
"Use the cinematic-web-motion skill. Concept: <brand/product>. Archetype: <from case studies>. Signature moment: <...>. Palette/fonts: <...>. Stack: <...>. Build, run dev server, screenshot at desktop+mobile, fix issues."

## Files
- `references/01-workflow-and-prompting.md` prompt recipes & AI tooling pipeline
- `references/02-scroll-video-pipeline.md` frames, canvas scrub, layers
- `references/03-3d-webgl.md` R3F, Three, Spline, shaders
- `references/04-ui-effects.md` code for marquee, tilt, text reveals, dividers, glass, configurator
- `references/05-design-system.md` palettes, type, DESIGN.md template
- `references/06-case-studies.md` the 8 reels broken down as recipes
- `references/07-resources.md` curated links
- `references/08-performance-a11y.md`
- `references/09-reference-sites.md` verified reference sites, galleries, component registries, Codrops repos
- `references/10-subtle-ui-references.md` 15+ subtle, generic, product/SaaS UI references (Design Spells, Details Matter, Dead Simple Sites, animations.dev, Origin UI, Kibo UI, SmoothUI, Motion Primitives, etc.)
- `examples/` 150 standalone HTML demos, catalogued by category (see Example Router below; `examples/INDEX.md`)

## Example Router (token-lean: read 1 category file, open max 2 examples)
1. Match the user's intent below. 2. Read ONLY `examples/index/<category>.md` (10-16 lines). 3. Open at most 2 examples, reading just the first ~25 lines (header comment: PATTERN/Motion/Accessibility/Adapting) before reusing code. Never list or read the whole `examples/` folder.

| Intent | Category file | # |
|---|---|---|
| product reveal, configurator, exploded view, hotspots, colorway, before/after, review parallax | `examples/index/product-showcase.md` | 10 |
| Three.js scenes, scroll-driven 3D, CSS 3D cards/tunnel, flythroughs | `examples/index/3d-webgl.md` | 12 |
| WebGL gradients, rays, aurora, particles grids, blobs, glass orbs, canvas visualizers | `examples/index/backgrounds-shaders.md` | 10 |
| first-screen heroes, preloaders, load sequences, hero-to-section hand-off | `examples/index/hero-intros.md` | 14 |
| pinned chapters, scrub timelines, frame sequences, route/SVG draws, horizontal pinned scroll, split compare | `examples/index/scroll-storytelling.md` | 16 |
| parallax depth, sticky stacks, accordions/bento, lookbooks, masonry, carousels, marquee galleries | `examples/index/parallax-layout.md` | 11 |
| smooth-scroll, scroll-snap, section wipes, velocity skew, scroll-driven CSS, headers/footers/nav tied to scroll | `examples/index/scroll-mechanics.md` | 10 |
| split/scramble/wave text, marquees, odometers, word-by-word scroll opacity, particle text, link hovers | `examples/index/typography-text.md` | 9 |
| custom cursors, magnetic, spotlight, lens, elastic, dock, cursor-follow cards, reactive grids | `examples/index/cursor-pointer-fx.md` | 9 |
| fullscreen menus, curtain/page transitions, view transitions, tabs, dropdown nav | `examples/index/navigation-transitions.md` | 6 |
| features, testimonials, pricing, team, FAQ, process steps, timelines, logo walls | `examples/index/content-sections.md` | 8 |
| closing CTA, giant-type footer, end credits | `examples/index/cta-footer-end.md` | 3 |
| date range, combobox, wizard, dropzone, OTP/range, toggles, stepper, search, copy button, motion preference | `examples/index/ui-forms-inputs.md` | 11 |
| context menu, popover, inbox, command palette, toasts, drawer, dialogs, lightbox, skeleton, empty state, swipe rows | `examples/index/ui-overlays-feedback.md` | 11 |
| sortable table, kanban, accordion, pricing toggle, TOC scrollspy, snap cards, marquee logos, flip clock, progress ring, avatars | `examples/index/ui-data-display.md` | 10 |

**Quick picks (best first)**
- Premium product hero/landing: 26, 28, 101, 24, 46 | 3D: 02, 06, 142 | Scrollytelling: 101, 102, 106, 25
- Hero intro: 118, 111, 89, 145 | Smooth/section scroll: 133, 132, 131, 140 | Page transitions: 55, 146
- Type/text: 07, 51, 135 | Cursor: 10, 11, 99 | SaaS UI: 71, 73, 74, 82 | Content sections: 121, 123, 126, 129
