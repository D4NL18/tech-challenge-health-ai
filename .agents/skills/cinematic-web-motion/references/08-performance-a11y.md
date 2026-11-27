# 08 - Performance, accessibility, QA

## Performance
- Frames: WebP, 1280 wide desktop / 720 mobile, <= 12MB per sequence; lazy-load after first 30%.
- `will-change: transform` only on animated layers; animate transform/opacity only.
- Pause canvas/WebGL offscreen; `dpr` cap 2; compress GLB (draco+webp).
- Fonts: `font-display:swap`, preload display font, subset.
- Images: `loading="lazy"`, width/height set (no CLS). Use `<picture>` AVIF/WebP.
- Kill ScrollTrigger on route change; `ScrollTrigger.refresh()` after images load.
- Lighthouse target: LCP < 2.5s with poster image as LCP element.

## Accessibility
```css
@media (prefers-reduced-motion: reduce){ *{animation:none!important;transition:none!important} }
```
In JS: `matchMedia('(prefers-reduced-motion: reduce)')` -> skip Lenis/pin, show static stacked posters.
- Text contrast >= 4.5:1 (check volt-lime on dark, text over video: add gradient scrim).
- Real `<button>`/`<a>`, focus rings, keyboard for configurators, `aria-live="polite"` on room/price changes.
- Alt text for hero images; `aria-hidden` for decorative canvas.

## Mobile
- Disable pinned heavy sequences if `innerWidth<768` or provide the 720px set; use `100svh`.
- `ScrollTrigger.normalizeScroll(true)` for iOS address-bar jumps; `ignoreMobileResize`.
- Touch: replace hover tilt with gyro/none.

## QA checklist
- [ ] Scroll top->bottom at 1440x900 and 390x844 without console errors
- [ ] Resize + refresh mid-page restores state
- [ ] Loader appears, no flash of unstyled content
- [ ] Back button / anchors work with Lenis (`lenis.scrollTo`)
- [ ] Reduced-motion mode OK
- [ ] Network throttled (Fast 3G) still usable
- [ ] License/disclaimer for third-party brands & AI images

## Common bugs
- Pin jitter -> Lenis not synced to ScrollTrigger.
- Frames blurry -> canvas not scaled by DPR.
- Pinned section height wrong -> images not loaded before `refresh()`.
- Text unreadable on video -> add `linear-gradient` scrim.
- Sticky not working -> ancestor has `overflow:hidden`; use `overflow:clip`.
