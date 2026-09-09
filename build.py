#!/usr/bin/env python3
"""
Regenerates the site from content.json + assets/img/manifest.json.

    python3 build.py

Edit content.json, run this, commit. Never edit the generated .html by hand.
"""
import json, os, re, html, shutil, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
IMG  = os.path.join(ROOT, "assets", "img")
DATA = json.load(open(os.path.join(ROOT, "content.json"), encoding="utf-8"))
MAN  = json.load(open(os.path.join(IMG, "manifest.json"), encoding="utf-8"))
SITE, PROJECTS = DATA["site"], DATA["projects"]
YEAR = datetime.date.today().year

e = lambda s: html.escape(str(s), quote=True)

# Foreign terms inside English prose take italic — the ordinary typographic
# convention, and it gives the page the roman/italic texture the type reference
# lives on without inventing emphasis that is not there. Place names stay roman.
FOREIGN = ["Definitief Ontwerp", "Voorlopig Ontwerp", "Sport- en speelplek",
           "Openbare ruimte", "Groenstructuur", "Stadsingenieurs", "Stedenbouw",
           "inrichtingsplan", "plankaart", "speelplaats", "blokplek", "daktuin",
           "Daktuin", "Speelplaats", "Blokplek", "Visie", "jeu de boules",
           "acqua alta", "Acqua alta"]
_FOREIGN_RE = re.compile(r"(?<![\w>])(" + "|".join(
    sorted((re.escape(w) for w in FOREIGN), key=len, reverse=True)) + r")(?![\w<])")

def it(escaped):
    """Wrap foreign terms in <em>. Input must already be HTML-escaped."""
    return _FOREIGN_RE.sub(r"<em>\1</em>", escaped)

EMD = "\u2014"   # em dash, kept out of f-string expressions (py3.9)

# ── authored botanical marks ────────────────────────────────────────────
# A tuft of tapered grass blades springing from one base line — drawn, not traced
# from a font. Each blade is a filled sliver: out along one curve, back along another.
BLADES = [
  "M20 78C30 62 47 50 69 42 47 55 32 66 26 78Z",
  "M46 78C50 56 58 34 75 13 64 38 58 58 54 78Z",
  "M78 78C76 50 80 26 93 2 88 28 86 52 86 78Z",
  "M104 78C108 54 121 32 141 14 124 36 114 56 112 78Z",
  "M130 78C142 62 161 50 185 44 162 56 146 66 138 78Z",
  "M60 78C58 66 60 56 67 46 64 58 64 68 66 78Z",
  "M92 78C96 66 105 58 117 52 106 60 100 68 98 78Z",
]
def mark(cls="mark", n=7, title=None):
    paths = "".join(
        f'<path d="{d}" opacity="{1 - i*0.055:.3f}"/>' for i, d in enumerate(BLADES[:n]))
    t = f"<title>{e(title)}</title>" if title else ""
    a11y = 'role="img"' if title else 'aria-hidden="true"'
    return (f'<svg class="{cls}" viewBox="0 0 200 82" fill="currentColor" '
            f'{a11y}>{t}{paths}</svg>')

ARROW = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
         'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
         '<path d="M5 12h14M13 6l6 6-6 6"/></svg>')
ARROW_BACK = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
              'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
              '<path d="M19 12H5M11 18l-6-6 6-6"/></svg>')

FAVICON = ('data:image/svg+xml,'
           '%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 62 62\'%3E'
           '%3Crect width=\'62\' height=\'62\' fill=\'%23454E22\'/%3E'
           '%3Cpath fill=\'%237C8A3E\' d=\'M8 57c14-16 22-35 24-56 5 22 0 42-16 58zM33 58C40 40 53 26 71 16 59 32 47 46 38 58z\'/%3E'
           '%3C/svg%3E')

def head(title, desc, rel, canonical):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(canonical)}">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(canonical)}">
<meta name="theme-color" content="#454E22">
<link rel="icon" href="{FAVICON}">
<link rel="preload" href="{rel}assets/fonts/Newsreader-latin.woff2" as="font" type="font/woff2" crossorigin>
<script>document.documentElement.className+=" js"</script>
<link rel="stylesheet" href="{rel}assets/css/site.css">
<link rel="stylesheet" href="{rel}assets/css/layout.css">
</head>
<body>"""

def masthead(rel, here=""):
    home = "Yuyu Peng" if here != "home" else "Yuyu Peng"
    return f"""
<header class="panel panel--flush">
 <div class="mast">
  <div><p class="name"><a href="{rel}">{home}</a></p></div>
  <div><p class="label">Landscape Architect</p></div>
  <div><p class="label">{e(SITE['location'])}</p></div>
  <div><p class="label"><a href="#contact" class="js-mail" data-u="{e(SITE['email'].split('@')[0])}" data-d="{e(SITE['email'].split('@')[1])}">Contact</a></p></div>
 </div>
</header>"""

def footer(rel):
    u, d = SITE["email"].split("@")
    return f"""
<footer class="foot wrap" id="contact">
 {mark("mark mark--foot", 5)}
 <div class="cols">
  <div>
   <p class="label">Email</p>
   <p><a class="js-mail" href="#contact" data-u="{e(u)}" data-d="{e(d)}"><span class="js-mail-txt">{e(u)}&#8203;<span aria-hidden="true"> [at] </span><span class="sr">@</span>&#8203;{e(d)}</span></a></p>
  </div>
  <div>
   <p class="label">Based in</p>
   <p>{e(SITE['location'])}</p>
  </div>
 </div>
 <p class="fine">© {YEAR} {e(SITE['name'])} · All project work shown was produced at Gemeente Utrecht and Buro Sant en Co, credited per project.</p>
