from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ConversionResult:
    """Résultat d'une conversion vers Markdown."""

    markdown: str
    warnings: list[str] = field(default_factory=list)
