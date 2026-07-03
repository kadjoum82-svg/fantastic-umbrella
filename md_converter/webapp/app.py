from __future__ import annotations

import base64
import io
import sys
import tempfile
import zipfile
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from ..core import convert
from ..exceptions import ConversionError

MAX_CONTENT_LENGTH = 512 * 1024 * 1024  # 512 Mo ; aucune limite de pages n'est imposée par ailleurs


def _resource_root() -> Path:
    """Localise templates/ et static/, que l'app tourne en source ou packagée (PyInstaller)."""
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS")) / "md_converter" / "webapp"
    return Path(__file__).parent


def create_app() -> Flask:
    root = _resource_root()
    app = Flask(
        __name__,
        template_folder=str(root / "templates"),
        static_folder=str(root / "static"),
    )
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.post("/convert")
    def convert_route():
        url = (request.form.get("url") or "").strip()
        ocr = request.form.get("ocr", "on") == "on"
        ocr_lang = request.form.get("ocr_lang") or "eng+fra"
        upload = request.files.get("file")

        if url:
            stem = "page"
            try:
                result = convert(url, ocr=ocr, ocr_lang=ocr_lang)
            except ConversionError as exc:
                return jsonify(error=str(exc)), 400
        elif upload and upload.filename:
            stem = Path(upload.filename).stem or "document"
            with tempfile.TemporaryDirectory() as tmp:
                tmp_path = Path(tmp) / upload.filename
                upload.save(tmp_path)
                try:
                    result = convert(str(tmp_path), ocr=ocr, ocr_lang=ocr_lang)
                except ConversionError as exc:
                    return jsonify(error=str(exc)), 400
        else:
            return jsonify(error="Merci de choisir un fichier ou de saisir une URL."), 400

        if result.assets:
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.writestr(f"{stem}.md", result.markdown)
                for rel_path, content in result.assets.items():
                    zf.writestr(rel_path, content)
            payload = buffer.getvalue()
            filename = f"{stem}.zip"
            mimetype = "application/zip"
        else:
            payload = result.markdown.encode("utf-8")
            filename = f"{stem}.md"
            mimetype = "text/markdown"

        return jsonify(
            filename=filename,
            mimetype=mimetype,
            content_b64=base64.b64encode(payload).decode("ascii"),
            warnings=result.warnings,
            preview=result.markdown[:20000],
        )

    return app
