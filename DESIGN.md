# DESIGN.md — yuyupeng.com

Mode: **Experience.** The work leads; the interface recedes.

The visual world is pinned by the client to **Atelier Rhizome**: a deep olive ground, bone panels floating on it, a hairline modular grid, small quiet sans-serif, and hand-drawn botanical marks. That reference wins over any category habit.

## Ground and panels

The page is olive. Content sits on **bone panels** inset from the edge, the way Rhizome's cards float on their green field. The olive is never a section background inside a panel — it is the ground the whole site stands on, so scrolling always shows the field at the margins.

## The hairline grid

Every group of cells is a CSS grid with `gap: 1px` over a rule-coloured background, so the rules are true 1px hairlines that never double up or misalign. This is the site's structure, not decoration: project cells, metadata rows, and the footer all resolve onto it.

## Colour

| Token | Value | Use |
|---|---|---|
| `--ground` | `#454E22` | page field |
| `--panel` | `#E8E6DC` | bone panels |
| `--ink` | `#31381A` | text on bone |
| `--ink-soft` | `#5E6440` | secondary text on bone — 4.96:1 |
| `--on-ground` | `#E8E6DC` | text on olive — 7.2:1 |
| `--on-ground-soft` | `#B9BC9C` | secondary on olive — 4.56:1 |
| `--rule` | `rgba(49,56,26,.18)` | hairlines on bone |
| `--moss` | `#7C8A3E` | botanical marks, hover |

Secondary text is tinted from the olive hue in both directions. No greys anywhere.

## Type

**Instrument Sans**, self-hosted variable (400–700), latin + latin-ext + italic. One family; hierarchy comes from size, weight and tracking, not from a second face — matching Rhizome, where the personality sits in the colour, grid and drawings rather than in type contrast.

- Display: `clamp(2.4rem, 6vw, 5rem)`, weight 500, tracking `-0.035em`
- Body: 1.0625rem/1.65, measure capped at 68ch
- Labels: 0.6875rem, weight 600, tracking `0.14em`, uppercase

## Botanical marks

Authored inline SVG grass strokes in `--moss`, drawn with irregular tapered paths. They mark section joins and the footer — the one place the site is allowed to be hand-made. Never emoji, never an icon font.

## Motion

One authored moment: images and panel sections rise 14px and fade in as they enter, on an exponential ease-out, staggered by position. Everything is visible by default and animates only if `prefers-reduced-motion` allows it — the page is complete with JavaScript off.

## Browser surfaces

Selection, caret, focus ring, scrollbar and the `::marker` are all themed from the palette. Focus is a 2px moss ring with a bone offset, visible on both grounds.

## Rules

- Images keep their own aspect ratio on project pages — the drawings are 6:1 strips and 3:4 boards, and cropping them to a uniform tile destroys the information. Only the home grid crops, to 4:3.
- Nothing in the design may demand more than ~1800 px of image width.
- No card-with-icon scaffolds, no eyebrows above headings, no gradient text, no section numbers.
