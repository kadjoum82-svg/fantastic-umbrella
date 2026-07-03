from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from docx import Document
from docx.document import Document as _DocumentType
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

from ..exceptions import ConversionError
from .base import ConversionResult

HEADING_RE = re.compile(r"^Heading (\d)$")


def convert_docx(path: str) -> ConversionResult:
    try:
        document = Document(path)
    except Exception as exc:
        raise ConversionError(f"Impossible de lire le document Word '{path}': {exc}") from exc

    parts: list[str] = []
    for block in _iter_block_items(document):
        if isinstance(block, Paragraph):
            md = _paragraph_to_markdown(block)
            if md:
                parts.append(md)
        elif isinstance(block, Table):
            table_md = _table_to_markdown(block)
            if table_md:
                parts.append(table_md)

    markdown = "\n\n".join(parts).strip() + "\n"
    return ConversionResult(markdown=markdown)


def convert_doc(path: str) -> ConversionResult:
    """Convertit un ancien .doc en le passant par LibreOffice puis par le pipeline .docx.

    Nécessaire car python-docx ne lit pas le format binaire .doc historique ;
    LibreOffice sait le réexporter fidèlement en .docx avant l'extraction Markdown.
    """
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        raise ConversionError(
            "La conversion des fichiers .doc nécessite LibreOffice ('soffice'), introuvable sur ce système."
        )

    with tempfile.TemporaryDirectory() as tmp:
        result = subprocess.run(
            [soffice, "--headless", "--norestore", "--convert-to", "docx", "--outdir", tmp, path],
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode != 0:
            raise ConversionError(f"Échec de la conversion .doc -> .docx via LibreOffice: {result.stderr.strip()}")

        converted = Path(tmp) / (Path(path).stem + ".docx")
        if not converted.exists():
            raise ConversionError("La conversion .doc -> .docx via LibreOffice n'a produit aucun fichier.")

        return convert_docx(str(converted))


def _iter_block_items(parent):
    if isinstance(parent, _DocumentType):
        parent_elm = parent.element.body
    else:
        parent_elm = parent._element

    for child in parent_elm.iterchildren():
        if child.tag == qn("w:p"):
            yield Paragraph(child, parent)
        elif child.tag == qn("w:tbl"):
            yield Table(child, parent)


def _paragraph_to_markdown(paragraph: Paragraph) -> str:
    text = _runs_to_markdown(paragraph).strip()
    if not text:
        return ""

    style = (paragraph.style.name or "").strip() if paragraph.style else ""

    heading_match = HEADING_RE.match(style)
    if heading_match:
        level = min(int(heading_match.group(1)), 6)
        return f"{'#' * level} {text}"
    if style == "Title":
        return f"# {text}"
    if "List" in style or _has_numbering(paragraph):
        return f"- {text}"
    return text


def _runs_to_markdown(paragraph: Paragraph) -> str:
    out: list[str] = []
    for run in paragraph.runs:
        text = run.text
        if not text:
            continue
        if run.bold and run.italic:
            text = f"***{text}***"
        elif run.bold:
            text = f"**{text}**"
        elif run.italic:
            text = f"*{text}*"
        out.append(text)
    return "".join(out)


def _has_numbering(paragraph: Paragraph) -> bool:
    ppr = paragraph._p.pPr
    if ppr is None:
        return False
    return ppr.find(qn("w:numPr")) is not None


def _table_to_markdown(table: Table) -> str:
    rows = [[cell.text.strip().replace("\n", " ") for cell in row.cells] for row in table.rows]
    if not rows:
        return ""

    header, *body_rows = rows
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * len(header)) + " |",
    ]
    for row in body_rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)
