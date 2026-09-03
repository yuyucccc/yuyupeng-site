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
<link rel="preload" href="{rel}assets/fonts/InstrumentSans-latin.woff2" as="font" type="font/woff2" crossorigin>
<script>document.documentElement.className+=" js"</script>
<link rel="stylesheet" href="{rel}assets/css/site.css">
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

# ── home ────────────────────────────────────────────────────────────────
def render_home():
    def cell(p):
        h = hero_of(p)
        if not h: return ""
        src = f"assets/img/{p['slug']}/{h['file']}"
        return f"""  <a class="item rise" href="work/{p['slug']}/">
   <figure><img src="{e(src)}" width="{h['w']}" height="{h['h']}" loading="lazy" decoding="async"
     alt="{e(p['title'])} — {e(p['place'])}"></figure>
   <div class="item__txt">
    <h3>{e(p['title'])}</h3>
    <p class="meta"><span>{e(p['place'])}</span><span>{e(p['years'])}</span></p>
   </div>
  </a>"""
    pro = [p for p in PROJECTS if p["group"] == "professional"]
    aca = [p for p in PROJECTS if p["group"] == "academic"]
    st = SITE["statement"]
    st_html = st.replace("bridge between people and nature", "<em>bridge between people and nature</em>", 1)

    return f"""{head(f"{SITE['name']} — {SITE['role']}, {SITE['location']}", SITE['meta_description'], "", f"https://{SITE['domain']}/")}
<main class="wrap">
{masthead("", "home")}

 <section class="panel panel--flush">
  <div class="grid hero-grid">
   <div class="hero">
    <h1>{st_html}</h1>
   </div>
   <div class="hero-aside">
    {mark("mark", 7, "Grass")}
    <p class="sub">Selected public space, playground and urban landscape projects for Gemeente Utrecht and Buro Sant en Co, and academic work from Delft and Shenzhen.</p>
   </div>
  </div>
 </section>

 <section class="panel panel--flush">
  <div class="rail"><p class="label">Professional work</p><p class="label">{len(pro):02d}</p></div>
  <div class="grid work">
{chr(10).join(cell(p) for p in pro)}
  </div>
 </section>

 <section class="panel panel--flush">
  <div class="rail"><p class="label">Academic work</p><p class="label">{len(aca):02d}</p></div>
  <div class="grid work">
{chr(10).join(cell(p) for p in aca)}
  </div>
 </section>
</main>
{footer("")}"""

# ── project page ────────────────────────────────────────────────────────
def render_project(p, nxt):
    ims  = imgs_for(p["slug"])
    hero = hero_of(p)
    rest = [i for i in ims if i is not hero]
    caps = p.get("captions", {})

    def plate(i, eager=False):
        key = i["file"].split(".")[0]
        cap = caps.get(key)
        figcap = f'<figcaption>{e(cap)}</figcaption>' if cap else ""
        # --nw carries the image's native pixel width so CSS can refuse to
        # upscale it. Most of these come out of a print PDF at ~1250 px; blown
        # to a 1365 px panel they go soft, and portraits grow past a screen.
        return f"""<figure class="plate rise panel panel--flush">
  <img src="../../assets/img/{p['slug']}/{i['file']}" width="{i['w']}" height="{i['h']}"
   style="--nw:{i['w']}px"
   {'fetchpriority="high"' if eager else 'loading="lazy"'} decoding="async"
   alt="{e(p['title'])} — {e(cap) if cap else 'project drawing'}">
  {figcap}
 </figure>"""

    facts = "\n".join(
        f'   <div class="row"><dt>{e(k)}</dt><dd>{e(v)}</dd></div>' for k, v in p["meta"])
    body = "\n".join(f"   <p>{e(t)}</p>" for t in p["body"])
    note = (f'<p class="note">{e(p["draft_note"])}</p>' if p.get("draft_note") else "")
    desc = p["lead"]

    return f"""{head(f"{p['title']} — {SITE['name']}", desc, "../../", f"https://{SITE['domain']}/work/{p['slug']}/")}
<main class="wrap">
{masthead("../../")}

 <article>
  <div class="panel panel--flush">
   <div class="head">
    <a class="back" href="../../">{ARROW_BACK}<span>All work</span></a>
    <h1>{e(p['title'])}</h1>
    <p class="where"><span>{e(p['place'])}</span><span>{e(p['years'])}</span></p>
    <p class="lead">{e(p['lead'])}</p>
   </div>
  </div>

{plate(hero, eager=True) if hero else ""}

  <div class="panel panel--flush">
   <div class="split">
    <div class="body">
{body}
{note}
    </div>
    <dl class="grid facts" style="margin:0">
{facts}
    </dl>
   </div>
  </div>

{chr(10).join(plate(i) for i in rest)}

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

# ── static extras ───────────────────────────────────────────────────────
JS = """document.querySelectorAll('.js-mail').forEach(function(a){
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
"""

NOT_FOUND = f"""{head(f"Not found — {SITE['name']}", "That page does not exist.", "", f"https://{SITE['domain']}/404.html")}
<main class="wrap">
{masthead("")}
 <section class="panel panel--flush">
  <div class="hero">
   {mark("mark", 5)}
   <h1>That page isn&rsquo;t here.</h1>
   <p class="sub">The link may be old, or the address mistyped.</p>
   <p style="margin-top:2rem"><a class="back" href="/">{ARROW_BACK}<span>All work</span></a></p>
  </div>
 </section>
</main>
{footer("")}"""

def write(path, s):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(s)

def main():
    write(os.path.join(ROOT, "index.html"), render_home())
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
