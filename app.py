from __future__ import annotations

import secrets
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

import pymupdf
from flask import Flask, abort, render_template, request, send_file, session
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename

from convert_pdf import convert_pdf

MAX_UPLOAD_BYTES = 25 * 1024 * 1024
MAX_REQUEST_BYTES = MAX_UPLOAD_BYTES + 64 * 1024


def create_app(test_config: dict[str, object] | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=secrets.token_bytes(32),
        MAX_CONTENT_LENGTH=MAX_REQUEST_BYTES,
        TRUSTED_HOSTS=["127.0.0.1", "localhost"],
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Strict",
    )
    if test_config:
        app.config.update(test_config)

    @app.after_request
    def add_security_headers(response):
        response.headers["Cache-Control"] = "no-store"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; img-src 'self'; style-src 'self'; "
            "form-action 'self'; base-uri 'none'; frame-ancestors 'none'"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    def render_upload_page(message: str | None = None, status: int = 200):
        csrf_token = session.setdefault("csrf_token", secrets.token_urlsafe(32))
        return render_template("index.html", csrf_token=csrf_token, message=message), status

    @app.get("/assets/pdf-to-md-banner.png")
    def banner():
        banner_path = Path(__file__).parent / "assets" / "pdf-to-md-banner.png"
        return send_file(banner_path, mimetype="image/png", max_age=3600)

    @app.errorhandler(RequestEntityTooLarge)
    def handle_file_too_large(error: RequestEntityTooLarge):
        return render_upload_page(
            "That file is too large. The maximum upload size is 25 MB.",
            error.code or 413,
        )

    @app.route("/", methods=["GET", "POST"])
    def index():
        if request.method == "GET":
            return render_upload_page()

        expected_token = session.get("csrf_token")
        submitted_token = request.form.get("csrf_token", "")
        if not expected_token or not secrets.compare_digest(
            expected_token, submitted_token
        ):
            abort(400)

        uploaded_file = request.files.get("pdf")
        if uploaded_file is None or not uploaded_file.filename:
            return render_upload_page("Choose a PDF file to convert.", 400)
        if Path(uploaded_file.filename).suffix.lower() != ".pdf":
            return render_upload_page("The selected file must have a .pdf extension.", 400)

        uploaded_file.stream.seek(0, 2)
        file_size = uploaded_file.stream.tell()
        uploaded_file.stream.seek(0)
        if file_size > MAX_UPLOAD_BYTES:
            return render_upload_page(
                "That file is too large. The maximum upload size is 25 MB.", 413
            )

        header = uploaded_file.stream.read(1024)
        if b"%PDF-" not in header:
            return render_upload_page("The selected file does not appear to be a PDF.", 400)
        uploaded_file.stream.seek(0)

        safe_name = secure_filename(uploaded_file.filename)
        output_stem = Path(safe_name).stem or "converted"

        with TemporaryDirectory(prefix="pdf-to-markdown-") as temporary_directory:
            pdf_path = Path(temporary_directory) / "upload.pdf"
            uploaded_file.save(pdf_path)

            try:
                with pymupdf.open(pdf_path) as document:
                    if document.needs_pass:
                        return render_upload_page(
                            "This PDF is password-protected. Remove the password and try again.",
                            400,
                        )
                    if document.page_count == 0:
                        return render_upload_page("This PDF contains no pages.", 400)

                markdown = convert_pdf(pdf_path)
            except (pymupdf.FileDataError, OSError, RuntimeError, ValueError) as error:
                app.logger.warning("PDF conversion rejected (%s)", type(error).__name__)
                return render_upload_page(
                    "This PDF could not be read or converted. Check that it is not damaged, "
                    "password-protected, or unsupported, then try again.",
                    400,
                )

        response = send_file(
            BytesIO(markdown.encode("utf-8")),
            mimetype="text/markdown; charset=utf-8",
            as_attachment=True,
            download_name=f"{output_stem}.md",
            max_age=0,
        )
        return response

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=8000, debug=False)
