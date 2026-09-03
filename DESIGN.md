# DESIGN.md — yuyupeng.com

Mode: **Experience.** The work leads; the interface recedes.

## Direction contract

**World** (client-pinned, Atelier Rhizome): a deep olive field with bone panels
floating on it, small quiet sans, hand-drawn botanical marks.

**Structure** (client-locked, dealt as concept 2 of 7 — *scattered photo-book*):
the panel is a **page**, not a column. Pictures are placed on it at deliberately
unequal sizes — a 2-column thumbnail beside a half-page anchor — at large
vertical offsets, some cropped by the page edge. Text appears as small blocks
dropped into the empty space, never as a caption strip under a picture. Well
over half of every page is empty, and that emptiness is the composition.

Explicitly rejected on the way here: the uniform thumbnail grid with one
full-width picture per row. It is the category default and the client refused it
by name.

## How the page is actually built

CSS Grid auto-placement cannot do this: an item starting at column 1 after an
item at column 9 is pushed to a new row, so pictures can never truly interleave.
Each **spread** is therefore a percentage canvas — `padding-bottom: var(--ar)`
sets its height from its width — and every element inside is absolutely
positioned at an authored `left / top / width` in percent. Aspect ratios do the
rest, so the whole composition scales with the viewport without a single
breakpoint in between.

Below 60rem the spread collapses to ordinary vertical flow at full width. A
phone has no room to scatter, and faking it just makes every picture tiny.

Compositions come from an authored library (`SPREADS` in `build.py`), not an
algorithm — a placement generator produces mush. Pictures are matched to slots
by aspect: the widest picture takes the widest slot.

## Colour

| Token | Value | Use |
|---|---|---|
| `--ground` | `#454E22` | the field the pages sit on |
| `--panel` | `#E8E6DC` | the page |
| `--ink` | `#31381A` | text on bone |
| `--ink-soft` | `#5E6440` | secondary text — 4.96:1 |
| `--on-ground` | `#E8E6DC` | text on olive — 7.2:1 |
| `--on-ground-soft` | `#B9BC9C` | secondary on olive — 4.56:1 |
| `--rule` | `rgba(49,56,26,.18)` | hairlines |
| `--moss` | `#7C8A3E` | botanical marks only — 3.0:1, display sizes |
| `--moss-text` | `#5F6B2C` | the only moss allowed on text — 4.56:1 |
| `--moss-lift` | `#9AA75A` | accents on the olive ground |

Secondary text is tinted from the olive hue in both directions. No greys.

## Type

**Familjen Grotesk**, self-hosted variable (400–700), latin + latin-ext + italic,
54 KB total. One family; hierarchy comes from size, weight and tracking.

Instrument Sans was the first choice and was replaced: the design detector flags
it as one of the faces every AI-generated interface converges on, and this site
cannot afford to look generated. Familjen Grotesk has real character in the a, g
and R while staying quiet at 11 px.

- Project title: `clamp(1.9rem, 4.4vw, 3.4rem)`, 500, tracking `-.032em`
- Statement: `clamp(1.5rem, 2.9vw, 2.35rem)`, 400
- Body and captions in the spreads: **0.8125rem / 0.6875rem** — small on purpose.
  In a photo-book the text is a margin note, not a column of prose. 11 px is the
  floor; nothing functional goes below it.
- Labels: 0.6875rem, 600, tracking `.12em`, uppercase

## Botanical marks

Authored inline SVG grass blades in `--moss`, each a tapered filled sliver. They
occupy slots in the scatter like any other element. Never emoji, never an icon font.

## Motion

One orchestrated moment: elements rise 14px and fade as they enter, staggered by
position, exponential ease-out. Gated on `html.js` so that with scripting off
every element is simply visible — the grid must never be blanked by a script
that failed. Elements already above the fold reveal immediately, and a 4s
fallback reveals everything regardless.

## Browser surfaces

Selection, caret, focus ring, scrollbar and `::marker` are themed from the
palette. Focus is a 2px moss ring with an offset, legible on both grounds.

## Rules

- Pictures are never enlarged past their own pixels — most come out of a print
  PDF at ~1250px, and the scatter's narrow slots are what keeps them sharp.
- Uniform anything is a regression: same-size tiles, one-picture-per-row,
  captions in a strip.
- No eyebrows above headings, no gradient text, no section numbers.

## Detector findings deliberately not acted on

`detect.mjs` reports four remaining classes. Each was judged, not ignored:

- **clipped-overflow-container** — `.page` carries `overflow:hidden` on purpose.
  Slots are authored past 100% so the page crops the picture at its edge, which
  is the reference's signature move.
- **cramped-padding** on `.panel` / `.mast` — the padding lives on the children
  (`.spread`, `.mast > *`), which the detector cannot see through. Verified in
  the captures: nothing sits flush.
- **gray-on-color** — `#E8E6DC` on `#454E22` in the footer is a warm bone tinted
  from the olive, not grey, at 7.21:1. Changing it would make the footer worse.
- **flat-type-hierarchy** — measured over the 11–17px band only. The home page
  steps to 37.6px at the statement and a project title reaches 54px.

## Capture discipline

`?eager=1` forces every picture to load and `?onepage` / `?probe` exist for
capture scripts. Full-page screenshots must use `--headless=new` **with**
`?eager=1`: the older headless mode silently drops images past the fold and
duplicates the page tail, which twice produced false defect reports.
