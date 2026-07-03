from __future__ import annotations

from ebooklib import epub

from md_converter import convert


def _make_epub(path, n_chapters: int = 3):
    book = epub.EpubBook()
    book.set_identifier("test-book-id")
    book.set_title("Mon Livre de Test")
    book.set_language("fr")

    chapters = []
    for i in range(1, n_chapters + 1):
        chapter = epub.EpubHtml(title=f"Chapitre {i}", file_name=f"chap_{i}.xhtml", lang="fr")
        chapter.content = f"<h1>Chapitre {i}</h1><p>Contenu du chapitre numéro {i}.</p>"
        book.add_item(chapter)
        chapters.append(chapter)

    book.toc = tuple(chapters)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ["nav"] + chapters

    epub.write_epub(str(path), book)


def test_convert_epub_all_chapters_present(tmp_path):
    epub_path = tmp_path / "livre.epub"
    _make_epub(epub_path, n_chapters=5)

    result = convert(str(epub_path))

    assert "Mon Livre de Test" in result.markdown
    for i in range(1, 6):
        assert f"Chapitre {i}" in result.markdown
        assert f"Contenu du chapitre numéro {i}." in result.markdown
