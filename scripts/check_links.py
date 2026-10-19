#!/usr/bin/env python3
"""Check every external link in index.html. Standard library only. Exit code 1 if any link is broken.

Sites that block automated clients (403/429/999 from DBLP, Scholar, LinkedIn, publishers) are reported
as WARN, not as failures: open those by hand if in doubt.
"""
import concurrent.futures
import html.parser
import pathlib
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
BLOCKING = {401, 403, 405, 418, 429, 999}


class Links(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        for k, v in attrs:
            if k == "href" and v and v.startswith(("http://", "https://")):
                self.urls.append(v)


def check(url):
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, method=method, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return "OK", r.status
        except urllib.error.HTTPError as e:
            if method == "HEAD":
                continue
            return ("WARN" if e.code in BLOCKING else "FAIL"), e.code
        except Exception as e:  # noqa: BLE001
            if method == "HEAD":
                continue
            return "FAIL", type(e).__name__
    return "FAIL", "?"


def main():
    p = Links()
    p.feed((ROOT / "index.html").read_text(encoding="utf-8"))
    urls = sorted(set(p.urls))
    with concurrent.futures.ThreadPoolExecutor(8) as ex:
        results = list(zip(urls, ex.map(check, urls)))
    fails = 0
    for url, (state, code) in results:
        print(f"{state:4} {code!s:>13}  {url}")
        fails += state == "FAIL"
    print(f"\n{len(urls)} links, {fails} broken")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
