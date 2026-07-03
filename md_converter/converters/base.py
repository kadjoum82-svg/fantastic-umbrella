from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ConversionResult:
    """Résultat d'une conversion vers Markdown."""

    markdown: str
    warnings: list[str] = field(default_factory=list)
    # Fichiers annexes (ex: images extraites) à écrire à côté du Markdown pour
    # que les liens relatifs qu'il contient restent valides. Clé = chemin
    # relatif tel que référencé dans le Markdown, valeur = contenu binaire.
    assets: dict[str, bytes] = field(default_factory=dict)
