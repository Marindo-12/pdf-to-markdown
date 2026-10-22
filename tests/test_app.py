import io
import unittest
from unittest.mock import patch

import pymupdf

from app import MAX_UPLOAD_BYTES, create_app


def make_pdf() -> bytes:
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), "Local conversion test")
    contents = document.tobytes()
    document.close()
    return contents


class UploadAppTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app({"TESTING": True, "SECRET_KEY": "test-secret"})
        self.client = self.app.test_client()
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.csrf_token = response.data.decode().split(
            'name="csrf_token" value="', 1
        )[1].split('"', 1)[0]

    def post_pdf(self, filename: str, content: bytes):
        return self.client.post(
            "/",
            data={
                "csrf_token": self.csrf_token,
                "pdf": (io.BytesIO(content), filename),
            },
            content_type="multipart/form-data",
        )

    @patch("app.convert_pdf", return_value="# Converted locally\n")
    def test_valid_pdf_returns_markdown_download(self, convert_mock) -> None:
        response = self.post_pdf(r"..\private\notes.pdf", make_pdf())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "text/markdown")
        self.assertIn("attachment;", response.headers["Content-Disposition"])
        self.assertIn("notes.md", response.headers["Content-Disposition"])
        self.assertEqual(response.get_data(as_text=True), "# Converted locally\n")
        convert_mock.assert_called_once()

    def test_real_pdf_conversion_returns_extracted_text(self) -> None:
        response = self.post_pdf("local-document.pdf", make_pdf())

        self.assertEqual(response.status_code, 200)
        self.assertIn("Local conversion test", response.get_data(as_text=True))

    def test_rejects_non_pdf_extension(self) -> None:
        response = self.post_pdf("notes.txt", make_pdf())
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"must have a .pdf extension", response.data)

    def test_rejects_non_pdf_content(self) -> None:
        response = self.post_pdf("notes.pdf", b"not a pdf")
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"does not appear to be a PDF", response.data)

    def test_rejects_missing_file(self) -> None:
        response = self.client.post(
            "/", data={"csrf_token": self.csrf_token}, content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Choose a PDF file", response.data)

    def test_rejects_invalid_csrf_token(self) -> None:
        response = self.client.post("/", data={"csrf_token": "invalid"})
        self.assertEqual(response.status_code, 400)

    def test_rejects_oversized_upload(self) -> None:
        with patch("app.MAX_UPLOAD_BYTES", 128):
            response = self.post_pdf("large.pdf", b"%PDF-" + b"x" * 124)
        self.assertEqual(response.status_code, 413)
        self.assertIn(b"maximum upload size is 25 MB", response.data)

    def test_rejects_untrusted_host(self) -> None:
        response = self.client.get("/", headers={"Host": "example.com"})
        self.assertEqual(response.status_code, 400)

    def test_response_disables_caching(self) -> None:
        response = self.client.get("/")
        self.assertEqual(response.headers["Cache-Control"], "no-store")
        self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")

    def test_upload_size_limit_is_25_mib(self) -> None:
        self.assertEqual(MAX_UPLOAD_BYTES, 25 * 1024 * 1024)


if __name__ == "__main__":
    unittest.main()
