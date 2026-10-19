#!/usr/bin/env python3
"""Build index.html from content/site.json and templates/page.html. Standard library only.

Text fields in site.json may contain inline HTML (<em>, <strong>, <a>, entities); they are inserted as-is.
"""
import datetime
import html
import json
import pathlib
import string
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FORBIDDEN = ["super-symbolic", "supersymbolic"]  # reserved name: never published


def a(url, label):
    return f'<a href="{html.escape(url, quote=True)}">{label}</a>'


def section(sid, heading, inner):
    return f'<section id="{sid}">\n<h2>{heading}</h2>\n{inner}\n</section>'


def build(site):
    out = []
    out.append(section("about", "Profile", "\n".join(f"<p>{p}</p>" for p in site["profile"])))

    items = []
    for op in site["open_problems"]:
        links = " · ".join(a(l["url"], l["label"]) for l in op["links"])
        items.append(
            f'<article class="problem" id="{op["id"]}">\n<h3>{op["title"]}</h3>\n<dl>\n'
            f'<dt>The problem</dt><dd>{op["problem"]}</dd>\n'
            f'<dt>Why it is hard</dt><dd>{op["why_hard"]}</dd>\n'
            f'<dt>What I am doing</dt><dd>{op["doing"]}</dd>\n</dl>\n'
            f'<p class="more">{links}</p>\n</article>'
        )
    out.append(section("open-problems", "Open problems I’m working on", "\n".join(items)))

    rec = []
    for r in site["recognition"]:
        text = a(r["url"], r["text"]) if r.get("url") else r["text"]
        year = f'<span class="year">{r["year"]}</span> — ' if r.get("year") else ""
        rec.append(f"<li>{year}{text}</li>")
    out.append(section("recognition", "Recognition and service", '<ul class="plain">\n' + "\n".join(rec) + "\n</ul>"))

    pubs = []
    for p in site["publications"]:
        badge = f'<span class="badge">{p["badge"]}</span>' if p.get("badge") else ""
        pubs.append(
            f'<li>{p["authors"]}. <a class="pub-title" href="{html.escape(p["url"], quote=True)}">{p["title"]}</a>. '
            f'{p["venue"]}, <span class="year">{p["year"]}</span>.{badge}</li>'
        )
    links = '<p class="linkrow">' + "".join(a(l["url"], l["label"]) for l in site["links"]) + "</p>"
    out.append(section("publications", "Selected publications",
                       f'<p class="note">{site["publications_note"]}</p>\n<ol class="pubs">\n'
                       + "\n".join(pubs) + "\n</ol>\n" + links))

    sw = [f'<li>{a(s["url"], "<strong>" + s["name"] + "</strong>")} — {s["text"]}</li>' for s in site["software"]]
    out.append(section("software", "Software", '<ul class="plain">\n' + "\n".join(sw) + "\n</ul>"))

    pr = []
    for p in site["projects"]:
        role = f' — <em>{p["role"]}</em>' if p.get("role") else ""
        pr.append(f'<li><strong>{p["name"]}</strong>, {p["funding"]}{role}</li>')
    out.append(section("projects", "Projects", '<ul class="plain">\n' + "\n".join(pr) + "\n</ul>"))

    ct = '<p class="linkrow">' + "".join(a(c["url"], c["label"]) for c in site["contacts"]) + "</p>"
    out.append(section("contact", "Contact", ct))
    return "\n\n".join(out)


def main():
    site = json.loads((ROOT / "content" / "site.json").read_text(encoding="utf-8"))
    aff = site["affiliation"]
    page = string.Template((ROOT / "templates" / "page.html").read_text(encoding="utf-8")).substitute(
        name=html.escape(site["name"]),
        title=html.escape(site["title"]),
        description=html.escape(site["description"], quote=True),
        affiliation=f'{a(aff["lab_url"], aff["lab"])}, {a(aff["institute_url"], aff["institute"])}',
        body=build(site),
        updated=datetime.date.today().strftime("%-d %B %Y"),
    )
    low = page.lower()
    bad = [w for w in FORBIDDEN if w in low]
    if bad:
        sys.exit(f"build refused: forbidden term(s) {bad} in output")
    (ROOT / "index.html").write_text(page, encoding="utf-8")
    print(f"index.html written ({len(page)} bytes)")


if __name__ == "__main__":
    main()
