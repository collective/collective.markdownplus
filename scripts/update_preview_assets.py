#!/usr/bin/env python3

import re
import urllib.request
from pathlib import Path


ASSETS = {
    "katex/katex.min.css": "https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css",
    "katex/katex.min.js": "https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js",
    "katex/auto-render.min.js": "https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js",
    "mermaid/mermaid.min.js": "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js",
}

ROOT = Path(__file__).resolve().parent.parent / "src/collective/markdownplus/browser/resources/vendor"


def download(url, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as response:
        target.write_bytes(response.read())


def katex_font_names(katex_css_path):
    css = katex_css_path.read_text()
    return sorted(set(re.findall(r'fonts/([^\\)"\']+\.woff2)', css)))


def main():
    for relative_path, url in ASSETS.items():
        download(url, ROOT / relative_path)

    katex_css_path = ROOT / "katex/katex.min.css"
    for font_name in katex_font_names(katex_css_path):
        download(
            f"https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/fonts/{font_name}",
            ROOT / "katex/fonts" / font_name,
        )


if __name__ == "__main__":
    main()