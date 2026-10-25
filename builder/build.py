"""Build Jennifer Abadi's website into site/.   Run:  python3 builder/build.py

Where things live:
  content/upcoming.json   upcoming classes & events (homepage + Upcoming Events page)
  content/posts.json      recipes and articles
  content/classes.json    cooking class catalog
  raw/*.html              captured WordPress pages used for About, Cookbooks, Gift Certificates, Contact, Catalog intro
"""
import json, os, re, html as H
from bs4 import BeautifulSoup
from common import ROOT, SITE, img, page, write, esc, MAILCHIMP, remove_stale_pages
import wphtml
from wphtml import clean, rows, LINKMAP

def load(name, default=None):
    p = os.path.join(ROOT, "content", name)
    return json.load(open(p)) if os.path.exists(p) else default

def raw(name):
    return open(os.path.join(ROOT, "raw", name)).read()

from urllib.parse import unquote
POSTS = load("posts.json")
CLASSES = load("classes.json")
for _p in POSTS + CLASSES: _p["slug"] = unquote(_p["slug"])
EVENTS = load("upcoming.json", [])
PAGES = {p["slug"]: p for p in load("pages.json")}

def is_recipe(p): return any("Recipes" in c for c in p["categories"])
def is_article(p): return "Articles" in p["categories"]
RECIPES = [p for p in POSTS if is_recipe(p)]
ARTICLES = [p for p in POSTS if is_article(p)]

# ---------------------------------------------------------------- address map (old WordPress URL -> new file)
for slug in ["about", "recipe-abadi", "articles-2022", "upcoming-events", "cooking-class-catalog",
             "cookbooks", "gift-certificates-2023", "contact-jennifer", "privacy-policy"]:
    LINKMAP[slug] = f"{slug}/index.html"
LINKMAP[""] = "index.html"
LINKMAP["book-a-class"] = "contact-jennifer/index.html"
LINKMAP["recipes"] = "recipe-abadi/index.html"
LINKMAP["articles"] = "articles-2022/index.html"
for p in POSTS: LINKMAP[p["slug"]] = f'{p["slug"]}/index.html'
for c in CLASSES: LINKMAP["classes/" + c["slug"]] = f'classes/{c["slug"]}/index.html'

def text_of(html, n=None):
    t = re.sub(r"\s+", " ", BeautifulSoup(html or "", "html.parser").get_text(" ")).strip()
    t = t.replace("©Jennifer Felicia Abadi: www.JenniferAbadi.com", "").strip()
    if n and len(t) > n:
        t = t[:n].rsplit(" ", 1)[0] + "…"
    return t

# ---------------------------------------------------------------- shared bits
def events_block():
    if not EVENTS:
        return '<div class="notice">Currently, there are no events planned. Please check back later.</div>'
    li = []
    for e in EVENTS:
        pic = f'<img src="{img(e["image"], 800)}" alt="" loading="lazy">' if e.get("image") else ""
        reg = f'<p><a class="btn" href="{esc(e["link"])}" target="_blank" rel="noopener">{esc(e.get("link_text","Register"))}</a></p>' if e.get("link") else ""
        li.append(f'<li><div class="when">{esc(e["date"])}<br><span>{esc(e.get("time",""))}</span>{pic}</div>'
                  f'<div><h3>{esc(e["title"])}</h3><p class="where">{esc(e.get("where",""))}</p>{e.get("description","")}{reg}</div></li>')
    return '<ul class="event-list">' + "".join(li) + "</ul>"

