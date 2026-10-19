# vincenzoml.github.io

Personal academic homepage, served by GitHub Pages from `index.html` on `master` (no Jekyll: see `.nojekyll`).

How to update:

1. Edit the content in `content/site.json` (profile, open problems, recognition, publications, software, projects, contacts). Text fields may contain inline HTML.
2. Change the look only in `templates/page.html` (CSS, layout; placeholders are `$name`, `$body`, `$updated`, ...).
3. Rebuild: `python3 scripts/build.py` regenerates `index.html` and writes the "Last updated" date. Never edit `index.html` by hand.
4. Check links: `python3 scripts/check_links.py` must report 0 broken (WARN = site blocks bots; check by hand).
5. Preview: `python3 -m http.server 8000`, then open http://localhost:8000.
6. Commit `content/`, `templates/` and the regenerated `index.html` together, then push to `master`.

Python 3 standard library only; no dependencies.
