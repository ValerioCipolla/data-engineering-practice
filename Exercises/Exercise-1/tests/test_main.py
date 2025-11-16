import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import BytesIO
from zipfile import ZipFile
import app.main as downloader
 # your script filename


# --- Helper to create an in-memory ZIP containing a CSV ---
def create_test_zip_bytes():
    mem_zip = BytesIO()
    with ZipFile(mem_zip, "w") as z:
        z.writestr("test.csv", "col1,col2\n1,2\n3,4")
    mem_zip.seek(0)
    return mem_zip.read()


# ---------------------------------------------------------
# Test: download_file() successful download
# ---------------------------------------------------------
@patch("app.main.requests.get")
def test_download_file_success(mock_get, tmp_path, monkeypatch):
    # Mock the requests.get response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.iter_content = lambda chunk_size: [b"abc", b"123"]
    mock_get.return_value = mock_response

    # Monkeypatch download_folder to temp directory
    monkeypatch.setattr(downloader, "download_folder", tmp_path)

    uri = "https://example.com/file.zip"
    zip_path = downloader.download_file(uri)

    expected_file_path = tmp_path / "file.zip"

    assert zip_path.exists()
    assert zip_path  == expected_file_path
    assert zip_path.read_bytes() == b"abc123"
