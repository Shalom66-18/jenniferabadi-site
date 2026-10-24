"""Turn WordPress content into clean HTML for the static site."""
import re
from bs4 import BeautifulSoup, NavigableString
from common import img, esc

BLOCK = r"(?:table|thead|tfoot|caption|col|colgroup|tbody|tr|td|th|div|dl|dd|dt|ul|ol|li|pre|form|map|area|blockquote|address|math|style|p|h[1-6]|hr|fieldset|legend|section|article|aside|hgroup|header|footer|nav|figure|figcaption|details|menu|summary|iframe)"

def wpautop(t):
    """Port of WordPress's wpautop(): blank lines become paragraphs, single newlines become <br>."""
    if not t or not t.strip():
        return ""
    t = t.replace("\r\n", "\n").replace("\r", "\n") + "\n"
    pres = {}
    def keep(m):
        k = f"<pre-{len(pres)}>"; pres[k] = m.group(0); return k
    t = re.sub(r"<pre[\s\S]*?</pre>", keep, t)
    t = re.sub(r"<br\s*/?>\s*<br\s*/?>", "\n\n", t)
    t = re.sub(r"(<" + BLOCK + r"[\s/>])", r"\n\n\1", t)
    t = re.sub(r"(</" + BLOCK + r">)", r"\1\n\n", t)
    t = re.sub(r"\n\n+", "\n\n", t)
    out = ""
    for chunk in re.split(r"\n\s*\n", t):
        if chunk.strip():
            out += "<p>" + chunk.strip("\n") + "</p>\n"
    out = re.sub(r"<p>\s*</p>", "", out)
    out = re.sub(r"<p>\s*(</?" + BLOCK + r"[^>]*>)", r"\1", out)
    out = re.sub(r"(</?" + BLOCK + r"[^>]*>)\s*</p>", r"\1", out)
    out = re.sub(r"<p>([^<]+)</(div|address|form)>", r"<p>\1</p></\2>", out)
    out = re.sub(r"(?<!<br />)\s*\n(?!\s*</?" + BLOCK + ")", "<br />\n", out)
    out = re.sub(r"<br />(\s*</?(?:p|li|div|dl|dd|dt|th|pre|td|ul|ol)[^>]*>)", r"\1", out)
    out = re.sub(r"\n</p>$", "</p>", out)
    for k, v in pres.items():
        out = out.replace(k, v)
    return out

KEEP_ATTR = {"href", "src", "alt", "target", "rel", "colspan", "rowspan", "title", "width", "height"}
KEEP_STYLE = ("color", "text-align", "text-decoration")

LINKMAP = {}   # old site path (no slashes) -> new page path; filled by build.py
UNKNOWN = set()

def map_url(u):
    if not u:
        return u
    m = re.match(r"^https?://(?:www\.)?jenniferabadi\.com(/[^#?]*)?([?#].*)?$", u.strip())
    if not m:
        return u
    from urllib.parse import unquote
    path = unquote((m.group(1) or "/").strip("/"))
    if path.startswith("wp-content/uploads/"):
        return img(u.strip(), 1600)
    if path in LINKMAP:
        frag = m.group(2) or ""
        return LINKMAP[path] + (frag if frag.startswith("#") else "")
    UNKNOWN.add(path)
    return u

def clean(fragment, autop=False):
    """Clean an HTML fragment (string or Tag): strip builder junk, keep the content."""
    html = fragment if isinstance(fragment, str) else fragment.decode_contents()
    html = re.sub(r"\[/?[a-z_\-]+[^\]]*\]", "", html)          # leftover shortcodes
    if autop:
        html = wpautop(html)
    s = BeautifulSoup(html, "html.parser")
    for t in s(["script", "style", "noscript", "form", "input", "button"]):
        t.decompose()
    for t in s.find_all(True):
        st = t.get("style", "")
        keep_style = ";".join(p.strip() for p in st.split(";") if p.strip().split(":")[0].strip().lower() in KEEP_STYLE)
        cls = t.get("class", [])
        for a in list(t.attrs):
            if a not in KEEP_ATTR:
                del t[a]
        if keep_style:
            t["style"] = keep_style
        if t.name == "a" and any(re.search("btn|button", c) for c in cls):
            t["class"] = "btn"
        if t.name == "a" and t.get("href"):
            t["href"] = map_url(t["href"])
            if "eepurl.com" in t["href"] or "list-manage.com" in t["href"]:   # newsletter sign-up opens in a new tab
                t["target"] = "_blank"; t["rel"] = "noopener"
        if t.name == "img":
            src = t.get("data-src") or t.get("src") or ""
            t["src"] = map_url(src) if "jenniferabadi.com" in src else img(src) if src.startswith("wp-uploads") else src
            t["loading"] = "lazy"
            for a in ("width", "height"):
                if a in t.attrs: del t[a]
        if t.name == "iframe":
            pass
    for p in s.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6"]):
        if not p.get_text(strip=True) and not p.find(["img", "iframe"]) and (p.name != "p" or not p.find("br")):
            p.decompose()
    return str(s).strip()

