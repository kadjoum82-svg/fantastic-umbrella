from __future__ import annotations

from PIL import Image, ImageDraw

from md_converter import convert

from .conftest import requires_tesseract


def _make_text_image(path, text: str = "BONJOUR"):
    image = Image.new("RGB", (600, 150), color="white")
    draw = ImageDraw.Draw(image)
    draw.text((20, 60), text, fill="black")
    image.save(path)


@requires_tesseract
def test_convert_image_extracts_text_via_ocr(tmp_path):
    image_path = tmp_path / "texte.png"
    _make_text_image(image_path, "BONJOUR")

    result = convert(str(image_path))

    assert "BONJOUR" in result.markdown.upper()
    assert "![texte.png](texte.png)" in result.markdown


def test_convert_image_includes_alt_reference(tmp_path):
    image_path = tmp_path / "photo.jpg"
    Image.new("RGB", (50, 50), color="blue").save(image_path)

    result = convert(str(image_path))

    assert "![photo.jpg](photo.jpg)" in result.markdown