</footer>
<script src="{rel}assets/js/site.js" defer></script>
</body>
</html>"""

def imgs_for(slug):
    return MAN.get(slug, [])

def hero_of(p):
    ims = imgs_for(p["slug"])
    if not ims: return None
    want = p.get("hero")
    for i in ims:
        if want and i["file"] == want: return i
    return ims[0]


# ── curtain ─────────────────────────────────────────────────────────────
# A solid field with circular apertures cut through it, the photograph behind.
# One click grows the apertures away. Positions are a fixed pseudo-random set,
# so the composition is stable between builds but never looks stepped.
def _holes(n=42, seed=20260903):
    s = seed
    def rnd():
        nonlocal s
        s = (s * 1103515245 + 12345) & 0x7FFFFFFF
        return s / 0x7FFFFFFF
    out, placed = [], []
    guard = 0
    while len(out) < n and guard < 4000:
        guard += 1
        r = 1.8 + rnd() * 4.2
        cx, cy = 3 + rnd() * 94, 4 + rnd() * 84
        if any(((cx-x)**2 + (cy-y)**2) ** .5 < (r + rr + 1.4) for x, y, rr in placed):
            continue
        placed.append((cx, cy, r))
        out.append('<circle cx="%.2f" cy="%.2f" r="%.2f" fill="#000"/>' % (cx, cy, r))
    return "".join(out)

def curtain(rel, photo, say):
    return ('<div class="curtain" id="curtain" hidden>'
            '<svg viewBox="0 0 100 100" preserveAspectRatio="xMidYMid slice" aria-hidden="true">'
            '<defs><mask id="apertures" maskUnits="userSpaceOnUse" x="0" y="0" width="100" height="100">'
            '<rect width="100" height="100" fill="#fff"/>'
            '<g class="holes">' + _holes() + '</g>'
            '</mask></defs>'
            '<image href="' + rel + photo + '" x="0" y="0" width="100" height="100"'
            ' preserveAspectRatio="xMidYMid slice"/>'
            '<rect width="100" height="100" fill="#454E22" mask="url(#apertures)"/>'
            "</svg>"
            '<div class="curtain__ui">'
            '<p class="curtain__say">' + e(say) + "</p>"
            '<button class="curtain__go" type="button" id="curtain-go">See the work</button>'
            "</div></div>")

# ── spreads: authored compositions ─────────────────────────────────────
# Each spread is a percentage canvas. "ar" is its height as a percent of its own
# width; every slot is (role, left%, top%, width%). Slots may run past 100 or
# start below 0 — that is a picture cropped by the page edge, which the reference
# does on nearly every spread. A generator would produce mush, so these are set
# by hand and matched to pictures by aspect: widest picture into the widest slot.


# A slot at top t% whose content is H width-units tall needs the canvas to be at
# least H / (1 - t/100) tall, or it spills past the canvas and lands on the next
# spread. Authored "ar" is the intent; this raises it to whatever the content
# actually needs, so compositions can be written freely and never collide.
LABEL_U = 3.6          # a tile's title + place, in width-units
CAP_U   = 2.4          # a figure caption

def txt_units(s, w, px=13.0, lh=1.66):
    """Rough height of a text block, in width-units (% of page width)."""
    if not s: return 0.0
    page = 1500.0
    cw = px * 0.5
    cpl = max(8.0, (w / 100.0) * page / cw)
    lines = max(1, int(len(s) / cpl + 0.999))
    return lines * px * lh / page * 100.0

def need_ar(items, floor):
    """items: (top%, height_in_width_units). Returns the canvas height needed."""
    a = float(floor)
    for t, h in items:
        if h <= 0: continue
        room = 1.0 - t / 100.0
        if room <= 0.02: continue
        a = max(a, h / room)
    return round(a, 1)

def picture(slug, i, rel, alt, w_pct, eager=False):
    """900px at 1x, the original as 2x. Slots are 12-60% of a page that is at
    most ~92vw, so nothing here ever needs more than 900 CSS px at 1x."""
    d = rel + "assets/img/" + slug + "/"
    small, big = d + i.get("w900", i["file"]), d + i["file"]
    sizes = "(min-width:60rem) %.0fvw, 92vw" % max(8.0, w_pct * 0.92)
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    srcset = ""
    if i.get("w900") and i["w900"] != i["file"]:
        srcset = (' srcset="' + small + " " + str(i.get("w900w", 900)) + "w, "
                  + big + " " + str(i["w"]) + 'w" sizes="' + sizes + '"')
    return ('<img src="' + small + '"' + srcset
            + ' width="' + str(i["w"]) + '" height="' + str(i["h"]) + '"'
            + " " + load + ' decoding="async" alt="' + e(alt) + '">')


def box(l, t, w):
    return "--l:{}%;--t:{}%;--w:{}%".format(l, t, w)

def el(tag, style, inner, cls=""):
    c = ' class="' + cls + '"' if cls else ""
    return "<" + tag + c + ' style="' + style + '">' + inner + "</" + tag + ">"

# image-only spreads, keyed by how many pictures they hold
SPREADS = {
 1: [
   (44, [("img", 12,  0, 62)]),
   (36, [("img", 34,  0, 72)]),
 ],
 2: [
   (52, [("img", 14,  0, 26), ("img", 52, 16, 52)]),
   (66, [("img", -3,  5, 52), ("img", 64,  0, 20)]),
   (44, [("img", 30,  0, 74), ("img",  0, 26, 16)]),
 ],
 3: [
   (58, [("img",  0,  6, 16), ("img", 22, -4, 32), ("img", 60, 16, 44)]),
   (64, [("img",  0,  3, 48), ("img", 54,  0, 14), ("img", 72, 28, 30)]),
   (42, [("img",  2,  0, 15), ("img", 24, 12, 20), ("img", 52,  2, 50)]),
 ],
 4: [
   (72, [("img", -2,  7, 50), ("img", 56,  0, 15), ("img", 56, 24, 15), ("img", 78, 38, 26)]),
   (68, [("img", 26, -5, 20), ("img", 54,  2, 48), ("img",  0, 24, 22), ("img", 34, 40, 34)]),
 ],
 5: [
   (82, [("img", 42, -6, 16), ("img", 66, -3, 38), ("img",  0, 14, 18),
         ("img", 30, 28, 16), ("img",  2, 50, 56)]),
 ],
}

# the opening spread: scatter from the first pixel, not a banner then content
OPEN = (72, [("ttl",  0,  4, 34), ("img", 52, -6, 21), ("img", 80,  2, 20),
             ("led",  0, 30, 26), ("hero", 40, 34, 60)])

# the words spread: prose as margin notes among pictures
WORDS = (56, [("bd1", 0, 3, 25), ("bd2", 29, 19, 25), ("fct", 85, 1, 15),
              ("img", 55, 31, 45), ("img", 0, 42, 21)])


def collide(ar, boxes, where):
    """boxes: (left%, top%, w%, aspect_h_over_w). Warn on any real overlap.
    top% resolves against the canvas height (= width * ar/100), so convert it
    into width-units before comparing with a picture's own height."""
    rects = []
    for l, t, w, hw in boxes:
        top_u = t * ar / 100.0
        rects.append((l, top_u, l + w, top_u + w * hw))
    for i in range(len(rects)):
        for j in range(i + 1, len(rects)):
            a, b = rects[i], rects[j]
            ox = min(a[2], b[2]) - max(a[0], b[0])
            oy = min(a[3], b[3]) - max(a[1], b[1])
            if ox > 0.4 and oy > 0.4:
                print("  ! overlap in %s: slot %d x slot %d (%.1f%% x %.1f%%)"
                      % (where, i, j, ox, oy))