CONTACT_FORM = """<form class="contact-form" action="https://api.web3forms.com/submit" method="POST" data-mailchimp="https://jenniferabadi.us14.list-manage.com/subscribe/post-json?u=ca9eade73500555c66cf1747c&amp;id=fe18af136f">
  <input type="hidden" name="access_key" value="36dc9de6-905f-44fd-a47b-32d00b1d00e7">
  <input type="hidden" name="subject" value="New message from jenniferabadi.com">
  <input type="checkbox" name="botcheck" class="hp" tabindex="-1" autocomplete="off">
  <fieldset><legend>Name <span class="req">*</span></legend>
    <div class="two"><label><input type="text" name="first_name" required><small>First</small></label>
    <label><input type="text" name="last_name" required><small>Last</small></label></div></fieldset>
  <label class="field">Email <span class="req">*</span><input type="email" name="email" required></label>
  <fieldset><legend>Your Interests <span class="req">*</span></legend>
    <label class="check"><input type="checkbox" name="interests[]" value="Cooking Class/Demonstration"> Cooking Class/Demonstration</label>
    <label class="check"><input type="checkbox" name="interests[]" value="Speaking Engagement"> Speaking Engagement</label>
    <label class="check"><input type="checkbox" name="interests[]" value="Recipe Writing/Development/Testing"> Recipe Writing/Development/Testing</label>
    <label class="check"><input type="checkbox" name="interests[]" value="Order Signed Cookbook"> Order Signed Cookbook</label>
    <label class="check"><input type="checkbox" name="interests[]" value="Order Gift Certificate"> Order Gift Certificate</label>
    <label class="check"><input type="checkbox" name="interests[]" value="Other"> Other</label></fieldset>
  <label class="field">Comment or Message<textarea name="message" rows="6"></textarea></label>
  <fieldset><legend>Newsletter</legend>
    <label class="check"><input type="checkbox" name="newsletter" value="Yes" checked> Sign-up to receive my events calendar newsletter?</label></fieldset>
  <button type="submit" class="send">SEND</button>
  <p class="form-status" hidden></p>
</form>"""

def wp_page(slug, raw_file, active, depth=1, extra_class=""):
    title, body = rows(raw(raw_file), CONTACT_FORM)
    title = title or PAGES.get(slug, {}).get("title", "")
    html = f'<h1 class="page-title">{esc(title)}</h1>\n<div class="wrap rows {extra_class}">\n{body}\n</div>'
    write(f"{slug}/index.html", page(title.title(), html, active=active, depth=depth, body_class="page-" + slug))

