"""Shared pieces for building Jennifer Abadi's site: paths, images, header/footer."""
import os, re, shutil, html as H
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "docs")   # published folder (GitHub Pages serves /docs)
IMG_OUT = os.path.join(SITE, "images")

# Page addresses keep the old WordPress URLs (e.g. /about/), so existing links keep working.
NAV = [
    ("ABOUT", "about/index.html"),
    ("RECIPES", "recipe-abadi/index.html", [("RECIPES", "recipe-abadi/index.html"), ("ARTICLES", "articles-2022/index.html")]),
    ("UPCOMING EVENTS", "upcoming-events/index.html"),
    ("COOKING CLASS CATALOG", "cooking-class-catalog/index.html"),
    ("COOKBOOKS", "cookbooks/index.html"),
    ("GIFT CERTIFICATES", "gift-certificates-2023/index.html"),
    ("CONTACT", "contact-jennifer/index.html"),
]
SOCIAL = [
    ("Instagram", "https://www.instagram.com/jenniferabadi/", "#e1306c",
     '<path d="M12 2.2c3.2 0 3.6 0 4.8.1 3.2.1 4.8 1.7 4.9 4.9.1 1.3.1 1.6.1 4.8s0 3.6-.1 4.8c-.1 3.2-1.7 4.8-4.9 4.9-1.3.1-1.6.1-4.8.1s-3.6 0-4.8-.1c-3.3-.1-4.8-1.7-4.9-4.9C2.2 15.6 2.2 15.2 2.2 12s0-3.6.1-4.8C2.4 4 3.9 2.4 7.2 2.3 8.4 2.2 8.8 2.2 12 2.2zM12 0C8.7 0 8.3 0 7.1.1 2.7.3.3 2.7.1 7.1 0 8.3 0 8.7 0 12s0 3.7.1 4.9c.2 4.4 2.6 6.8 7 7 1.2.1 1.6.1 4.9.1s3.7 0 4.9-.1c4.4-.2 6.8-2.6 7-7 .1-1.2.1-1.6.1-4.9s0-3.7-.1-4.9c-.2-4.4-2.6-6.8-7-7C15.7 0 15.3 0 12 0zm0 5.8a6.2 6.2 0 100 12.4 6.2 6.2 0 000-12.4zM12 16a4 4 0 110-8 4 4 0 010 8zm6.4-11.8a1.4 1.4 0 100 2.9 1.4 1.4 0 000-2.9z"/>'),
    ("Facebook", "https://www.facebook.com/jennifer.abadi.9/", "#3b5998",
     '<path d="M24 12a12 12 0 10-13.9 11.9v-8.4h-3V12h3V9.4c0-3 1.8-4.7 4.5-4.7 1.3 0 2.7.2 2.7.2v3h-1.5c-1.5 0-2 .9-2 1.9V12h3.4l-.5 3.5h-2.9v8.4A12 12 0 0024 12z"/>'),
    ("LinkedIn", "https://www.linkedin.com/in/jenniferabadi/", "#141414",
     '<path d="M20.4 20.5h-3.6v-5.6c0-1.3 0-3-1.8-3s-2.1 1.4-2.1 2.9v5.7H9.4V9h3.4v1.6c.5-.9 1.6-1.8 3.4-1.8 3.6 0 4.3 2.4 4.3 5.5v6.2zM5.3 7.4a2.1 2.1 0 110-4.1 2.1 2.1 0 010 4.1zM7.1 20.5H3.6V9h3.5v11.5zM22.2 0H1.8C.8 0 0 .8 0 1.7v20.6c0 .9.8 1.7 1.8 1.7h20.4c1 0 1.8-.8 1.8-1.7V1.7C24 .8 23.2 0 22.2 0z"/>'),
]
MAILCHIMP = "http://eepurl.com/cyZruf"

def esc(s): return H.escape(s or "", quote=True)

def _find_source(ref):
    """ref is a URL on jenniferabadi.com or a wp-uploads/... path. Return a local file path."""
    rel = ref.split("wp-content/uploads/", 1)[-1] if "wp-content/uploads/" in ref else ref.replace("wp-uploads/", "", 1)
    base = os.path.basename(rel)
    cands = [os.path.join(ROOT, "wp-uploads", rel), os.path.join(ROOT, "assets", "images", base)]
    stem, ext = os.path.splitext(rel)
    plain = re.sub(r"-\d+x\d+$", "", stem)
    for s in (plain + ext, plain.replace("-scaled", "") + ext, plain + "-scaled" + ext):
        cands.append(os.path.join(ROOT, "wp-uploads", s))
    # The original WordPress files are not in this repository; fall back to the
    # copies already published in docs/images (same file names).
    cands += [os.path.join(IMG_OUT, os.path.basename(c)) for c in list(cands)]
    for c in cands:
        if os.path.exists(c):
            return c
    return None