def fill(slots, images, imhtml, capof):
    """Widest picture into the widest slot; text slots pass through untouched."""
    idx = [k for k, s in enumerate(slots) if s[0] in ("img", "hero")]
    idx.sort(key=lambda k: -slots[k][3])
    ranked = sorted(images, key=lambda i: -(i["w"] / i["h"]))
    return dict(zip(idx, ranked))


def spread(ar, slots, images, imhtml, capof, texts=None, eager_first=False):
    texts = texts or {}
    assign = fill(slots, images, imhtml, capof)

    need = []
    for k, (role, l, t, w) in enumerate(slots):
        if role in ("img", "hero"):
            img = assign.get(k)
            if img:
                h = w * img["h"] / img["w"] + (CAP_U if capof(img) else 0)
                need.append((t, h))
        else:
            need.append((t, txt_units(re.sub("<[^>]+>", "", texts.get(role, "")), w,
                                      37.0 if role in ("stm",) else
                                      18.0 if role in ("ttl",) else
                                      16.0 if role in ("led",) else 13.0,
                                      1.24 if role in ("stm", "ttl") else 1.55)))
    ar = need_ar(need, ar)
    out, used = [], []
    for k, (role, l, t, w) in enumerate(slots):
        st = box(l, t, w)
        if role in ("img", "hero"):
            img = assign.get(k)
            if not img: continue
            used.append(img)
            cap = capof(img)
            fc = "<figcaption>" + it(e(cap)) + "</figcaption>" if cap else ""
            out.append(el("figure", st, imhtml(img, eager_first and role == "hero", w) + fc,
                          "pl rise"))
        else:
            inner = texts.get(role, "")
            if inner:
                out.append(el("div", st, inner, "rise"))
    boxes = []
    for k, (role, l, t, w) in enumerate(slots):
        img = assign.get(k)
        if role in ("img", "hero") and img:
            boxes.append((l, t, w, img["h"] / img["w"]))
    if boxes: collide(ar, boxes, "spread ar=%s" % ar)
    body = "\n   ".join(out)
    return ('<div class="spread" style="--arn:' + str(ar) + '">\n   '
            + body + "\n  </div>"), used


def pack(images, imhtml, capof, seed=0):
    """Lay the remaining pictures out over a varied run of authored spreads."""
    out, i, turn = [], 0, seed
    while i < len(images):
        left = len(images) - i
        n = 5 if left >= 5 else left
        while n > 1 and n not in SPREADS:
            n -= 1
        opts = SPREADS[n]
        ar, slots = opts[turn % len(opts)]
        html_, used = spread(ar, slots, images[i:i+n], imhtml, capof)
        out.append(html_)
        i += n; turn += 1
    return "\n  ".join(out)


# ── home ────────────────────────────────────────────────────────────────
# Authored per spread. The three current/realised projects take the anchors.
HOME_OPEN = (64, [("stm",  0,  5, 34), ("mrk", 80,  5, 16), ("sub", 80, 23, 18),
                  ("t0",  40,  1, 38), ("t1",  0, 56, 26), ("t2", 62, 44, 36)])
