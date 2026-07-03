from __future__ import annotations

import shutil
import subprocess

from docx import Document

from md_converter import convert

from .conftest import requires_soffice


def _make_docx(path):
    document = Document()
    document.add_heading("Titre du document", level=1)

    paragraph = document.add_paragraph()
    run_bold = paragraph.add_run("Ce texte est en gras")
    run_bold.bold = True
    paragraph.add_run(" et ceci est normal.")

    document.add_paragraph("Premier élément", style="List Bullet")
    document.add_paragraph("Deuxième élément", style="List Bullet")

    table = document.add_table(rows=2, cols=2)
    table.rows[0].cells[0].text = "Colonne A"
    table.rows[0].cells[1].text = "Colonne B"
    table.rows[1].cells[0].text = "1"
    table.rows[1].cells[1].text = "2"

    document.save(path)


def test_convert_docx_headings_lists_and_tables(tmp_path):
    docx_path = tmp_path / "sample.docx"
    _make_docx(docx_path)

    result = convert(str(docx_path))

    assert "# Titre du document" in result.markdown
    assert "**Ce texte est en gras**" in result.markdown
    assert "- Premier élément" in result.markdown
    assert "- Deuxième élément" in result.markdown
    assert "| Colonne A | Colonne B |" in result.markdown
    assert "| 1 | 2 |" in result.markdown


@requires_soffice
def test_convert_legacy_doc_via_libreoffice(tmp_path):
    docx_path = tmp_path / "ancien.docx"
    document = Document()
    document.add_heading("Document Word Ancien", level=1)
    document.add_paragraph("Contenu de test pour le format .doc.")
    document.save(docx_path)

    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    subprocess.run(
        [soffice, "--headless", "--norestore", "--convert-to", "doc", "--outdir", str(tmp_path), str(docx_path)],
        check=True,
        capture_output=True,
        timeout=300,
    )
    doc_path = tmp_path / "ancien.doc"
    assert doc_path.exists()

    result = convert(str(doc_path))

    assert "Document Word Ancien" in result.markdown
    assert "Contenu de test pour le format .doc." in result.markdown
