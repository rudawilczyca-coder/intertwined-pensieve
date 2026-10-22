#!/usr/bin/env python3
"""Build the Pensieve: fragments/*.md -> static HTML. No dependencies."""
import html, json, pathlib, re

ROOT = pathlib.Path(__file__).parent
SITE = "https://rudawilczyca-coder.github.io/intertwined-pensieve"
CREDIT = "Ruby &amp; Sable"


def parse(md):
    meta, body = {}, md
    if md.startswith("---"):
        head, body = md[3:].split("\n---", 1)
        for line in head.strip().splitlines():
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, body.strip()


def inline(text):
    t = html.escape(text, quote=False)
    return re.sub(r"\*(.+?)\*", r"<em>\1</em>", t)


def render_body(body):
    out = []
    for block in re.split(r"\n\s*\n", body):
        block = block.strip()
        if not block:
            continue
        if block == "⁂":
            out.append('<p class="break" aria-hidden="true">⁂</p>')
        else:
            out.append(f"<p>{inline(' '.join(block.splitlines()))}</p>")
    return "\n".join(out)


def page(title, description, url, image, content, depth=0):
    up = "../" * depth
    t, d = html.escape(title), html.escape(description)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t}</title>
<meta name="description" content="{d}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="The Intertwined Pensieve">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{t}">
<meta name="twitter:description" content="{d}">
<meta name="twitter:image" content="{image}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&family=EB+Garamond:ital@0;1&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{up}style.css">
</head>
<body>
{content}
<footer class="credit">The Intertwined Pensieve &middot; {CREDIT}</footer>
</body>
</html>
"""


def main():
    frags = []
    for md in sorted((ROOT / "fragments").glob("*.md")):
        meta, body = parse(md.read_text())
        slug = md.stem
        meta["slug"] = slug
        frags.append(meta)
        img = f"{SITE}/assets/{meta.get('image', slug + '.jpg')}"
        hero = f'<img class="hero" src="../assets/{meta.get("image", slug + ".jpg")}" alt="{html.escape(meta.get("alt", ""))}">'
        content = f"""<header class="masthead"><a href="../">The Intertwined Pensieve</a></header>
<article class="fragment">
{hero}
<h1>{html.escape(meta['title'])}</h1>
<p class="sub">{html.escape(meta.get('subtitle', ''))}</p>
<p class="byline">{CREDIT}</p>
{render_body(body)}
<p class="end" aria-hidden="true">~</p>
</article>"""
        (ROOT / "fragments" / f"{slug}.html").write_text(
            page(f"{meta['title']} · The Intertwined Pensieve", meta.get("subtitle", ""),
                 f"{SITE}/fragments/{slug}.html", img, content, depth=1))
    items = "\n".join(
        f'<li><a href="fragments/{f["slug"]}.html"><span class="t">{html.escape(f["title"])}</span>'
        f'<span class="s">{html.escape(f.get("subtitle", ""))}</span></a></li>' for f in frags)
    first = frags[0] if frags else {}
    content = f"""<header class="masthead home">
<h1>The Intertwined Pensieve</h1>
<p class="tag">Memories drawn out of the story, one silver thread at a time.</p>
</header>
<main class="index">
<h2>Fragments</h2>
<ul class="fragments">
{items}
</ul>
</main>"""
    (ROOT / "index.html").write_text(page(
        "The Intertwined Pensieve", "Fragments from Intertwined, a dark romantasy written by Ruby & Sable.",
        f"{SITE}/", f"{SITE}/assets/{first.get('image', first.get('slug', '') + '.jpg')}", content))
    (ROOT / ".nojekyll").write_text("")
    print("built", len(frags), "fragment(s)")


if __name__ == "__main__":
    main()