def img(ref, maxw=1600):
    """Copy (and shrink if needed) an image into site/images; return its web path."""
    if not ref:
        return ""
    src = _find_source(ref)
    if not src:
        print("  !! missing image:", ref)
        return ref
    name = os.path.basename(src)
    dst = os.path.join(IMG_OUT, name)
    if os.path.abspath(src) != os.path.abspath(dst) and not os.path.exists(dst):
        try:
            im = Image.open(src)
            if im.width > maxw and src.lower().endswith((".jpg", ".jpeg", ".png")):
                im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
                if name.lower().endswith((".jpg", ".jpeg")):
                    im.convert("RGB").save(dst, quality=85, optimize=True, progressive=True)
                else:
                    im.save(dst, optimize=True)
            else:
                shutil.copy2(src, dst)
        except Exception:
            shutil.copy2(src, dst)
    return "images/" + name

def header(active):
    items = []
    for entry in NAV:
        label, href = entry[0], entry[1]
        sub = entry[2] if len(entry) > 2 else None
        cls = ' class="current"' if label == active else ""
        if sub:
            subs = "".join(f'<li><a href="{h}">{l}</a></li>' for l, h in sub)
            items.append(f'<li class="has-sub"><a href="{href}"{cls}>{label}</a><ul class="sub">{subs}</ul></li>')
        else:
            items.append(f'<li><a href="{href}"{cls}>{label}</a></li>')
    social = "".join(
        f'<a href="{u}" target="_blank" rel="noopener" aria-label="{n}"><svg viewBox="0 0 24 24" fill="{c}">{p}</svg></a>'
        for n, u, c, p in SOCIAL)
    return f"""<header class="site-header">
  <a class="logo" href="index.html"><img src="{img('wp-uploads/2022/02/Logo_Name_JenniferAbadi.png')}" alt="Jennifer Abadi" width="546" height="68"></a>
  <div class="social">{social}</div>
  <button class="menu-toggle" aria-label="Menu"><span></span><span></span><span></span></button>
  <nav class="main-nav"><ul>{''.join(items)}</ul></nav>
</header>"""

def _ver(path):
    """Short fingerprint of a file, added to its link so browsers fetch the new version after a change."""
    import hashlib
    try:
        return hashlib.md5(open(os.path.join(SITE, path), "rb").read()).hexdigest()[:8]
    except OSError:
        return "1"

def page(title, body, active="", description="", body_class="", depth=0, hidden=False):
    """depth = how many folders deep the page sits (0 for index.html, 1 for about/index.html)."""
    t = "Jennifer Abadi" if not title else f"{title} – Jennifer Abadi"
    base = f'<base href="{"../" * depth}">\n' if depth else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
{base}<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(t)}</title>
<meta name="description" content="{esc(description)}">{chr(10) + '<meta name="robots" content="noindex, nofollow">' if hidden else ""}
<link rel="icon" href="{img('wp-uploads/2022/11/cropped-JenniferAbadi_COMPRESSED.png') if _find_source('wp-uploads/2022/11/cropped-JenniferAbadi_COMPRESSED.png') else img('assets/images/cropped-JenniferAbadi_COMPRESSED-300x300.png')}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css?family=Economica:400,700,400italic,700italic%7CLato:300,400,400italic,700%7COpen+Sans+Condensed:300,700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="css/style.css?v={_ver('css/style.css')}">
</head>
<body class="{body_class}">
{header(active)}
<main>
{body}
</main>
<footer class="site-footer"><p>Jennifer Abadi© <span class="year">2026</span> All rights reserved</p></footer>
<a href="#" class="to-top" aria-label="Back to top">&#8963;</a>
<script src="js/site.js?v={_ver('js/site.js')}"></script>
</body>
</html>
"""

WRITTEN = set()

def write(name, content):
    path = os.path.join(SITE, name)
    WRITTEN.add(os.path.normpath(path))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    pass

def remove_stale_pages():
    """Delete generated pages that no longer exist in the content (e.g. a deleted recipe)."""
    removed = []
    for dirpath, dirs, files in os.walk(SITE):
        if "index.html" in files and dirpath != SITE:
            p = os.path.normpath(os.path.join(dirpath, "index.html"))
            if p not in WRITTEN:
                os.remove(p)
                removed.append(os.path.relpath(dirpath, SITE))
                if not os.listdir(dirpath):
                    os.rmdir(dirpath)
    return removed
