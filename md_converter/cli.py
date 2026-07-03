from __future__ import annotations

import argparse
import sys
from pathlib import Path
from urllib.parse import urlparse

from . import __version__
from .core import convert
from .exceptions import ConversionError
from .utils.detect import SUPPORTED_EXTENSIONS, is_url


def _iter_inputs(inputs: list[str], recursive: bool) -> list[str]:
    resolved: list[str] = []
    for item in inputs:
        if is_url(item):
            resolved.append(item)
            continue
        path = Path(item)
        if path.is_dir():
            pattern = "**/*" if recursive else "*"
            for file in sorted(path.glob(pattern)):
                if file.is_file() and file.suffix.lower() in SUPPORTED_EXTENSIONS:
                    resolved.append(str(file))
        else:
            resolved.append(item)
    return resolved


def _write_assets(assets: dict[str, bytes], output_dir: Path) -> None:
    """Écrit les fichiers annexes (ex: images extraites) à côté du Markdown,
    au chemin relatif exact référencé par celui-ci."""
    for rel_path, content in assets.items():
        normalized = Path(rel_path)
        if normalized.is_absolute() or ".." in normalized.parts:
            continue
        asset_path = output_dir / normalized
        asset_path.parent.mkdir(parents=True, exist_ok=True)
        asset_path.write_bytes(content)


def _default_output_path(source: str, output_dir: Path | None) -> Path:
    if is_url(source):
        name = urlparse(source).path.rstrip("/").rsplit("/", 1)[-1] or "page"
        stem = Path(name).stem or "page"
        directory = output_dir or Path(".")
    else:
        stem = Path(source).stem
        directory = output_dir or Path(source).parent
    return directory / f"{stem}.md"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mdconvert",
        description=(
            "Convertit des fichiers PDF, Word (doc/docx), EPUB, images et pages web "
            "en Markdown, sans limite de pages."
        ),
    )
    parser.add_argument("inputs", nargs="+", help="Fichier(s), dossier(s) ou URL(s) à convertir.")
    parser.add_argument("-o", "--output", help="Fichier de sortie (uniquement pour une seule entrée).")
    parser.add_argument("--output-dir", help="Dossier de sortie pour les conversions en lot.")
    parser.add_argument("--recursive", action="store_true", help="Parcourt les sous-dossiers.")
    parser.add_argument("--no-ocr", action="store_true", help="Désactive l'OCR pour les images et PDF scannés.")
    parser.add_argument("--ocr-lang", default="eng+fra", help="Langue(s) Tesseract pour l'OCR (défaut: eng+fra).")
    parser.add_argument("--overwrite", action="store_true", help="Écrase les fichiers de sortie existants.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Affiche les avertissements de conversion.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    sources = _iter_inputs(args.inputs, args.recursive)
    if not sources:
        parser.error("Aucun fichier à convertir n'a été trouvé.")

    if args.output and len(sources) > 1:
        parser.error("--output ne peut être utilisé qu'avec une seule entrée ; utilisez --output-dir pour un lot.")

    output_dir = Path(args.output_dir) if args.output_dir else None
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)

    exit_code = 0
    for source in sources:
        out_path = Path(args.output) if args.output else _default_output_path(source, output_dir)

        if out_path.exists() and not args.overwrite:
            print(f"[ignoré] {source}: '{out_path}' existe déjà (utilisez --overwrite).", file=sys.stderr)
            continue

        try:
            result = convert(source, ocr=not args.no_ocr, ocr_lang=args.ocr_lang)
        except ConversionError as exc:
            print(f"[erreur] {source}: {exc}", file=sys.stderr)
            exit_code = 1
            continue

        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(result.markdown, encoding="utf-8")
        _write_assets(result.assets, out_path.parent)
        print(f"[ok] {source} -> {out_path}")

        if args.verbose:
            for warning in result.warnings:
                print(f"  avertissement: {warning}", file=sys.stderr)

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
