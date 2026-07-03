# md-converter

Convertisseur multi-format vers Markdown : **PDF, Word (.doc/.docx), EPUB, images (JPEG/PNG/...), pages web/HTML**, et en repli tout autre format supporté par `markitdown` (PPTX, XLSX, CSV, JSON, XML, TXT...).

Aucune limite de pages n'est imposée : les PDF, EPUB et documents Word sont traités page/élément par élément (streaming), quelle que soit leur taille.

## Application (exécutable, sans ligne de commande)

Le moyen le plus rapide de l'utiliser : un exécutable autonome qui lance une petite application
(interface web locale dans votre navigateur) — glissez-déposez un fichier, récupérez le Markdown.

1. Allez dans l'onglet **[Actions](https://github.com/kadjoum82-svg/fantastic-umbrella/actions/workflows/build-executables.yml)**
   du dépôt (ou **Releases** si une version taguée existe), et téléchargez l'exécutable de votre
   système parmi les artefacts du dernier run :
   - `mdconvert-app-windows.exe` (Windows)
   - `mdconvert-app-macos` (macOS)
   - `mdconvert-app-linux` (Linux)
2. Lancez-le (double-clic). Votre navigateur s'ouvre automatiquement sur l'application.
   - **Windows** : SmartScreen peut avertir « éditeur non reconnu » → *Informations
     complémentaires* → *Exécuter quand même* (l'exécutable n'est pas signé).
   - **macOS** : Gatekeeper bloquera le premier lancement → clic droit sur le fichier → *Ouvrir*
     (ou `xattr -d com.apple.quarantine mdconvert-app-macos` dans le Terminal), pour la même raison.
3. **Depuis votre téléphone** : le terminal affiche une seconde adresse du type
   `http://192.168.x.x:PORT/`. Ouvrez-la dans le navigateur du téléphone (même réseau Wi-Fi que
   l'ordinateur qui fait tourner l'application), puis utilisez *« Ajouter à l'écran d'accueil »*
   (Chrome/Safari) pour obtenir une icône d'application. Il ne s'agit pas d'une application native
   iOS/Android publiée sur un store — cela nécessiterait Xcode/Android Studio, un compte
   développeur et une revue de store, hors de portée d'un exécutable généré ici — mais l'expérience
   d'usage (icône, plein écran, hors ligne pour l'interface) est équivalente pour un usage
   personnel.

Pour reconstruire ces exécutables vous-même (ou en générer un pour une plateforme non listée) :

```bash
pip install -e ".[build]"
pyinstaller --noconfirm --onefile --name mdconvert-app \
  --add-data "md_converter/webapp/templates:md_converter/webapp/templates" \
  --add-data "md_converter/webapp/static:md_converter/webapp/static" \
  run_desktop.py
# sur Windows, remplacer les ":" du --add-data par ";"
```

L'exécutable ne fonctionne que sur le système d'exploitation pour lequel il a été construit ;
c'est pourquoi la CI (`.github/workflows/build-executables.yml`) le construit séparément pour
Windows, macOS et Linux à chaque tag `vX.Y.Z` (ou déclenchement manuel).

## Installation (ligne de commande / bibliothèque Python)

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

Une fois installé, `mdconvert-app` lance la même interface web locale que l'exécutable packagé,
sans avoir besoin de PyInstaller :

```bash
mdconvert-app
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
