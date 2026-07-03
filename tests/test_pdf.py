from __future__ import annotations

import io

import fitz
from PIL import Image, ImageDraw

from md_converter import convert

from .conftest import requires_tesseract


def _make_text_pdf(path):
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Titre Principal", fontsize=24)
    page.insert_text((72, 110), "Ceci est un paragraphe de corps de texte normal.", fontsize=11)
    doc.save(path)
    doc.close()


def _make_scanned_pdf(path, text: str = "TEXTE SCANNE"):
    image = Image.new("RGB", (800, 200), color="white")
    draw = ImageDraw.Draw(image)
    draw.text((20, 80), text, fill="black")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")

    doc = fitz.open()
    page = doc.new_page(width=800, height=200)
    page.insert_image(fitz.Rect(0, 0, 800, 200), stream=buffer.getvalue())
    doc.save(path)
    doc.close()


def test_convert_pdf_text_extraction_and_heading(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    _make_text_pdf(pdf_path)

    result = convert(str(pdf_path))

    assert "Titre Principal" in result.markdown
    assert "Ceci est un paragraphe de corps de texte normal." in result.markdown
    assert "# Titre Principal" in result.markdown or "## Titre Principal" in result.markdown


@requires_tesseract
def test_convert_scanned_pdf_uses_ocr_fallback(tmp_path):
    pdf_path = tmp_path / "scanned.pdf"
    _make_scanned_pdf(pdf_path, "HELLO WORLD")

    result = convert(str(pdf_path))

    assert "HELLO" in result.markdown.upper()


def test_convert_pdf_without_ocr_flags_scanned_page(tmp_path):
    pdf_path = tmp_path / "scanned_no_ocr.pdf"
    _make_scanned_pdf(pdf_path, "HELLO WORLD")

    result = convert(str(pdf_path), ocr=False)

    assert any("scannée" in w for w in result.warnings)
