from unittest.mock import patch, MagicMock
from zipfile import ZipFile
import main as downloader

@patch("main.requests.get")
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

@patch("main.requests.get")
def test_download_file_failure(mock_get, tmp_path, monkeypatch):
    # Mock the requests.get response
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    # Monkeypatch download_folder to temp directory
    monkeypatch.setattr(downloader, "download_folder", tmp_path)

    uri = "https://example.com/file.zip"
    zip_path = downloader.download_file(uri)

    assert zip_path is None

def test_extract_and_delete_zip_file(tmp_path, monkeypatch):
    # Create a fake CSV inside a temporary zip file
    csv_name = "good.csv"
    csv_content = "col1,col2\n1,2\n"

    # Create the zip file path
    zip_path = tmp_path / "test.zip"
    
    # Create a zip containing a CSV
    with ZipFile(zip_path, "w") as z:
        csv_file = tmp_path / csv_name
        csv_file.write_text(csv_content)
        z.write(csv_file, arcname=csv_name)  # store only the name

    # Ensure the downloader uses tmp_path as the extraction directory
    monkeypatch.setattr(downloader, "download_folder", tmp_path)

    # Run the function
    downloader.extract_and_delete_zip_file(zip_path)

    # Assertions
    extracted_csv = tmp_path / csv_name

    # CSV should have been extracted
    assert extracted_csv.exists()
    assert extracted_csv.read_text() == csv_content

    # Zip should have been deleted
    assert not zip_path.exists()

@patch("main.requests.get")
def test_full_downloader(mock_get, tmp_path, monkeypatch):
    # ---- Create a real ZIP in tmp_path for the success case ----
    csv_name = "good.csv"
    csv_content = b"col1,col2\n1,2\n"

    temp_zip_path = tmp_path / "good.zip"
    with ZipFile(temp_zip_path, "w") as z:
        z.writestr(csv_name, csv_content)

    good_zip_bytes = temp_zip_path.read_bytes()

    # ---- Mock response for SUCCESS ----
    good_response = MagicMock()
    good_response.status_code = 200
    good_response.iter_content = lambda chunk_size: [good_zip_bytes]

    # ---- Mock response for FAILURE ----
    bad_response = MagicMock()
    bad_response.status_code = 400

    # ---- First call returns 200, second returns 400 ----
    mock_get.side_effect = [good_response, bad_response]

    # ---- Patch folder and URIs ----
    monkeypatch.setattr(downloader, "download_folder", tmp_path)
    monkeypatch.setattr(
        downloader,
        "download_uris",
        ["https://example.com/good.zip", "https://example.com/bad.zip"]
    )

    # ---- Run full workflow ----
    downloader.main()

    # SUCCESS CASE:
    extracted_csv = tmp_path / "good.csv"
    downloaded_good_zip = tmp_path / "good.zip"

    assert extracted_csv.exists()
    assert extracted_csv.read_bytes() == csv_content
    assert not downloaded_good_zip.exists()    # should be deleted

    # FAILURE CASE:
    not_extracted_csv = tmp_path / "bad.csv"
    downloaded_bad_zip = tmp_path / "bad.zip"
    assert not downloaded_bad_zip.exists()
    assert not not_extracted_csv.exists()