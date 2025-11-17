import requests
from pathlib import Path
import shutil
from zipfile import ZipFile


download_uris = [
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2018_Q4.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q1.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q2.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q3.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q4.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2020_Q1.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2220_Q1.zip",
]


download_folder = Path("downloads")

if download_folder.exists() and download_folder.is_dir():
    shutil.rmtree(download_folder)
    print(f"Deleted existing folder: {download_folder}")

download_folder.mkdir(exist_ok=True)

def download_file(uri: str) -> Path | None:
    filename = uri.split("/")[-1]
    zip_path = download_folder / filename

    response = requests.get(uri, stream=True)

    if response.status_code != 200:
        print(f"Failed to download {uri} (status {response.status_code})")
        return None

    with open(zip_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=4096):
            if chunk:
                f.write(chunk)
    print(f"Downloaded {zip_path.name}")
    return zip_path

def extract_and_delete_zip_file(zip_path: Path | None) -> None:
    if zip_path is None:
        return
    print(f"Extracting {zip_path.name}...")
    with ZipFile(zip_path, 'r') as z:
        z.extractall(download_folder)

    zip_path.unlink()
    print(f"Extracted and deleted {zip_path.name}")
    


def main():
    for uri in download_uris:
        zip_path = download_file(uri)
        extract_and_delete_zip_file(zip_path)
    return


if __name__ == "__main__":
    main()
