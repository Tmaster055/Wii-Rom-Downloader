import os
import sys
import zipfile
import py7zr
import requests
import urllib3

from tqdm import tqdm
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_vimms_id(url):
    response = requests.get(url, timeout=15, verify=False)

    soup = BeautifulSoup(response.text, 'html.parser')
    serial_id = soup.find(id="serials").text
    middle_part = serial_id.split('-')[1]
    result = middle_part + "01"
    return result


def download_file(url: str, installer_path: str, headers = None):
    try:
        if headers:
            response = requests.get(url, stream=True, headers=headers)
        else:
            response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024
        t = tqdm(total=total_size, unit='B', unit_scale=True)
        with open(installer_path, 'wb') as f:
            for data in response.iter_content(block_size):
                t.update(len(data))
                f.write(data)
        t.close()
        print(f"Download was successful!")
    except Exception as e:
        print(f"Error while downloading: {e}")
        if os.path.exists(installer_path):
            os.remove(installer_path)
        sys.exit(1)


def extract_rename_folders(game_id: str, zip_path: str):
    print("Extracting Folders...")
    if ".7z" in zip_path:
        folder_path = zip_path.replace(".7z", "")
        with py7zr.SevenZipFile(zip_path, mode="r") as archive:
            archive.extractall(folder_path)
            print("Folders extracted!")
    else:
        folder_path = zip_path.replace(".zip", "")
        with zipfile.ZipFile(zip_path, mode="r") as archive:
            archive.extractall(folder_path)
            print("Folders extracted!")

    print("Removing zipfiles...")
    os.remove(zip_path)
    print("Removed zipfile!")

    print("Renaming in id...")
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)

        if os.path.isfile(file_path):
            name, ext = os.path.splitext(file)

            new_name = f"{game_id}{ext}"
            new_path = os.path.join(folder_path, new_name)

            os.rename(file_path, new_path)
            print(f"Renamed: {file} → {new_name}")

            if not ".txt" in ext:
                game = name.split("(")[0]
            else:
                os.remove(new_path)

    os.rename(folder_path, folder_path.replace(game_id, f"{game}[{game_id}]"))

    print("All files have been renamed.")


if __name__ == "__main__":
    pass