# Width range 12-48 and slots that run past the page edge on purpose: a picture
# cropped by the page boundary is the reference's signature move.
# Every slot stays inside 0..100. Sizes still differ hard, but no picture is
# ever cut off by the page edge — the client asked for whole pictures.
HOME_SPREADS = [
  (56, [("t",  0,  8, 14), ("t", 22,  0, 30), ("t", 58, 18, 40)]),
  (68, [("t",  0,  4, 30), ("t", 34, 30, 22), ("t", 62,  0, 22), ("t", 86, 34, 14)]),
  (50, [("t",  8,  0, 44), ("t", 60, 22, 18), ("t", 82,  2, 14)]),
  (60, [("t",  0, 30, 22), ("t", 28,  0, 16), ("t", 50, 14, 46)]),
  (46, [("t", 30,  0, 12), ("t", 48, 20, 26), ("t", 78,  0, 22)]),
]

# Foliage, not a scene. Every aperture has to land on something worth seeing,
# and only an all-over texture reads at circle size.
CURTAIN_PHOTO = "assets/img/_cover/01.jpg"

def render_home():
    def tile(p, w_pct=26.0):
        h = hero_of(p)
        if not h: return ""
        return ('<a class="tile" href="work/' + p["slug"] + '/">'
                + picture(p["slug"], h, "", p["title"] + " \u2014 " + p["place"], w_pct)
                + '<span class="tile__t">' + e(p["title"]) + "</span>"
                '<span class="tile__m">' + e(p["place"]) + " &middot; "
                + e(p["years"]) + "</span></a>")

    pro = [p for p in PROJECTS if p["group"] == "professional"]
    aca = [p for p in PROJECTS if p["group"] == "academic"]
    st = SITE["statement"].replace("bridge between people and nature",
            "<em>bridge between people and nature</em>", 1)

    # opening: the statement is one element among pictures, not a banner
    ar, slots = HOME_OPEN
    texts = {
      "stm": '<h1 class="statement">' + st + "</h1>",
      "mrk": mark("mark mark--cell", 7, "Grass"),
      "sub": '<p class="blk blk--soft blk--fine">Selected public space, playground and '
             'urban landscape projects for Gemeente Utrecht and Buro Sant en Co, and '
             'academic work from Delft and Shenzhen.</p>',
      "t0": tile(pro[0], 40), "t1": tile(pro[1], 26), "t2": tile(pro[2], 40),
    }
    op, need = [], []
    for role, l, t, w in slots:
        inner = texts.get(role, "")
        if not inner: continue
        op.append(el("div", box(l, t, w), inner, "rise"))
        if role.startswith("t") and role[1:].isdigit():
            pr = [pro[0], pro[1], pro[2]][int(role[1:])]
            h0 = hero_of(pr)
            need.append((t, w * h0["h"] / h0["w"] + LABEL_U if h0 else 0))
        elif role == "mrk":
            need.append((t, w * 0.41))
        else:
            need.append((t, txt_units(re.sub("<[^>]+>", "", inner), w,
                                      37.0 if role == "stm" else 12.0,
                                      1.24 if role == "stm" else 1.6)))
    ar = need_ar(need, ar)
    opening = ('<div class="spread" style="--arn:' + str(ar) + '">\n   '
               + "\n   ".join(op) + "\n  </div>")

    # the rest of the index, over authored spreads
    rest = pro[3:] + aca
    blocks, i, turn = [], 0, 0
    while i < len(rest):
        ar, slots = HOME_SPREADS[turn % len(HOME_SPREADS)]
        n = min(len(slots), len(rest) - i)
        cells, need = [], []
        for (role, l, t, w), p in zip(slots[:n], rest[i:i+n]):
            cells.append(el("div", box(l, t, w), tile(p, w), "rise"))
            h0 = hero_of(p)
            if h0: need.append((t, w * h0["h"] / h0["w"] + LABEL_U))
        ar2 = need_ar(need, ar)
        blocks.append('<div class="spread" style="--arn:' + str(ar2) + '">\n   '
                      + "\n   ".join(cells) + "\n  </div>")
        i += n; turn += 1

    return f"""{head(f"{SITE['name']} {EMD} {SITE['role']}, {SITE['location']}", SITE['meta_description'], "", f"https://{SITE['domain']}/")}
<main class="wrap">
{masthead("", "home")}
 {curtain("", CURTAIN_PHOTO, SITE["curtain_say"])}
 <section class="panel page">
  {opening}
  {"".join(chr(10) + "  " + b for b in blocks)}
 </section>
</main>
{footer("")}"""

