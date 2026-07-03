from __future__ import annotations

from md_converter import convert
from md_converter.converters import web_converter

SAMPLE_HTML = """
<html>
<head><title>Mon Article de Test</title></head>
<body>
  <nav>Menu de navigation à ignorer</nav>
  <article>
    <h1>Mon Article de Test</h1>
    <p>Voici le <strong>premier paragraphe</strong> de l'article avec du contenu utile
    et suffisamment de texte pour que l'extraction du contenu principal fonctionne correctement.</p>
    <p>Un second paragraphe pour vérifier que le contenu est bien converti en Markdown,
    avec encore davantage de texte substantiel afin d'aider l'algorithme d'extraction.</p>
    <p>Cette page comporte également une liste d'éléments importants à ne pas perdre lors
    de la conversion, comme détaillé ci-dessous :</p>
    <ul>
      <li>Point un de la liste</li>
      <li>Point deux de la liste</li>
    </ul>
  </article>
  <footer>Pied de page à ignorer</footer>
</body>
</html>
"""


def test_convert_html_file_extracts_main_content(tmp_path):
    html_path = tmp_path / "page.html"
    html_path.write_text(SAMPLE_HTML, encoding="utf-8")

    result = convert(str(html_path))

    assert "premier paragraphe" in result.markdown
    assert "second paragraphe" in result.markdown
    assert "Point un de la liste" in result.markdown
    assert "Point deux de la liste" in result.markdown


RELATIVE_LINKS_HTML = """
<html>
<head><title>Article avec liens relatifs</title></head>
<body>
  <article>
    <h1>Article avec liens relatifs</h1>
    <p>Voici un lien relatif vers <a href="/autre-page.html">une autre page</a> et suffisamment
    de texte pour que l'extraction du contenu principal fonctionne correctement sur cet exemple.</p>
    <img src="images/illustration.png" alt="illustration">
    <p>Encore un peu de texte substantiel pour aider l'algorithme de détection du contenu principal.</p>
  </article>
</body>
</html>
"""


class _FakeResponse:
    def __init__(self, text: str, url: str):
        self.text = text
        self.url = url

    def raise_for_status(self) -> None:
        return None


def test_convert_web_resolves_relative_links_and_images(monkeypatch):
    def fake_get(url, headers=None, timeout=None):
        return _FakeResponse(RELATIVE_LINKS_HTML, "https://exemple.com/blog/article.html")

    monkeypatch.setattr(web_converter.requests, "get", fake_get)

    result = convert("https://exemple.com/blog/article.html")

    assert "https://exemple.com/autre-page.html" in result.markdown
    assert "https://exemple.com/blog/images/illustration.png" in result.markdown
