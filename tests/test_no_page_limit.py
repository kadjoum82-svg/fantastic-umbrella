from __future__ import annotations

import fitz

from md_converter import convert

N_PAGES = 250


def _make_large_pdf(path, n_pages: int):
    doc = fitz.open()
    for i in range(n_pages):
        page = doc.new_page()
        page.insert_text((72, 72), f"Contenu unique de la page numero {i + 1}", fontsize=11)
    doc.save(path)
    doc.close()


def test_convert_pdf_has_no_artificial_page_cap(tmp_path):
    pdf_path = tmp_path / "large.pdf"
    _make_large_pdf(pdf_path, N_PAGES)

    result = convert(str(pdf_path))

    for i in range(1, N_PAGES + 1):
        assert f"Contenu unique de la page numero {i}" in result.markdown
    assert f"<!-- Page {N_PAGES}/{N_PAGES} -->" in result.markdown


def test_convert_epub_has_no_artificial_chapter_cap(tmp_path):
    from ebooklib import epub

    n_chapters = 120
    book = epub.EpubBook()
    book.set_identifier("large-book")
    book.set_title("Livre Volumineux")
    book.set_language("fr")

    chapters = []
    for i in range(1, n_chapters + 1):
        chapter = epub.EpubHtml(title=f"Chapitre {i}", file_name=f"chap_{i}.xhtml", lang="fr")
        chapter.content = f"<h1>Chapitre {i}</h1><p>Texte unique {i}.</p>"
        book.add_item(chapter)
        chapters.append(chapter)

    book.toc = tuple(chapters)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ["nav"] + chapters

    epub_path = tmp_path / "large.epub"
    epub.write_epub(str(epub_path), book)

    result = convert(str(epub_path))

    for i in range(1, n_chapters + 1):
        assert f"Texte unique {i}." in result.markdown