# ── project page ────────────────────────────────────────────────────────
# Not the index's scatter. A project opens as one main picture beside its
# information, then runs down the page as aligned figures — reading a project
# is a sequence, not a search. Nothing here is cropped except the opening
# picture, which fills its half the way a full-bleed plate fills a page.
def render_project(p, nxt):
    ims  = imgs_for(p["slug"])
    hero = hero_of(p)
    rest = [i for i in ims if i is not hero]
    caps = p.get("captions", {})
    slug, T = p["slug"], p["title"]

    def capof(i): return caps.get(i["file"].split(".")[0])
    def im(i, eager=False, w_pct=50.0):
        cap = capof(i)
        alt = T + " " + EMD + " " + (cap if cap else "project drawing")
        return picture(slug, i, "../../", alt, w_pct, eager)
    def fig(i, cls, w_pct):
        cap = capof(i)
        fc = "<figcaption>" + it(e(cap)) + "</figcaption>" if cap else ""
        return '<figure class="' + cls + ' rise">' + im(i, False, w_pct) + fc + "</figure>"

    paras = list(p["body"])
    lead_para = paras.pop(0) if paras else ""
    note = ('<p class="blk blk--fine blk--soft" style="margin-top:1rem">'
            + e(p["draft_note"]) + "</p>") if p.get("draft_note") else ""

    # ── opening: picture left, information right ──
    inset = rest.pop(0) if rest else None
    inset_html = ""
    if inset:
        cap = capof(inset)
        fc = "<figcaption>" + it(e(cap)) + "</figcaption>" if cap else ""
        inset_html = ('<figure class="split__inset">' + im(inset, False, 29) + fc + "</figure>")
    hero_html = ""
    if hero:
        hero_html = '<div class="split__img">' + im(hero, True, 50) + "</div>"

    opening = ('<section class="split">' + hero_html
        + '<div class="split__info">'
        + '<p class="pkicker">' + e(p["place"]) + " &middot; " + e(p["years"]) + "</p>"
        + '<h1 class="ptitle">' + e(T) + "</h1>"
        + '<p class="plead">' + it(e(p["lead"])) + "</p>"
        + inset_html
        + '<div class="split__tail"><div class="blk">' + "<p>" + it(e(lead_para)) + "</p></div></div>"
        + "</div></section>")

    # ── the run: figures in a legible sequence, prose interleaved ──
    blocks, i, flip, used_text = [], 0, False, 0
    while i < len(rest):
        a = rest[i]
        ar = a["w"] / a["h"]
        nx = rest[i + 1] if i + 1 < len(rest) else None
        if paras and used_text < len(paras) and i % 2 == 1:
            side = " withtext--flip" if flip else ""
            blocks.append('<div class="withtext' + side + '">'
                          + fig(a, "fig", 58)
                          + '<div class="blk">' + "<p>" + it(e(paras[used_text])) + "</p>"
                          + (note if used_text == len(paras) - 1 else "") + "</div></div>")
            used_text += 1
        elif ar >= 2.2:
            blocks.append(fig(a, "fig", 92))
        elif ar >= 1.5:
            blocks.append(fig(a, "fig fig--w66" + (" fig--right" if flip else ""), 60))
        elif nx and (nx["w"] / nx["h"]) < 1.5:
            blocks.append('<div class="pair">' + fig(a, "fig", 44) + fig(nx, "fig", 44) + "</div>")
            i += 1
        else:
            blocks.append(fig(a, "fig fig--w50" + (" fig--right" if flip else ""), 45))
        flip = not flip
        i += 1

    while used_text < len(paras):
        blocks.append('<div class="blk rise">' + "<p>" + it(e(paras[used_text])) + "</p>"
                      + (note if used_text == len(paras) - 1 else "") + "</div>")
        used_text += 1
    if not paras and note:
        blocks.append('<div class="blk rise">' + note + "</div>")

    facts = "".join('<div class="frow"><dt>' + e(k) + "</dt><dd>" + it(e(v)) + "</dd></div>"
                    for k, v in p["meta"])
    blocks.append('<dl class="facts rise">' + facts + "</dl>")
    run = '<section class="run">' + "".join(blocks) + "</section>"

    return f"""{head(f"{p['title']} {EMD} {SITE['name']}", p['lead'], "../../", f"https://{SITE['domain']}/work/{p['slug']}/")}
<main class="wrap">
{masthead("../../")}
 <article>
  <p style="margin:0 0 var(--gut)"><a class="back back--onground" href="../../">{ARROW_BACK}<span>All work</span></a></p>
  {opening}
  {run}
  <a class="next panel panel--flush" href="../{nxt['slug']}/">
   <span>
    <span class="label">Next project</span>
    <strong style="display:block;margin-top:.3rem">{e(nxt['title'])}</strong>
   </span>
   {ARROW}
  </a>
 </article>
</main>
{footer("../../")}"""



# ── the mark ────────────────────────────────────────────────────────────
# Taken straight out of her logo2.ai, not redrawn by eye. The Bézier points and
# the gradient functions below were read out of that file's PDF operators, and
# the tone curve was measured against a 1:1 render of the original: her CMYK
# 100% K lands on rgb(55,55,55), a soft charcoal, and she asked to keep it.
#
# The file holds three forms. They are not three logos — they are one object at
# three stages of turning into the light: wire, filled, inverted. So the whole
# animation vocabulary is already in her drawing; nothing has to be invented.

INK = 55                             # her CMYK black, converted for screen
DOM = 0.997963                       # where Illustrator ended every gradient

# Centre-relative, in the file's own points, y as Illustrator wrote it (up).
# Two overlapping circles: r 67.717 at ±51.106 (the body), r 79.493 at ±59.993
# (the ring that floats outside it).
_IN_A = [(0, -44.429),
         (12.415, -58.698), (30.707, -67.717), (51.106, -67.717),
         (88.505, -67.717), (118.823, -37.399), (118.823, 0),
         (118.823, 37.399), (88.505, 67.717), (51.106, 67.717),
         (30.707, 67.717), (12.415, 58.698), (0, 44.429)]
_IN_B = [(0.001, 44.428),
         (-12.414, 58.697), (-30.706, 67.717), (-51.106, 67.717),
         (-88.505, 67.717), (-118.823, 37.399), (-118.823, 0),
         (-118.823, -37.399), (-88.505, -67.717), (-51.106, -67.717),
         (-30.706, -67.717), (-12.414, -58.697), (0.001, -44.428)]
_OUT_A = [(0, -52.155),
          (14.574, -68.905), (36.047, -79.493), (59.993, -79.493),
          (103.896, -79.493), (139.487, -43.903), (139.487, 0),
          (139.487, 43.903), (103.896, 79.493), (59.993, 79.493),
          (36.047, 79.493), (14.574, 68.905), (0, 52.155)]
_OUT_B = [(0.002, 52.154),
          (-14.572, 68.905), (-36.046, 79.493), (-59.993, 79.493),
          (-103.896, 79.493), (-139.486, 43.903), (-139.486, 0),
          (-139.486, -43.903), (-103.896, -79.493), (-59.993, -79.493),
          (-36.046, -79.493), (-14.572, -68.906), (0.002, -52.154)]


