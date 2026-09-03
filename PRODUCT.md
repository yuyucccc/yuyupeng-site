# PRODUCT.md — yuyupeng.com

## What this is

The personal portfolio site of **Yuyu Peng**, a landscape architect based in Utrecht, NL.
It replaces sending a 53 MB PDF as the first thing a stranger sees.

## Who it is for

1. **Dutch hiring managers and studio principals** (gemeenten, landscape/urban design offices). They arrive from a CV, a LinkedIn message, or an application. They skim, look for built work and relevant scale, and decide in under a minute whether to keep reading.
2. **Collaborators and clients** checking who she is before a meeting.

Not for: recruiters harvesting contact data, or a general public audience.

## What success looks like

A visitor who lands cold can, within seconds, tell that she is a landscape architect working on Dutch public space, see real built work, and find a way to contact her. A visitor who is interested can go deep on any one project.

## Product truth

- 15 projects: 11 professional (Gemeente Utrecht, Buro Sant en Co), 4 academic.
- Three projects are **realised and photographed** (Kameleon, Van Eysingalaan) or in active delivery (KEI 3.0). These are the strongest evidence and lead the site.
- Everything is in **English**.
- Contact is **betweenness.u@outlook.com**; location is stated as Utrecht, NL.
- **No PDF or CV download**, no About page, no social links. Deliberate — the site is the portfolio.
- The statement "I perceive my role as a bridge between people and nature…" is her own words and leads the home page.

## Constraints

- Static HTML/CSS, no build step, no framework. Hosted on GitHub Pages at the apex domain `yuyupeng.com`.
- She is not a developer. Updating content must not require touching HTML — content lives in `content.json`, and `build.py` regenerates the pages.
- Images are extracted from the print PDF, so they are ~1800 px wide at best. The design must never demand more resolution than that.
- Three academic project texts are drafts written from drawings, flagged with `draft_note` in `content.json` — they need her approval before the site is announced.
