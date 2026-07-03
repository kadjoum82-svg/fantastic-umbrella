from __future__ import annotations

from md_converter import convert

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