def _path(a, b):
    "Illustrator's y-up points as one SVG outline."
    f = lambda p: "%.3f %.3f" % (p[0], -p[1])
    out = ["M " + f(a[0])]
    for i in range(1, 13, 3):
        out.append("C " + " ".join(f(a[i + j]) for j in range(3)))
    out.append("L " + f(b[0]))
    for i in range(1, 13, 3):
        out.append("C " + " ".join(f(b[i + j]) for j in range(3)))
    return " ".join(out) + " Z"


BODY = _path(_IN_A, _IN_B)           # the filled shape, and form 1's inner wire
RING = _path(_OUT_A, _OUT_B)         # the wire outside it

# The gradients, evaluated from the file's own stitching functions. Each returns
# ink coverage 0–1 at radius s (1 = the gradient's own edge).
def _g_wire(s):  return 0.0 if s >= DOM else 1 - (s / DOM) ** 3.40967
def _g_body(s):  return 0.0 if s >= DOM else 1 - (s / DOM) ** 1.2964
def _g_halo(s):  return 0.0 if s >= DOM else (1 - s / DOM) ** 1.65097
def _g_lit(s):   return 0.66 * (1 - s)
def _g_wire3(s):
    if s < 0.118457: return 1.0
    if s < 0.39126:  return 1 - (s - 0.118457) / 0.272803 * 0.119708
    return 0.880292 * (1 - (s - 0.39126) / 0.60874)


def _grad(gid, r, fn, cx=0.0, cy=0.0, n=22):
    stops = "".join('<stop offset="%.4f" stop-color="currentColor" stop-opacity="%.4f"/>'
                    % (i / n, fn(i / n)) for i in range(n + 1))
    return ('<radialGradient id="%s" gradientUnits="userSpaceOnUse" cx="%g" cy="%g" r="%g">'
            '%s</radialGradient>' % (gid, cx, cy, r, stops))


def _lit(idp, key, d, gid, width=None):
    """Ink laid through a shape, so the outline can never move and only the light
    inside it does. The shape becomes a mask and the gradient rides a plate
    behind it that the animation is free to turn or scale. Mask ids end in
    "msk" and gradient ids in "g" — share one namespace and url(#…) silently
    resolves to the wrong node, which drops the mask and floods the frame."""
    m = idp + key + "msk"
    if width is None:
        cut = '<path d="%s" fill="#fff"/>' % d
    else:
        cut = ('<path d="%s" fill="none" stroke="#fff" stroke-width="%g" '
               'stroke-linejoin="round" stroke-linecap="round"/>' % (d, width))
    return ('<mask id="%s" maskUnits="userSpaceOnUse" x="-320" y="-320" width="640" height="640">'
            '%s</mask>'
            '<g mask="url(#%s)"><g class="turn turn--%s">'
            '<rect x="-320" y="-320" width="640" height="640" fill="url(#%s)"/></g></g>'
            % (m, cut, m, key, gid))


def logo_mark(idp="m", forms=(1, 2, 3), ox=0.0, oy=0.0, cls="mark__svg",
              vb="-176 -170 352 340"):
    """Her three forms in one SVG, each in its own layer so CSS can cross-fade,
    stack or gate them. ox/oy pushes the gradient centres off the middle: at 0,0
    every form is pixel-for-pixel the drawing she handed over, and an orbit has
    nothing to move, so the turning variants ask for an offset."""
    ink = "rgb(%d,%d,%d)" % (INK, INK, INK)
    g, layers = [], []

    for form in forms:
      if form == 1:
        g += [_grad(idp + "1ag", 98.1547, _g_wire, ox, oy),
              _grad(idp + "1bg", 114.972, _g_wire, ox, oy)]
        layers.append('<g class="f f1">%s%s</g>'
                      % (_lit(idp, "1a", BODY, idp + "1ag", 3),
                         _lit(idp, "1b", RING, idp + "1bg", 2)))
      elif form == 2:
        g += [_grad(idp + "2ag", 96.7072, _g_body, ox, oy),
              _grad(idp + "2bg", 114.972, _g_wire, ox, oy)]
        layers.append('<g class="f f2">%s%s</g>'
                      % (_lit(idp, "2a", BODY, idp + "2ag"),
                         _lit(idp, "2b", RING, idp + "2bg", 3)))
      else:
        # form 3 is the inverted one: the body is painted light *over* the halo,
        # so it needs an opaque knockout the other two do not.
        g += [_grad(idp + "3hg", 165.667, _g_halo, -4.327 + ox, -0.971 + oy),
              _grad(idp + "3ag", 96.7072, _g_lit, ox, oy),
              _grad(idp + "3bg", 114.489, _g_wire3, ox, oy),
              '<mask id="%s3hmsk" maskUnits="userSpaceOnUse" x="-320" y="-320" '
              'width="640" height="640"><circle cx="-4.327" cy="-0.971" r="165.667" '
              'fill="#fff"/></mask>' % idp]
        layers.append('<g class="f f3">'
                      '<g mask="url(#%s3hmsk)"><g class="turn turn--3h">'
                      '<rect x="-320" y="-320" width="640" height="640" fill="url(#%s3hg)"/></g></g>'
                      '<path d="%s" fill="var(--paper,#fff)"/>%s%s</g>'
                      % (idp, idp, BODY,
                         _lit(idp, "3a", BODY, idp + "3ag"),
                         _lit(idp, "3b", RING, idp + "3bg", 2)))

    return ('<svg class="%s" viewBox="%s" color="%s" aria-hidden="true">'
            '<defs>%s</defs>%s</svg>' % (cls, vb, ink, "".join(g), "".join(layers)))