# ---------------------------------------------------------------- HOME
def build_home():
    portfolio = json.load(open(os.path.join(ROOT, "raw", "portfolio_data.json")))
    slides = {p["hero_image"].split("/")[-1]: p["slug"] for p in POSTS if p.get("hero_image")}
    hero = img("wp-uploads/2021/06/Jennifer_Chef_Kitchen_Writiing_COLOR_72dpi_1-scaled.jpg", 2000)
    services = [("VIRTUAL CLASSES", "wp-uploads/2022/11/HomePage_VirtualClass_SQUARE_COMPRESSED.png"),
                ("IN-PERSON CLASSES", "wp-uploads/2022/11/HomePage_KidsClass_Square_COMPRESSED.png"),
                ("TEAM BUILDING CLASSES", "wp-uploads/2022/11/HomePage_TeamBuildingClass_SQUARE_COMPRESSED.png")]
    quotes = [
        ("Hiring Jennifer to come over for a one-on-one private bread-baking lesson was the best decision I had made all year! After just one session I learned enough techniques to create fabulous challahs and whole wheat breads all on my own.", "Claire Sauerhoff"),
        ("Jennifer graciously spent hours adapting an old family bourekas recipe for us so that we could come together around the globe for a virtual lesson. With patience and skill Jennifer taught us step by step how to master this beloved pastry over Zoom—through multiple time zones!", "Vicki Alvy"),
        ("Jennifer led a series of cooking demonstrations for our virtual Middle East and North Africa programs. From Moroccan mufletta and Tunisian couscous, to Kurdish biryani, she shared her extensive knowledge of the history and culture of Jews from MENA countries, bringing regional context to each recipe in a fun, hands-on experience.", "Sapir Taib, JIMENA.org (Jews Indigenous to the Middle East and North Africa)"),
    ]
    svc = "".join(f'<a href="cooking-class-catalog/index.html"><img src="{img(p, 800)}" alt="{t.title()}" loading="lazy"><h4>{t}</h4></a>' for t, p in services)
    cards = ""
    for p in portfolio:
        slug = slides.get(p["img"].split("/")[-1])
        inner = f'<h3>{esc(p["title"])}</h3><img src="{img(p["img"], 900)}" alt="{esc(p["title"])}" loading="lazy">'
        cards += f'<a class="card" href="{slug}/index.html">{inner}</a>' if slug else f'<div class="card">{inner}</div>'
    qs = "".join(f'<blockquote>“{esc(q)}”<cite>—{esc(a)}</cite></blockquote>' for q, a in quotes)
    body = f"""
<section class="hero" style="background-image:url('{hero}')">
  <div class="inner">
    <h2 class="name">JENNIFER ABADI</h2>
    <div class="bar"></div>
    <h1>Sephardic &amp; Judeo-Arabic<br>Recipe Preserver<br>Cookbook Author<br>Culinary Instructor</h1>
  </div>
</section>
<section class="intro reveal">
  <h2>Learn the secrets &amp; traditions of Middle Eastern,<br>Mediterranean, and Central Asian cuisine—<br>one recipe at a time, in your very own kitchen!</h2>
  <h3 dir="rtl" lang="ar">الي بيدري بيدري<br>و الي ما بيدري<br>بيقول كف عدس</h3>
  <h3 class="en">He who knows, knows.<br>And he who does not know says:<br>(It is just) a fistful of lentils.<br>— Arabic Proverb</h3>
</section>
<section class="services reveal">
  <h2 class="section-title">COOKING CLASSES &amp; SERVICES</h2>
  <div class="grid">{svc}</div>
</section>
<section class="band">
  <h2 class="section-title">PORTFOLIO</h2>
  <div class="carousel">
    <div class="track">{cards}</div>
    <div class="arrows"><button class="prev" aria-label="Previous">&#8249;</button><button class="next" aria-label="Next">&#8250;</button></div>
  </div>
  <div class="testimonials reveal">{qs}</div>
</section>
<section class="events reveal" id="events">
  <h2 class="section-title">UPCOMING CLASSES &amp; EVENTS</h2>
  <a class="btn" href="{MAILCHIMP}" target="_blank" rel="noopener">Receive Events Newsletter!</a>
  {events_block()}
</section>"""
    write("index.html", page("", body, description="Learn Sephardic, Judeo-Arabic, Middle Eastern, Mediterranean and Central Asian cooking with cookbook author and culinary instructor Jennifer Abadi."))

# ---------------------------------------------------------------- simple pages
def build_about():
    title, html = rows(raw("about.html"))
    body = f'<h1 class="page-title">{esc(title)}</h1>\n<article class="content">\n{html}\n<div class="clear"></div>\n</article>'
    write("about/index.html", page("About", body, active="ABOUT", depth=1, body_class="page-about",
          description="About Jennifer Abadi, Sephardic and Judeo-Arabic recipe preserver, cookbook author and culinary instructor."))

def build_events_page():
    body = f"""<h1 class="page-title">UPCOMING EVENTS</h1>
<section class="events events-page">
  <a class="btn" href="{MAILCHIMP}" target="_blank" rel="noopener">Receive Events Newsletter!</a>
  {events_block()}
</section>"""
    write("upcoming-events/index.html", page("Upcoming Events", body, active="UPCOMING EVENTS", depth=1))

def build_privacy():
    p = PAGES["privacy-policy"]
    body = f'<h1 class="page-title">Privacy Policy</h1>\n<article class="content">{clean(p["content_html"], autop=True)}</article>'
    write("privacy-policy/index.html", page("Privacy Policy", body, depth=1))

