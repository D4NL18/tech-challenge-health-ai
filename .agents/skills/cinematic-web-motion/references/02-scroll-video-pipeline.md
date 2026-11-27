# 02 - Scroll video / frame-sequence pipeline

Used by: coffee (reel 4), tennis (6), house tour (7), cookie (2, alt).

## 1. Make the footage
1. Generate **keyframe images** (Midjourney / Nano Banana / Flux / GPT-image) in the same style, same camera angle, same background. Lock palette in the prompt.
2. Animate between keyframes with image-to-video using **start frame + end frame** (Veo, Kling, Runway, Luma, Seedance). One clip per chapter, 3-6s. Prompt example: "slow continuous dolly forward, product centered, studio light, no cuts, no text".
3. Chain clips so the last frame of A = first frame of B (seamless journey). For walkthroughs: clip per room transition (lounge->kitchen->suite).
4. Optional: remove background per frame (rembg / Figma Remove background) for transparent product layers.

## 2. Extract frames
```bash
# 1280px wide, 24fps -> webp, ~60-150 frames total per section
ffmpeg -i chapter1.mp4 -vf "fps=24,scale=1280:-2" -c:v libwebp -quality 70 frames/c1_%04d.webp
# desktop 1920 / mobile 720 variants: scale=1920:-2 and scale=720:-2
# Or keep video and seek: ffmpeg -i in.mp4 -g 1 -an -movflags +faststart scrub.mp4  (all-intra, seekable)
```
Budget: <= 8-12 MB per section on desktop; fewer frames (12-16fps) + CSS blur-free upscaling is fine.

## 3. Canvas scrub (vanilla)
See `examples/25-scroll-sequence.html` (complete). Key points:
- Preload all frames, show loader with progress, start ScrollTrigger only after first ~30% loaded (lazy-load the rest).
- `gsap.to(seq,{frame:N-1,snap:'frame',ease:'none',scrollTrigger:{pin:true,scrub:0.5,end:'+=4000'}})`.
- Draw with cover-fit; multiply by `devicePixelRatio` (cap at 2).
- Lenis sync: `lenis.on('scroll',ScrollTrigger.update); gsap.ticker.add(t=>lenis.raf(t*1000)); gsap.ticker.lagSmoothing(0)`.

## 4. Video-seek alternative (simplest)
```js
video.pause();
ScrollTrigger.create({trigger:stage,start:'top top',end:'+=300%',pin:true,scrub:true,
  onUpdate:s=>{ video.currentTime = s.progress*video.duration }});
```
Needs all-intra encoded mp4 (see ffmpeg above) or it stutters. Use for prototypes.

## 5. Chapters with copy
Overlay copy blocks absolutely positioned; fade each in/out over a progress range using a timeline:
```js
const tl=gsap.timeline({scrollTrigger:{trigger:stage,pin:true,scrub:1,end:'+=5000'}});
tl.to(seq,{frame:N-1,ease:'none',duration:10,snap:'frame',onUpdate:render},0)
  .from('.copy-1',{autoAlpha:0,y:40,duration:1},0.5).to('.copy-1',{autoAlpha:0,duration:1},3)
  .from('.copy-2',{autoAlpha:0,y:40,duration:1},3.5)...
```

## 6. Click-to-walk (reel 7)
Buttons call `gsap.to(seq,{frame:target,duration:2.4,ease:'power2.inOut',snap:'frame',onUpdate:render})` with each room mapped to a frame index (frames of the whole tour concatenated). Update the frosted card text at completion (crossfade). Lock scroll (`lenis.stop()`) while walking.

## 7. Scroll through a "glass" (hero -> interior)
Hero = first ~40 frames of dolly clip; during them fade hero text out (`opacity`, `y`), add subtle blur/vignette increase, then crossfade card in. Scroll hint at bottom.

## 8. Layered product assembly (reel 2 cookie) without video
`examples/26-sticky-layers-scrollytelling.html`: sticky stage; each layer is transparent WebP; timeline moves `y:-120vh -> 0` + slight rotate + shadow growth; section backgrounds change via `backgroundColor` tweens; final plate with rotating SVG textPath badge. Add `will-change: transform`.

## 9. Poster/fallback
Mobile or reduced-motion: show a static poster of each chapter stacked normally (no pin).
