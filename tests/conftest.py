from __future__ import annotations

import shutil

import pytest

TESSERACT_AVAILABLE = shutil.which("tesseract") is not None
SOFFICE_AVAILABLE = shutil.which("soffice") is not None or shutil.which("libreoffice") is not None

requires_tesseract = pytest.mark.skipif(
    not TESSERACT_AVAILABLE, reason="Tesseract OCR non installé sur cette machine."
)

requires_soffice = pytest.mark.skipif(
    not SOFFICE_AVAILABLE, reason="LibreOffice (soffice) non installé sur cette machine."
)