# ── v2 home: front + gallery on one page ────────────────────────────────
# The mark is two overlapping rings — an eye you look through. Click it and a
# film burn hands you the constellation: the mark shrinks to the centre and ten
# projects hang off it on straight threads.
#
# Every project is a real <a> with real text in the source from the start. It is
# only *positioned* by CSS, never injected by script, so a crawler and a screen
# reader both get the whole list even though the page looks like a canvas.

GALLERY = ["kameleon-speelplaats", "kei-3-0", "van-eysingalaan", "city-nieuwegein",
           "groene-zoom", "parkstraat", "kloppend-hart-soest", "jaarbeursplein",
           "de-koploper", "sport-dak-park"]

# centre x%, centre y%, width% — a loose ring around the mark, sizes varied hard,
# nothing closer than ~18% to the centre where the mark sits.
# Held off the margins by about the distance the motion can travel, so a
# picture near an edge still has somewhere to go and does not spend its life
# pinned against the glass.
NODES = [(28, 24, 14), (48, 16, 10), (72, 20, 12), (84, 54, 10), (76, 67, 13),
         (56, 80, 11), (34, 76, 13), (18, 62, 10), (17, 35, 11), (66, 41, 8)]

FAVICON_V2 = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
              "viewBox='0 0 64 64'%3E%3Crect width='64' height='64' fill='%23fff'/%3E"
              "%3Ccircle cx='25' cy='32' r='15' fill='none' stroke='%23000' stroke-width='3'/%3E"
              "%3Ccircle cx='39' cy='32' r='15' fill='none' stroke='%23000' stroke-width='3'/%3E"
              "%3C/svg%3E")

STORY = ('I perceive my role as a <em>bridge between people and nature</em>. '
         'Public space, playgrounds and urban landscapes for Gemeente Utrecht '
         'and Buro Sant en Co.')

def render_home_v2():
    idx = {p["slug"]: p for p in PROJECTS}
    picks = [idx[s] for s in GALLERY if s in idx]

    nodes, threads = [], []
    for i, ((x, y, w), p) in enumerate(zip(NODES, picks)):
        h = hero_of(p)
        if not h:
            continue
        alt = p["title"] + " " + EMD + " " + p["place"]
        # Depth: the small pictures read as further off, so they answer the
        # pointer hardest and drift widest. Widths run 8–14%.
        dz = round(1.35 - (w - 8) * 0.075, 3)
        nodes.append(
            '<a class="node" style="--x:%d%%;--y:%d%%;--w:%d%%;--dz:%g" href="work/%s/">'
            % (x, y, w, dz, p["slug"])
            + '<span class="node__d"><span class="node__in">'
            + picture(p["slug"], h, "", alt, w)
            + '<span class="node__t">' + e(p["title"]) + "</span>"
            + '<span class="node__m">' + e(p["place"]) + ", " + e(p["years"])
            + "</span></span></span></a>")
        threads.append('<line x1="50" y1="50" x2="%d" y2="%d"/>' % (x, y))

    u, d = SITE["email"].split("@")
    tpl = open(os.path.join(ROOT, "templates", "home.html"), encoding="utf-8").read()
    for k, v in [
        ("TITLE", e(SITE["name"] + " " + EMD + " " + SITE["role"] + ", " + SITE["location"])),
        ("DESC", e(SITE["meta_description"])),
        ("DOMAIN", SITE["domain"]),
        ("FAVICON", FAVICON_V2),
        ("STORY", STORY),
        ("PLACE", e(SITE["location"])),
        ("MAIL_U", e(u)), ("MAIL_D", e(d)),
        # Light-DOM children of a custom element stop rendering the moment it
        # upgrades, so this is the mark with no script: form 1, framed in the
        # component's own box so nothing shifts when the animation takes over.
        ("EYE", logo_mark("h", forms=(1,), cls="mark__still",
                          vb="-210 -155 420 310")),
        ("THREADS", "\n  ".join(threads)),
        ("NODES", "\n  ".join(nodes)),
    ]:
        tpl = tpl.replace("{{" + k + "}}", v)
    return tpl

