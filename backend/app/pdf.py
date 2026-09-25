"""Headless-Chromium PDF rendering.

The browser's own print dialog injects a header (page title + date) and footer
(URL + `Page N of M`) that CSS cannot remove. We render the paper's HTML through
headless Chromium instead, with `display_header_footer` under our control: an
empty header, and a footer that is a bare page numeral in the bottom outer
corner — the Edexcel convention. No URL, no timestamp, no "Page N of M".
"""

from __future__ import annotations

import io

from playwright.sync_api import sync_playwright
from pypdf import PdfReader, PdfWriter

# A4 with the Edexcel-ish margin. Page number: bare numeral, bottom-right (the
# outer corner on a single-sided print).
_PAGE_MARGIN = {"top": "18mm", "bottom": "16mm", "left": "15mm", "right": "15mm"}

_FOOTER_TEMPLATE = (
    '<div style="width:100%;font-size:9px;font-family:Arial,Helvetica,sans-serif;'
    'color:#000;padding:0 15mm;box-sizing:border-box;text-align:right;">'
    '<span class="pageNumber"></span>'
    "</div>"
)
_EMPTY_HEADER = "<span></span>"


def _pad_to_even(pdf_bytes: bytes) -> bytes:
    """Append a blank page if needed so the paper prints double-sided cleanly."""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    if len(reader.pages) % 2 == 0:
        return pdf_bytes
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    last = reader.pages[-1].mediabox
    writer.add_blank_page(width=last.width, height=last.height)
    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()


def render_pdf(html: str, css: str) -> bytes:
    """Render a self-contained HTML fragment + CSS to a clean, even-page A4 PDF."""
    document = (
        "<!doctype html><html><head><meta charset='utf-8'>"
        f"<style>{css}</style></head><body>{html}</body></html>"
    )
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        try:
            page = browser.new_page()
            page.set_content(document, wait_until="networkidle")
            pdf = page.pdf(
                format="A4",
                margin=_PAGE_MARGIN,
                print_background=True,
                display_header_footer=True,
                header_template=_EMPTY_HEADER,
                footer_template=_FOOTER_TEMPLATE,
                prefer_css_page_size=False,
            )
        finally:
            browser.close()
    return _pad_to_even(pdf)
