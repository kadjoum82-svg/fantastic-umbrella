from __future__ import annotations

from ..exceptions import ConversionError
from .base import ConversionResult


def convert_generic(path: str) -> ConversionResult:
    """Convertisseur de repli pour les formats non pris en charge nativement
    (pptx, xlsx, csv, json, xml, txt, ...), via la bibliothèque markitdown."""
    try:
        from markitdown import MarkItDown
    except ImportError as exc:
        raise ConversionError(
            "Le paquet 'markitdown' est requis pour convertir ce type de fichier."
        ) from exc

    try:
        result = MarkItDown().convert(path)
    except Exception as exc:
        raise ConversionError(f"Impossible de convertir '{path}': {exc}") from exc

    markdown = (result.text_content or "").strip() + "\n"
    return ConversionResult(markdown=markdown)