# ── static extras ───────────────────────────────────────────────────────
JS = """// ── curtain ───────────────────────────────────────────────────────────
// The home opens behind a solid field with apertures cut through it. Click
// anywhere (or the button, or Escape) and the apertures grow away. Shown once
// per session: coming back from a project should not replay it.
(function(){
  var c = document.getElementById('curtain');
  if (!c) return;
  var seen = false;
  try { seen = sessionStorage.getItem('yp-seen') === '1'; } catch (e) {}
  // capture hooks skip the curtain so a full-page screenshot shows the index
  if (seen || /[?&](eager|nocurtain)/.test(location.search)) { c.remove(); return; }

  c.hidden = false;
  document.body.classList.add('curtain-up');
  var quick = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function open(){
    if (c.dataset.going) return;
    c.dataset.going = '1';
    try { sessionStorage.setItem('yp-seen', '1'); } catch (e) {}
    document.body.classList.remove('curtain-up');
    if (quick) { c.remove(); return; }
    c.classList.add('opening');
    setTimeout(function(){ c.classList.add('gone'); }, 780);
    setTimeout(function(){ c.remove(); }, 1750);
  }
  c.addEventListener('click', open);
  addEventListener('keydown', function(ev){
    if (ev.key === 'Escape' || ev.key === 'Enter' || ev.key === ' ') open();
  });
  var go = document.getElementById('curtain-go');
  if (go) { go.focus({ preventScroll: true }); }
})();

document.querySelectorAll('.js-mail').forEach(function(a){
  var addr = a.dataset.u + '@' + a.dataset.d;
  a.href = 'mailto:' + addr;
  var t = a.querySelector('.js-mail-txt');
  if (t) t.textContent = addr;
});

var rise = [].slice.call(document.querySelectorAll('.rise'));
function reveal(el){ el.classList.add('in'); }
function revealAll(){ rise.forEach(reveal); }

if (window.matchMedia('(prefers-reduced-motion: reduce)').matches || !('IntersectionObserver' in window)) {
  revealAll();
} else {
  var io = new IntersectionObserver(function(entries){
    entries.forEach(function(en, i){
      if (!en.isIntersecting) return;
      var el = en.target;
      setTimeout(function(){ reveal(el); }, Math.min(i, 5) * 55);
      io.unobserve(el);
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });

  rise.forEach(function(el){
    // Anything already at or above the fold — including content the reader
    // jumped past with an anchor or a restored scroll position — is shown at
    // once. An observer alone never fires for those and would strand them.
    if (el.getBoundingClientRect().top < window.innerHeight) { reveal(el); return; }
    io.observe(el);
  });

  // Last resort: nothing on this site may stay invisible.
  setTimeout(revealAll, 4000);
}

// Lazy-loading has failed on this layout before (absolutely positioned plates
// inside a ratio-sized canvas). If an image is on screen and still has not
// decoded, stop waiting for the browser and fetch it.
// Capture-only hooks: ?probe reports the document height in the title so a
// screenshot script can size itself, and ?y scrolls to an offset so a tall page
// can be captured in segments at a normal viewport (where lazy-loading behaves).
(function(){
  var q = new URLSearchParams(location.search);
  if (q.has('y')) addEventListener('load', function(){
    setTimeout(function(){ window.scrollTo(0, parseInt(q.get('y'), 10) || 0); }, 400);
  });
  // ?onepage makes the whole document one PDF page, so --print-to-pdf yields a
  // valid full-page capture without relying on scroll or an over-tall window.
  if (q.has('onepage')) addEventListener('load', function(){
    setTimeout(function(){
      var w = document.documentElement.scrollWidth;
      var h = document.documentElement.scrollHeight;
      var s = document.createElement('style');
      s.textContent = '@page{size:' + w + 'px ' + h + 'px;margin:0}'
                    + 'html,body{width:' + w + 'px}';
      document.head.appendChild(s);
    }, 700);
  });
  if (q.has('probe')) addEventListener('load', function(){
    setTimeout(function(){
      document.title = 'H=' + document.documentElement.scrollHeight
                     + ' V=' + window.innerHeight;
    }, 900);
  });
})();

// ?eager=1 loads every picture up front. Used only for full-page capture, so
// screenshots are valid evidence rather than a half-decoded page.
if (location.search.indexOf('eager') > -1) {
  document.querySelectorAll('img[loading="lazy"]').forEach(function(im){ im.loading = 'eager'; });
}
function rescueImages(){
  document.querySelectorAll('img[loading="lazy"]').forEach(function(im){
    if (im.complete && im.naturalWidth > 0) return;
    var r = im.getBoundingClientRect();
    if (r.bottom > -600 && r.top < window.innerHeight + 600) im.loading = 'eager';
  });
}
addEventListener('scroll', rescueImages, { passive: true });
addEventListener('resize', rescueImages, { passive: true });
setTimeout(rescueImages, 1200);
setTimeout(rescueImages, 3500);
"""

NOT_FOUND = f"""{head(f"Not found {EMD} {SITE['name']}", "That page does not exist.", "", f"https://{SITE['domain']}/404.html")}
<main class="wrap">
{masthead("")}
 <section class="panel page">
  <div class="spread" style="--arn:34">
   <div style="--l:0%;--t:12%;--w:46%">
    {mark("mark mark--cell", 5)}
    <h1 class="statement" style="margin-top:1.6rem">That page isn&rsquo;t here.</h1>
    <p class="blk blk--soft" style="margin-top:1.2rem">The link may be old, or the address mistyped.</p>
    <p style="margin-top:2rem"><a class="back" href="/">{ARROW_BACK}<span>All work</span></a></p>
   </div>
  </div>
 </section>
</main>
{footer("")}"""

def write(path, s):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(s)

def main():
    write(os.path.join(ROOT, "index.html"), render_home_v2())
    for i, p in enumerate(PROJECTS):
        nxt = PROJECTS[(i + 1) % len(PROJECTS)]
        write(os.path.join(ROOT, "work", p["slug"], "index.html"), render_project(p, nxt))
    write(os.path.join(ROOT, "404.html"), NOT_FOUND)
    write(os.path.join(ROOT, "assets", "js", "site.js"), JS)
    open(os.path.join(ROOT, "CNAME"), "w").write(SITE["domain"] + "\n")
    open(os.path.join(ROOT, ".nojekyll"), "w").close()
    open(os.path.join(ROOT, "robots.txt"), "w").write(
        f"User-agent: *\nAllow: /\nSitemap: https://{SITE['domain']}/sitemap.xml\n")
    urls = [f"https://{SITE['domain']}/"] + [
        f"https://{SITE['domain']}/work/{p['slug']}/" for p in PROJECTS]
    sm = "\n".join(f"  <url><loc>{u}</loc></url>" for u in urls)
    open(os.path.join(ROOT, "sitemap.xml"), "w").write(
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sm}\n</urlset>\n')
    print(f"built  index.html + {len(PROJECTS)} project pages + 404 + sitemap")

if __name__ == "__main__":
    main()
