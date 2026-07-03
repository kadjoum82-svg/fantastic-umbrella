from __future__ import annotations

from pathlib import Path

from PIL import Image

from ..exceptions import ConversionError
from .base import ConversionResult


def convert_image(path: str, *, ocr_lang: str = "eng+fra", include_image_ref: bool = True) -> ConversionResult:
    try:
        image = Image.open(path)
        image.load()
    except Exception as exc:
        raise ConversionError(f"Impossible d'ouvrir l'image '{path}': {exc}") from exc

    warnings: list[str] = []
    text = ""
    try:
        import pytesseract

        text = pytesseract.image_to_string(image, lang=ocr_lang).strip()
    except ImportError:
        warnings.append("pytesseract n'est pas installé ; aucun texte n'a pu être extrait de l'image.")
    except Exception as exc:
        warnings.append(f"L'OCR a échoué ({exc}) ; aucun texte n'a pu être extrait de l'image.")

    filename = Path(path).name
    sections: list[str] = []
    if include_image_ref:
        sections.append(f"![{filename}]({filename})")
    sections.append(f"## Texte extrait (OCR)\n\n{text}" if text else "*[Aucun texte détecté par l'OCR]*")

    markdown = "\n\n".join(sections).strip() + "\n"
    return ConversionResult(markdown=markdown, warnings=warnings)