# ---------------------------------------------------------------- recipes & articles
def card(p, excerpt=False):
    pic = f'<img src="{img(p["hero_image"], 700)}" alt="" loading="lazy">' if p.get("hero_image") else ""
    ex = f'<p>{esc(text_of(p.get("excerpt") or p["content_html"], 190))}</p>' if excerpt else ""
    cats = "|".join(p["categories"])
    return (f'<a class="post-card" href="{p["slug"]}/index.html" data-cats="{esc(cats)}" data-text="{esc((p["title"]+" "+text_of(p["content_html"])).lower())}">'
            f'<h3>{esc(p["title"])}</h3>{pic}{ex}</a>')

def sidebar(title, items):
    links = "".join(f'<li><a href="{p["slug"]}/index.html">{esc(p["title"])}</a></li>' for p in items)
    return f'<aside class="sidebar"><h3>{title}</h3><ul>{links}</ul></aside>'

def build_recipes():
    cats = {}
    for p in RECIPES:
        for c in p["categories"]:
            if c != "All Recipes" and "Recipes" in c: cats[c] = cats.get(c, 0) + 1
    opts = "".join(f'<option value="{esc(c)}">{esc(c)} ({n})</option>' for c, n in sorted(cats.items()))
    grid = "".join(card(p) for p in RECIPES)
    body = f"""<h1 class="page-title">RECIPES</h1>
<div class="wrap with-sidebar">
  <div class="main">
    <div class="filters"><select data-filter="cats"><option value="">View Recipes by Holiday and Type</option>{opts}</select></div>
    <div class="post-grid" data-paged="18">{grid}</div>
    <nav class="pager"></nav>
  </div>
  {sidebar("ARTICLES", ARTICLES)}
</div>"""
    write("recipe-abadi/index.html", page("Recipes", body, active="RECIPES", depth=1, body_class="page-recipes"))

def build_articles():
    grid = "".join(card(p, excerpt=True) for p in ARTICLES)
    body = f"""<h1 class="page-title">ARTICLES</h1>
<div class="wrap with-sidebar">
  <div class="main">
    <form class="filters search" onsubmit="return false"><label>Search by keyword <input type="search" data-filter="text"></label>
      <button type="submit" class="btn-green">Submit</button><button type="reset" class="btn-orange">Reset</button></form>
    <div class="post-grid with-excerpt" data-paged="18">{grid}</div>
    <nav class="pager"></nav>
  </div>
  {sidebar("RECIPES LIST", RECIPES)}
</div>"""
    write("articles-2022/index.html", page("Articles", body, active="RECIPES", depth=1, body_class="page-articles"))

def share(title):
    t = H.escape(title)
    return f'''<div class="share">
<a href="https://www.instagram.com/jenniferabadi/" target="_blank" rel="noopener" aria-label="Instagram" class="s-ig"><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5" fill="none" stroke="#fff" stroke-width="2"/><circle cx="12" cy="12" r="4.2" fill="none" stroke="#fff" stroke-width="2"/><circle cx="17.3" cy="6.7" r="1.3" fill="#fff"/></svg></a>
<a class="s-fb js-share" data-net="fb" href="#" aria-label="Share on Facebook">Facebook</a>
<a class="s-li js-share" data-net="li" href="#" aria-label="Share on LinkedIn">LinkedIn</a>
<a class="s-em js-share" data-net="em" href="#" aria-label="Share by email" data-title="{t}">Email</a>
<a class="s-pr" href="javascript:print()" aria-label="Print">Print</a></div>'''

def drop_image(html, image_path):
    """Remove the first occurrence of an image from post HTML (it is shown under the title instead)."""
    stem = re.sub(r"(-scaled)?(-\d+x\d+)?\.\w+$", "", image_path.split("/")[-1])
    soup = BeautifulSoup(html, "html.parser")
    for i in soup.find_all("img"):
        if stem and stem in i.get("src", ""):
            node = i
            while node.parent is not None and node.parent.name in ("a", "figure", "p", "div") and \
                    len(node.parent.get_text(strip=True)) == 0 and len(node.parent.find_all("img")) == 1:
                node = node.parent
            node.decompose()
            break
    return str(soup)

