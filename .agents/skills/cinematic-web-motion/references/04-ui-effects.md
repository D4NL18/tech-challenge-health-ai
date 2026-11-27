# 04 - UI effects cookbook (copy-paste)

## Smooth scroll + GSAP sync (always first)
```js
gsap.registerPlugin(ScrollTrigger);
const lenis = new Lenis({duration:1.15, easing:t=>Math.min(1,1.001-Math.pow(2,-10*t))});
lenis.on('scroll', ScrollTrigger.update);
gsap.ticker.add(t=>lenis.raf(t*1000)); gsap.ticker.lagSmoothing(0);
```

## Scroll reveal (CSS, from Arsenal prompt)
```css
.rev{opacity:0;transform:translateY(24px);transition:opacity .9s cubic-bezier(.2,.7,.2,1),transform .9s cubic-bezier(.2,.7,.2,1)}
.rev.on{opacity:1;transform:none}
```
```js
const io=new IntersectionObserver(es=>es.forEach(e=>e.isIntersecting&&(e.target.classList.add('on'),io.unobserve(e.target))),{threshold:.15});
document.querySelectorAll('.rev').forEach(el=>io.observe(el));
```

## Tilted marquee ribbon (Oakberry)
```css
.ribbon{transform:rotate(-3deg);background:var(--accent);overflow:hidden;white-space:nowrap;padding:1rem 0}
.ribbon .track{display:inline-flex;gap:3rem;animation:mq 25s linear infinite;font:italic 800 2.5rem var(--display)}
@keyframes mq{to{transform:translateX(-50%)}}  /* duplicate content twice */
```

## Sawtooth / wave dividers
```css
.saw{height:28px;background:linear-gradient(135deg,var(--bg) 25%,transparent 25%) -14px 0,linear-gradient(225deg,var(--bg) 25%,transparent 25%) -14px 0;background-size:28px 28px;background-color:var(--next)}
```
Wave: inline SVG `<path d="M0,40 C300,120 600,0 1440,60 L1440,0 L0,0Z"/>` filled with previous section color, placed at section top/bottom with `display:block;width:100%`.

## 3D tilt card with spotlight (Spell UI tilt-card / dotmira)
```js
card.addEventListener('pointermove',e=>{const r=card.getBoundingClientRect();
 const x=(e.clientX-r.left)/r.width-.5, y=(e.clientY-r.top)/r.height-.5;
 card.style.transform=`perspective(900px) rotateY(${x*14}deg) rotateX(${-y*14}deg) scale(1.03)`;
 card.style.setProperty('--mx',(x+.5)*100+'%');card.style.setProperty('--my',(y+.5)*100+'%');});
card.addEventListener('pointerleave',()=>card.style.transform='');
```
```css
.card{transition:transform .25s;transform-style:preserve-3d;background:radial-gradient(circle at var(--mx,50%) var(--my,50%),rgba(255,255,255,.18),transparent 45%),#111}
```

## Split text reveal (headline)
```js
// split into words/chars (SplitText from GSAP is free now) 
const s=new SplitText('.h1',{type:'lines,words'});
gsap.from(s.words,{yPercent:110,opacity:0,stagger:.06,duration:1,ease:'expo.out',scrollTrigger:'.h1'});
```
Wrap lines in `overflow:hidden` masks for the "rising from below" editorial look.

## Italic serif accent word (DEUCE, "waiting", "surface")
`<h2>YOUR COURT IS <em>waiting</em></h2>` with `h2{font-family:var(--sans);text-transform:uppercase}` `em{font-family:var(--serif);font-style:italic;text-transform:none}`.

## Frosted glass card (house tour)
```css
.glass{background:rgba(20,20,20,.38);backdrop-filter:blur(18px) saturate(1.2);border:1px solid rgba(255,255,255,.14);border-radius:20px;color:#fff}
```

## Pill nav
`position:fixed;top:16px;left:50%;translate:-50%;padding:.5rem;border-radius:999px;` + glass; active item = cream pill.

## Highlighted word pill ("Respect the OAK")
`<span class="hl">OAK</span>` `.hl{background:#FFD23F;color:#2a0a4a;padding:.02em .25em;border-radius:.3em;display:inline-block;transform:rotate(-2deg)}`

## Curved rotating text badge
```html
<svg viewBox="0 0 200 200" class="badge"><defs><path id="c" d="M100,100 m-80,0 a80,80 0 1,1 160,0 a80,80 0 1,1 -160,0"/></defs>
<text><textPath href="#c">PREMIUM SERVING • FRESHLY MADE • </textPath></text></svg>
```
`.badge{animation:spin 18s linear infinite}` `@keyframes spin{to{rotate:360deg}}`

## Floating tilted tags (ORIGIN / ROAST / FLAVOR)
Absolute-position chips with `rotate(-6deg)`; GSAP `yoyo` float `y:-10`, `repeat:-1`, `ease:'sine.inOut'`, staggered; parallax on scroll `y: i*-60`.

## Magnetic button
```js
btn.addEventListener('pointermove',e=>{const r=btn.getBoundingClientRect();gsap.to(btn,{x:(e.clientX-r.left-r.width/2)*.3,y:(e.clientY-r.top-r.height/2)*.3,duration:.4})});
btn.addEventListener('pointerleave',()=>gsap.to(btn,{x:0,y:0,duration:.6,ease:'elastic.out(1,.4)'}));
```

## Bowl/product configurator (Oakberry)
State object `{size,base,toppings:Set}`; render function: cup `<div class="cup">` with absolutely stacked `<img class="layer">` per topping (z-index by order, drop-in animation `from y:-60, opacity:0, ease:'bounce.out'`), counter "n de 7", price = size + extras, modal summary "Pedido simulado". Cap toppings (max 7) with disabled state. See `examples/28-product-configurator-builder.html`.

## Horizontal scroll section
```js
const track=document.querySelector('.track');
gsap.to(track,{x:()=>-(track.scrollWidth-innerWidth),ease:'none',scrollTrigger:{trigger:'.hs',pin:true,scrub:1,end:()=>'+='+track.scrollWidth}});
```

## Page loader / intro
Counter 0-100 tied to image preload, then curtain reveal `clip-path: inset(0 0 100% 0)` and hero text stagger.

## Custom cursor, grain, noise
Grain: fixed pseudo-element with SVG feTurbulence data-URI, `opacity:.06; mix-blend-mode:multiply`. Cursor: 12px dot lerped by GSAP `quickTo`.

## Bento grid (booking cards)
`display:grid;grid-template-columns:repeat(4,1fr);gap:16px` cards spanning `grid-column:span 2` for wide ones; card: image bg, tags, price tabular-nums, hover lift + arrow translate.
