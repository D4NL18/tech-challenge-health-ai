# 05 - Design system guidance

## DESIGN.md template (fill BEFORE coding; Refero Styles format)
```
# <Brand> Design System
Mood: <3 adjectives>. Reference: <site>.
Colors: bg #…, surface #…, text #…, muted #…, accent #…, alt-section #…
Type: Display <font> (weights, tracking, case), Accent <italic serif>, UI <sans>. Scale: h1 clamp(4rem,12vw,14rem) lh .9
Spacing: 8px base; section padding clamp(5rem,12vw,10rem)
Radius: pills 999px, cards 20-28px
Shadows/Glass: …
Motion: ease cubic-bezier(.2,.7,.2,1); durations 0.6-1.2s; scrub 0.5-1; stagger .06
Components: nav, pill CTA (solid/outline), card, tag, marquee
```
Tip: browse styles.refero.design, copy a DESIGN.md of a brand you like, adapt it.

## Palettes from the reels
| Concept | bg | alt | text | accent |
|---|---|---|---|---|
| MELT cookie | cream #F4EBDD | espresso #2B1710 / caramel #C98A3B | #2B1710 / #fff | marshmallow white |
| POUR/PLAY coffee | #F5EFE6 | - | #1A1512 | caramel #C68A4A, terracotta #B5603A |
| DEUCE tennis | #070B09 | emerald #133A27 | #F5F7F2 | volt #D4FF28, clay #D9542B |
| Oakberry acai | cream #FFF6E6 | deep purple #2A0A4A | #2A0A4A | mango #FFD23F, leaf green |
| HALF light cabin | fog slate #6E7A7C | charcoal #151515 | #fff | amber #FF9A3C |
| Cota Zero architecture | #0C0B0A | - | #F2EEE8 | warm beige #CDB89A |
| Sneaker Pista | sage #A9B79A -> cream | - | #1B1B1B | pastel pink/lilac |

## Typography pairings (free, Google Fonts / Fontshare)
- Editorial serif + sans: **Playfair Display / Fraunces / Instrument Serif / DM Serif Display** + **Inter / Manrope / DM Sans / Outfit**.
- Heavy condensed display: **Anton, Bebas Neue, Oswald, Big Shoulders, Archivo (wdth 62-125)**.
- Wide display: **Unbounded, Syne, Space Grotesk**. Fontshare: **Clash Display, Cabinet Grotesk, General Sans, Satoshi**.
- Rule: display huge + tight leading (.85-.95) + negative tracking (-0.02 to -0.05em); eyebrows 11-12px uppercase tracking .14-.2em.

## Layout patterns
- 2-column asymmetric: copy left (max 34rem), product right sticky.
- Fullscreen chapters with caption bottom-left/right alternating.
- Hairline vertical rules framing the content (editorial).
- Bento grids for functional sections; logos/marquee strips; sticky pill nav.
- Footer: big wordmark, disclaimer for concepts.

## Avoid "AI default" look
No purple-blue gradient hero, no generic floating glass cards on everything, no emoji icons, no centered-everything stack, no lorem ipsum. Use real-sounding copy, specific nouns, and photography/3D with consistent lighting.

## Image generation prompts (consistency)
Prefix every prompt with the same style block: "<subject>, studio product photography, soft top light, <bg color> seamless background, shallow depth of field, 85mm, no text, 4k". Reuse seed/reference image to keep identity.