def build_posts():
    for p in POSTS:
        content = clean(p["content_html"], autop=True)
        hero = ""
        if p.get("hero_image"):                                     # same picture as the thumbnail, under the title
            hero = f'<figure class="post-hero"><img src="{img(p["hero_image"], 1400)}" alt="{esc(p["title"])}"></figure>'
            content = drop_image(content, p["hero_image"])
        tags = [t for t in p.get("tags", []) if t.lower() != "home page slides"]
        tag_html = ('<div class="tags"><span>Tags</span>' + "".join(f"<em>{esc(t)}</em>" for t in tags) + "</div>") if tags else ""
        body = f"""<article class="post">
<h1 class="post-title">{esc(p["title"])}</h1>
{hero}
<div class="post-body">{content}</div>
{tag_html}
</article>"""
        write(f'{p["slug"]}/index.html', page(p["title"], body, active="RECIPES" if (is_recipe(p) or is_article(p)) else "",
              depth=1, description=text_of(p.get("excerpt") or p["content_html"], 155)))

# ---------------------------------------------------------------- class catalog
# Only classes with one of these formats appear in the Cooking Class Catalog.
# Past events (e.g. format "Private Events" or "JCC 20s + 30s") keep their own page but are not listed.
CATALOG_FORMATS = [
    "1-DISH VIRTUAL PRIVATE COOKING LESSON",
    "2-DISH/LONGER DISH VIRTUAL PRIVATE COOKING LESSON",
    "IN-PERSON PRIVATE 3-HOUR FULL MENU COOKING CLASS",
    "KIDS COOKING CLASSES",
    "TEENS AND TWEENS COOKING CLASSES",
    "VIRTUAL CHEF TALK & LESSON PROGRAM",
]
def catalog_format(f):
    return any(f.upper().startswith(x) for x in CATALOG_FORMATS)

def build_catalog():
    title, intro = rows(raw("cooking-class-catalog.html"))
    # the captured page has the intro/FAQ in the left column; keep only that column
    s = BeautifulSoup(intro, "html.parser")
    cols = s.select(".row .col")
    left = cols[0].decode_contents() if cols else ""
    topics, formats = {}, {}
    # "past_event": true files a class/event away: it keeps its page (old links still work)
    # but is not listed in the catalog. Remove the flag to bring it back.
    listed = [c for c in CLASSES if not c.get("past_event") and any(catalog_format(f) for f in c["formats"])]
    for c in listed:
        for t in c["topics"]: topics[t] = topics.get(t, 0) + 1
        for f in c["formats"]:
            if catalog_format(f): formats[f] = formats.get(f, 0) + 1
    t_opts = "".join(f'<option value="{esc(t)}">{esc(t)} ({n})</option>' for t, n in sorted(topics.items(), key=lambda x: x[0].lower()))
    f_opts = "".join(f'<option value="{esc(f)}">{esc(f)} ({n})</option>' for f, n in sorted(formats.items()))
    cards = ""
    for c in listed:
        pic = f'<img src="{img(c["hero_image"], 700)}" alt="" loading="lazy">' if c.get("hero_image") else ""
        cards += (f'<a class="post-card class-card" href="classes/{c["slug"]}/index.html" data-topics="{esc("|".join(c["topics"]))}" data-formats="{esc("|".join(c["formats"]))}">'
                  f'<h3>{esc(c["title"])}</h3>{pic}<p class="fmt">{esc(", ".join(c["formats"]))}</p></a>')
    body = f"""<div class="wrap catalog">
  <aside class="catalog-intro">{left}</aside>
  <div class="main">
    <div class="filters two">
      <label>Filter Classes by Cuisine, Food Type, Holiday<select data-filter="topics"><option value="">All</option>{t_opts}</select></label>
      <label>Filter Classes by Format<select data-filter="formats"><option value="">All Classes</option>{f_opts}</select></label>
    </div>
    <div class="post-grid" data-paged="25">{cards}</div>
    <nav class="pager"></nav>
  </div>
</div>"""
    print("catalog:", len(listed), "listed,", len(CLASSES) - len(listed), "hidden:", [c["title"] for c in CLASSES if c not in listed])
    write("cooking-class-catalog/index.html", page("Cooking Class Catalog", body, active="COOKING CLASS CATALOG", depth=1, body_class="page-catalog"))

