from __future__ import annotations

import shutil

import pytest

TESSERACT_AVAILABLE = shutil.which("tesseract") is not None

requires_tesseract = pytest.mark.skipif(
    not TESSERACT_AVAILABLE, reason="Tesseract OCR non installé sur cette machine."
)
