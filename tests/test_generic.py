from __future__ import annotations

import json

from md_converter import convert


def test_convert_csv_fallback_produces_markdown_table(tmp_path):
    csv_path = tmp_path / "donnees.csv"
    csv_path.write_text("nom,age\nAlice,30\nBob,25\n", encoding="utf-8")

    result = convert(str(csv_path))

    assert "| nom | age |" in result.markdown
    assert "| Alice | 30 |" in result.markdown
    assert "| Bob | 25 |" in result.markdown


def test_convert_json_fallback_produces_content(tmp_path):
    json_path = tmp_path / "donnees.json"
    json_path.write_text(json.dumps({"cle": "valeur importante"}), encoding="utf-8")

    result = convert(str(json_path))

    assert "valeur importante" in result.markdown


def test_convert_txt_fallback_preserves_text(tmp_path):
    txt_path = tmp_path / "notes.txt"
    txt_path.write_text("Une simple note en texte brut.", encoding="utf-8")

    result = convert(str(txt_path))

    assert "Une simple note en texte brut." in result.markdown
