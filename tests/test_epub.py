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


def test_convert_epub_extracts_embedded_images(tmp_path):
    book = epub.EpubBook()
    book.set_identifier("test-book-with-image")
    book.set_title("Livre Illustré")
    book.set_language("fr")

    image_bytes = b"\x89PNG\r\n\x1a\nfake-png-content"
    image_item = epub.EpubImage(
        uid="cover-img",
        file_name="images/illustration.png",
        media_type="image/png",
        content=image_bytes,
    )
    book.add_item(image_item)

    chapter = epub.EpubHtml(title="Chapitre 1", file_name="chap_1.xhtml", lang="fr")
    chapter.content = '<h1>Chapitre 1</h1><img src="images/illustration.png" alt="illustration">'
    book.add_item(chapter)

    book.toc = (chapter,)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ["nav", chapter]

    epub_path = tmp_path / "illustre.epub"
    epub.write_epub(str(epub_path), book)

    result = convert(str(epub_path))

    assert "images/illustration.png" in result.markdown
    assert result.assets.get("images/illustration.png") == image_bytes