def accordion_html(acc):
    """Easy Accordion plugin markup -> native <details> elements."""
    out = []
    for card in acc.select(".ea-card"):
        h = card.select_one(".ea-header")
        b = card.select_one(".ea-body") or card.select_one(".sp-collapse")
        if not h: continue
        out.append(f'<details class="acc"><summary>{esc(h.get_text(" ", strip=True))}</summary><div class="acc-body">{clean(b) if b else ""}</div></details>')
    return '<div class="accordion">' + "".join(out) + "</div>"

def text_column(col, contact_form_html=""):
    inner = col.select_one(".wpb_wrapper") or col
    for acc in inner.select(".sp-easy-accordion"):
        acc.replace_with(BeautifulSoup("<!--ACC-->" + accordion_html(acc) + "<!--/ACC-->", "html.parser"))
    for f in inner.select(".wpforms-container"):
        f.replace_with(BeautifulSoup("<!--FORM-->", "html.parser"))
    for g in inner.select(".pt-cv-wrapper"):
        g.decompose()
    raw = inner.decode_contents()
    # protect accordions from the cleaner (it would be fine, but keep summary/details intact)
    parts = re.split(r"(<!--ACC-->.*?<!--/ACC-->)", raw, flags=re.S)
    html = "".join(p[10:-11] if p.startswith("<!--ACC-->") else clean(p) for p in parts)
    html = html.replace("<!--FORM-->", contact_form_html)
    drop = " drop-cap" if "pls_drop_cap" in col.get("class", []) else ""
    return f'<div class="text{drop}">{html}</div>' if html.strip() else ""

def image_block(e, maxw=1400):
    i = e.find("img")
    if not i: return ""
    src = i.get("data-src") or i.get("src")
    align = "align-center"
    for a in ("left", "right"):
        if f"vc_align_{a}" in e.get("class", []): align = "align-" + a
    link = e.find("a")
    pic = f'<img src="{map_url(src) if "jenniferabadi" in src else src}" alt="{esc(i.get("alt",""))}" loading="lazy">'
    if link and link.get("href") and not link["href"].lower().endswith((".jpg", ".jpeg", ".png")):
        pic = f'<a href="{map_url(link["href"])}">{pic}</a>'
    return f'<figure class="{align}">{pic}</figure>'

def rows(raw_html, contact_form_html="", skip_first_heading=True):
    """Convert a WPBakery page into rows/columns of clean HTML. Returns (title, html)."""
    s = BeautifulSoup(raw_html, "html.parser")
    for t in s(["script", "style", "noscript"]): t.decompose()
    h1 = s.select_one("h1.header_font")
    title = h1.get_text(strip=True) if h1 else ""
    out = []
    for row in s.select(".vc_row"):
        if row.find_parent(class_="vc_row"):
            continue
        cols = [c for c in row.find_all(class_=re.compile(r"^vc_col-sm-\d+$")) if c.find_parent(class_=re.compile(r"^vc_col-sm-\d+$")) is None]
        if not cols: continue
        col_html = []
        for c in cols:
            w = int([x for x in c["class"] if x.startswith("vc_col-sm-")][0].split("-")[-1])
            items = []
            wrap = c.find(class_="wpb_wrapper")
            kids = wrap.find_all(recursive=False) if wrap else []
            for e in kids:
                cl = e.get("class", [])
                if "wpb_single_image" in cl: items.append(image_block(e))
                elif "wpb_text_column" in cl: items.append(text_column(e, contact_form_html))
                elif "theme_button" in cl or "vc_btn3-container" in cl:
                    a = e.find("a")
                    if a: items.append(f'<p class="btn-wrap"><a class="btn" href="{map_url(a.get("href",""))}"' + (' target="_blank" rel="noopener"' if a.get("target") == "_blank" or "eepurl.com" in a.get("href", "") else "") + f'>{esc(a.get_text(strip=True))}</a></p>')
                elif "prk_shortcode-title" in cl:
                    h = e.find(re.compile("^h[1-6]$"))
                    if h: items.append(f'<{h.name} class="block-title">{esc(h.get_text(" ", strip=True))}</{h.name}>')
                elif "vc_separator" in cl:
                    t = e.get_text(" ", strip=True)
                    items.append(f'<div class="separator"><span>{esc(t)}</span></div>' if t else '<hr class="separator">')
                elif "wpforms-container" in cl:
                    items.append(contact_form_html)
            col_html.append(f'<div class="col" style="--w:{w}">' + "\n".join(x for x in items if x) + "</div>")
        if any(len(BeautifulSoup(x, "html.parser").get_text(strip=True)) or "<img" in x or "<form" in x for x in col_html):
            out.append('<div class="row">' + "\n".join(col_html) + "</div>")
    return title, "\n".join(out)
