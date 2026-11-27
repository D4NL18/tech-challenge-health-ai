# 06 - Case studies (the 8 reels as recipes)

Each: concept -> structure -> signature technique -> how to build.

## 1. Oakberry "Respect the OAK" (@_marsdesigner)
Unsolicited concept site for a brand (add disclaimer; AI product imagery).
Structure: hero (nav Produtos/Monte o seu/Ofertas/Lojas, eyebrow, headline w/ yellow pill word, 2 pill CTAs, cup photo) -> tilted marquee ribbon -> dark purple editorial punchlines in bold italic with arc/horizon transition + floating particles -> **bowl builder** -> simulated order modal -> yellow store banner -> sawtooth into footer.
Build: DOM-only; configurator state + layered PNG toppings; see 04 & `examples/28-product-configurator-builder.html`. Workflow: Figma layout + AI images (remove background, boost resolution) then Claude builds.

## 2. MELT cookie scrollytelling (@polanaeem.tech)
Structure (all in one sticky stage, product right, copy left): MADE TO MELT (cream) -> DARK AT HEART (brown, chocolate drops) -> TOASTED TO PERFECTION (caramel, marshmallow drops) -> THE PERFECT STACK (cream, angled planes, top cookie drops) -> FEEL THE MELT (brown, 3/4 tilt) -> wave divider -> IMPOSSIBLE TO RESIST (plate + circular text badge).
Build: `examples/26-sticky-layers-scrollytelling.html`; transparent layer images (AI-generated, bg removed); timeline scrub; bg color tween per chapter; layer drop with slight rotation + shadow; headline swap with split-text; step dots indicating chapter.

## 3. Arsenal Pages prompt library / Cota Zero / sneaker (@ogustavohirt)
Workflow: library of 600+ page/component prompts -> copy for Claude Code/Cursor/Codex/Lovable -> paste -> site in ~5 min. Prompts contain complete code + "Como usar" file path.
Signature: Spline ring of slabs rotating+descending behind text on scroll (architecture studio, dark warm, Outfit font); mouse-reactive 3D sneaker over giant DUNK type (sage->cream gradient, heavy condensed sans).
Lesson: **write prompts as full specs**: stack, palette, fonts, section list with copy, motion spec per section, file structure, responsive rules. See 01.

## 4. POUR/PLAY coffee (@enkywebstudio)
Hero WAKE THE BEANS (bean splits) -> pour crema -> 2. LET IT BLOOM (V60) -> carafe -> MAKE TIME TASTE BETTER (latte + floating ORIGIN/ROAST/FLAVOR cards).
Build: AI keyframes + image-to-video chain -> frame sequence canvas (02). Cream bg #F5EFE6, serif display uppercase, hairline margin rules, nav wordmark/links/icons, bottom dots. Cards float with yoyo + parallax.

## 5. Spell UI + Inspora + Refero Styles (@talescavalcanti.ia)
Toolbox rather than a site: Spell UI components (tilt card, animated gradient, light rays, text marquee, words stagger, gradient wave text, flow/pop buttons, exploding input), Inspora (reference library), Refero Styles (design systems as DESIGN.md pasted into IDE). Use: install components via shadcn registry, feed DESIGN.md to the agent before building.

## 6. DEUCE tennis club (@0808cayden, Claude + Readdy)
Hero: giant serif DEUCE with tennis ball as the "U" -> scrubbed chapters (racket strike, night court, aerial) with italic serif captions alternating corners -> triptych "YOUR COURT IS waiting" + volt pill CTA -> "Choose your surface" venue pills + bento court cards (price, tags, availability, Book court ->).
Build: frame sequence (02) + bento grid & filter pills (04). Ball-as-letter: inline `<span>` replaced by `<img>` ball, rotate on scroll. Palette obsidian/emerald/volt.

## 7. HALF light cabin (@michonmotion)
Scroll dolly through glass facade -> lounge -> choose room (lounge/kitchen/suite) with continuous glides. Frosted card bottom-left with title/copy/pills; floating pill nav; huge wide sans "HALF" + italic serif "light".
Build: one concatenated frame sequence; scroll for hero->lounge, buttons animate frame index to room anchors (02 section 6). Alternative: gaussian splat + camera path (03).

## 8. Reference hubs (@caiolzn_)
MotionSites (animated-site prompts, dark gallery w/ filters), Dribbble, Land-book. Use as inspiration step: pick 3 references, extract layout+motion, write DESIGN.md.

## Common DNA
1. one product, one continuous journey; 2. giant type + short copy; 3. color-blocked chapters; 4. AI-generated assets with consistent style; 5. pill CTAs + pill nav; 6. editorial serif italic accent; 7. prompt-driven build (Claude Code) with a pre-made design spec.