def build_past_events():
    """Private archive of filed past events. Not in the menu, not linked, hidden from search engines.
    Address: /past-events/ (only people who know it can open it)."""
    past = [c for c in CLASSES if c.get("past_event")]
    cards = ""
    for c in past:
        pic = f'<img src="{img(c["hero_image"], 700)}" alt="" loading="lazy">' if c.get("hero_image") else ""
        cards += (f'<a class="post-card class-card" href="classes/{c["slug"]}/index.html">'
                  f'<h3>{esc(c["title"])}</h3>{pic}<p class="fmt">{esc(", ".join(c["formats"]))}</p></a>')
    body = f"""<h1 class="page-title">PAST EVENTS</h1>
<div class="wrap">
  <p class="archive-note">Private archive — this page is not in the menu and not shown on Google.
  {len(past)} filed events. Click one to see its full page.</p>
  <div class="post-grid">{cards}</div>
</div>"""
    write("past-events/index.html", page("Past Events", body, depth=1, hidden=True))

def build_404():
    """Shown for any address that doesn't exist (e.g. old WordPress-only links). Uses root-relative links."""
    body = """<h1 class="page-title">PAGE NOT FOUND</h1>
<div class="wrap" style="text-align:center">
  <p>Sorry, this page has moved or no longer exists.</p>
  <p class="btn-wrap"><a class="btn" href="index.html">Go to the home page</a></p>
  <p><a href="recipe-abadi/index.html">Recipes</a> &nbsp;·&nbsp; <a href="cooking-class-catalog/index.html">Cooking Class Catalog</a> &nbsp;·&nbsp; <a href="contact-jennifer/index.html">Contact</a></p>
</div>"""
    html = page("Page Not Found", body, hidden=True).replace('<meta charset="UTF-8">', '<meta charset="UTF-8">\n<base href="/">', 1)
    write("404.html", html)

def build_classes():
    for c in CLASSES:
        pic = f'<img src="{img(c["hero_image"], 1400)}" alt="{esc(c["title"])}">' if c.get("hero_image") else ""
        from urllib.parse import quote
        msg = "contact-jennifer/index.html?class=" + quote(c["title"], safe="")
        body = f"""<article class="wrap class-page">
  <div class="class-top">
    <div class="class-img">{pic}{share(c["title"])}</div>
    <div class="class-meta">
      <h1>{esc(c["title"])}</h1>
      <p class="meta"><b>Cuisine &amp; Diet:</b> {esc(", ".join(c["topics"]))}</p>
      <p class="meta"><b>Class Format:</b> {esc(", ".join(c["formats"]))}</p>
      <a class="btn" href="{msg}">Message Me About this Class</a>
    </div>
  </div>
  <div class="class-body">{clean(c["content_html"], autop=True)}</div>
</article>"""
        write(f'classes/{c["slug"]}/index.html', page(c["title"], body, active="COOKING CLASS CATALOG", depth=2, hidden=bool(c.get("past_event")),
              description=text_of(c["content_html"], 155)))

if __name__ == "__main__":
    build_home(); build_about(); build_events_page(); build_privacy()
    wp_page("cookbooks", "cookbooks.html", "COOKBOOKS", extra_class="cookbooks")
    wp_page("gift-certificates-2023", "gift-certificates-2023.html", "GIFT CERTIFICATES", extra_class="gifts")
    wp_page("contact-jennifer", "contact-jennifer.html", "CONTACT", extra_class="contact")
    build_recipes(); build_articles(); build_posts()
    build_catalog(); build_classes(); build_past_events(); build_404()
    gone = remove_stale_pages()
    if gone: print("removed old pages:", gone)
    print("pages built. unknown internal links:", sorted(wphtml.UNKNOWN)[:40], len(wphtml.UNKNOWN))
