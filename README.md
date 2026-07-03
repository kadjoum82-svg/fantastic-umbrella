# md-converter

Convertisseur multi-format vers Markdown : **PDF, Word (.doc/.docx), EPUB, images (JPEG/PNG/...), pages web/HTML**, et en repli tout autre format supporté par `markitdown` (PPTX, XLSX, CSV, JSON, XML, TXT...).

Aucune limite de pages n'est imposée : les PDF, EPUB et documents Word sont traités page/élément par élément (streaming), quelle que soit leur taille.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Dépendances système requises pour certaines fonctionnalités :
- **Tesseract OCR** (`tesseract-ocr`, `tesseract-ocr-fra`) — pour l'OCR des images et des PDF scannés.
- **Poppler** (`poppler-utils`) — utilisé en complément par certains outils PDF.
- **LibreOffice Writer** (`libreoffice-writer`) — uniquement nécessaire pour convertir les anciens fichiers `.doc`.

```bash
sudo apt-get install tesseract-ocr tesseract-ocr-fra poppler-utils libreoffice-writer
```

## Utilisation en ligne de commande

```bash
# Un seul fichier
mdconvert rapport.pdf -o rapport.md

# Plusieurs fichiers / formats mélangés
mdconvert document.docx livre.epub photo.jpg --output-dir sortie/

# Un dossier entier (récursif)
mdconvert ./mes_documents --recursive --output-dir sortie/

# Une page web
mdconvert https://exemple.com/article -o article.md

# Désactiver l'OCR ou changer la langue
mdconvert scan.pdf --no-ocr
mdconvert photo.jpg --ocr-lang eng
```

Options principales :

| Option | Description |
| --- | --- |
| `-o, --output` | Fichier de sortie (une seule entrée) |
| `--output-dir` | Dossier de sortie (conversion en lot) |
| `--recursive` | Parcourt les sous-dossiers |
| `--no-ocr` | Désactive l'OCR (images / PDF scannés) |
| `--ocr-lang` | Langue(s) Tesseract, défaut `eng+fra` |
| `--overwrite` | Écrase les fichiers `.md` existants |
| `-v, --verbose` | Affiche les avertissements de conversion |

## Utilisation en tant que bibliothèque

```python
from md_converter import convert

result = convert("rapport.pdf")
print(result.markdown)
print(result.warnings)  # avertissements éventuels (pages illisibles, etc.)
print(result.assets)    # fichiers annexes (ex: images EPUB) : {chemin_relatif: bytes}
```

Si `result.assets` n'est pas vide, écrivez chaque fichier au chemin relatif indiqué, à côté du
Markdown, pour que les liens/images qu'il contient restent valides (c'est ce que fait la CLI
automatiquement).

## Formats pris en charge

| Format | Méthode |
| --- | --- |
| PDF | Extraction de texte native (PyMuPDF) avec détection de titres par taille de police et des tableaux (grilles) restitués en tableaux Markdown ; OCR (Tesseract) automatique pour les pages scannées |
| DOCX | Titres, listes, tableaux et mise en forme (gras/italique) via `python-docx` |
| DOC | Conversion préalable en `.docx` via LibreOffice, puis pipeline DOCX |
| EPUB | Parcours de tous les chapitres du spine via `ebooklib` + conversion HTML→Markdown ; images embarquées extraites à côté du fichier `.md` avec liens réécrits |
| JPEG / PNG / BMP / TIFF / GIF / WEBP | OCR Tesseract (texte extrait) |
| Pages web / fichiers HTML | Extraction du contenu principal (`readability-lxml`) puis conversion en Markdown ; liens et images relatifs résolus en URLs absolues |
| Autres (PPTX, XLSX, CSV, JSON, XML, TXT...) | Repli via `markitdown` |

## Tests

```bash
pip install -e ".[dev]"
pytest
```
