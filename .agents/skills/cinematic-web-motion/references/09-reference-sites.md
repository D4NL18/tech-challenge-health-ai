# 09 - Reference sites (verified via search, round 2)

## Cited in the reels - what they are
| Site | What | Use it for |
|---|---|---|
| motionsites.ai | Library of copy-paste prompts for animated sites (React+Vite+Tailwind+Framer/GSAP); filters Hero/Sections/3D/AI/SaaS/Agency | pick a prompt close to your concept, adapt palette/copy |
| spell.sh | shadcn-registry React motion components (Tailwind+Radix): tilt card, marquee, animated gradient, light rays, text effects. `pnpm dlx shadcn@latest add @spell/<name>` (repo xxtomm/spell-ui) | drop-in effects |
| styles.refero.design | 2000+ `DESIGN.md` design systems from real products (colors, type, spacing, components) + Refero MCP/skills | give agent a concrete design system |
| Inspora | Free curated visual stream; filters Web Design, Branding, Product, Motion, Illustration, 3D, Print | mood/layout inspiration |
| dotmira.com | Index of web effects/components (React, Tailwind, HTML/CSS, Vue) with code, author, license; MCP for Cursor | find a specific hover effect; CHECK license |
| Dribbble / Land-book | UI shots / real landing pages by niche | layout references |
| Arsenal Pages | PT-BR library of 600+ page/component prompts (HTML/CSS/JS), copy for Claude Code/Cursor/Codex/Lovable | prompt structure model |
| Readdy (readdy.ai) | AI site builder from prompt/screenshot/URL, visual editor, backend/forms | quick prototype |

## Similar & better galleries
- **Godly** godly.website - best for WebGL/Three/Spline/scroll motion.
- **Awwwards** - tags 3D, Scroll, Animation; Sites of the Day/Developer award.
- **Siteinspire**, **Minimal Gallery** - clean typographic.
- **Lapa Ninja** - has a "3D websites" category, landing pages.
- **Saved.design**, **Umanmade**, **Are.na** - moodboards. **Mobbin**, **Pageflows**, **Refero** - real product flows.
- Search keywords in galleries: `Spline`, `Three.js`, `WebGL`, `ScrollTrigger`, `Immersive`, `Parallax`, `Product Showcase`.

## Component registries (compare)
| Lib | Strength | Notes |
|---|---|---|
| React Bits (reactbits.dev) | 600+ effect snippets: text, backgrounds, cursors; JS/TS/CSS/Tailwind variants | mixed easing - normalize |
| Magic UI | SaaS marketing blocks, shadcn+Motion | free core |
| Aceternity UI | bold 3D/canvas showpieces | heavy - test mobile |
| 21st.dev | community registry + MCP for agents | variety |
| Spell UI | motion/3D tilt/shaders | see above |

## Open-source scroll/WebGL learning repos (Codrops ecosystem)
- `codrops/RotatingOnScrollAnimations` - images rotating in 3D on scroll (Three+GSAP+Lenis)
- `JosephASG/codrops-cinematic-scroll-animations` - 3D cinematic scroll with particles/shaders
- `J0SUKE/gsap-threejs-codrops` - WebGL gallery with GSAP plugins (ScrollTrigger, Flip, SplitText)
- `codrops/interlude` - Astro + Three + GSAP page-transition starter
- Pattern: fixed full-screen WebGL canvas behind HTML; ScrollTrigger progress -> uniforms/camera/rotation; custom GLSL for distortion.

## How to use references (process)
1. Collect 3 refs (one layout, one motion, one type). 2. Write what you take from each (never copy assets/branding). 3. Create DESIGN.md (see 05). 4. Choose components from `examples/`. 5. Build & verify.
