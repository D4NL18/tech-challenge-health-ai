# 01 - Workflow & prompting

## Pipeline used by the reel creators
1. Reference (Land-book, Dribbble, MotionSites, Awwwards) -> 2. Design system (Refero DESIGN.md / Figma) -> 3. Assets (AI image -> video / 3D) -> 4. Build with an AI agent (Claude Code/Cursor/Codex/Lovable/Readdy) using a rich prompt -> 5. Polish & ship.

## Master prompt template (paste into the agent)
```
Build a single-page website for <BRAND> (<one-line concept>).
Stack: <Vite+React+Tailwind+GSAP+Lenis | single index.html with CDN libs>.
Design system: <paste DESIGN.md>.
Signature interaction: <e.g. product layers drop into a stack as the user scrolls; pinned stage; background color changes per chapter>.
Sections (copy included):
1. Hero - eyebrow "...", headline "...", sub "...", CTAs "...", visual: ...
2. ...
Motion spec: smooth scroll (Lenis) synced to ScrollTrigger; reveals cubic-bezier(.2,.7,.2,1); scrub 0.8; split-text headlines; marquee; magnetic buttons.
Assets: /assets/frames/c1_0001.webp ... (N frames) / /assets/model.glb / placeholders if missing (generate gradients/SVG).
Responsive: mobile <768 stacks, simplified animations, 100svh.
Accessibility: reduced-motion fallback, focus states, contrast AA.
Deliver: runnable project, README with how to run, screenshots desktop+mobile.
```

## Tips
- Give exact copy; the model otherwise invents generic text.
- Specify file structure and "Como usar" (how to use) lines - Arsenal Pages prompts do this.
- Ask for iteration steps: scaffold -> hero -> each chapter -> polish; verify each in browser.
- Use `Plan` mode first for complex 3D/scroll builds.
- Keep a `DESIGN.md` and `ASSETS.md` in the repo so any model can continue.
- Paste reference screenshots; say what to take (layout/motion) and what not to copy (logos, assets).

## Asset prompt recipes
- Keyframe: "<product> centered, <bg>, studio lighting, hero shot, 16:9, no text".
- Video: "Start frame A, end frame B. Slow cinematic <motion>, locked camera, no cuts, product stays centered, 5s".
- Layers: "<ingredient> isolated on pure white, top-down, soft shadow" -> remove bg -> WebP.
- 3D: image of product (3 views) -> Meshy/Tripo -> optimize GLB.

## Handoff discipline (for credit/model limits)
Keep `PROGRESS.md` with checked steps and next actions; commit often.
