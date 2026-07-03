from __future__ import annotations

from .converters.base import ConversionResult
from .utils.detect import detect_kind


def convert(source: str, *, ocr: bool = True, ocr_lang: str = "eng+fra") -> ConversionResult:
    """Convertit une source (fichier local ou URL) en Markdown.

    Le type de conversion est déduit automatiquement de l'extension ou du schéma
    de l'URL : pdf, docx/doc, epub, image, page web/HTML, ou un format générique
    pris en charge via markitdown (pptx, xlsx, csv, json, xml, txt, ...).
    """
    kind = detect_kind(source)

    if kind == "pdf":
        from .converters.pdf_converter import convert_pdf

        return convert_pdf(source, ocr=ocr, ocr_lang=ocr_lang)
    if kind == "docx":
        from .converters.docx_converter import convert_docx

        return convert_docx(source)
    if kind == "doc":
        from .converters.docx_converter import convert_doc

        return convert_doc(source)
    if kind == "epub":
        from .converters.epub_converter import convert_epub

        return convert_epub(source)
    if kind == "image":
        from .converters.image_converter import convert_image

        return convert_image(source, ocr_lang=ocr_lang)
    if kind == "web":
        from .converters.web_converter import convert_web

        return convert_web(source)

    from .converters.generic_converter import convert_generic

    return convert_generic(source)
