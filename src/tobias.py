import os
import time
import zipfile
import requests

from tqdm import tqdm
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()
        page.goto("https://vimm.net/vault/63633")

        soup = BeautifulSoup(page.content(), "html.parser")

        select_version = soup.find("select", {"id": "dl_version"})
        select_format = soup.find("select", {"id": "dl_format"})

        if select_version:
            versions = [option.text for option in select_version.find_all("option")]
            print("Available versions:")
            for idx, version in enumerate(versions):
                print(f"{idx}: {version}")
            version_choice = int(input("Choose version by number: "))
            selected_version = select_version.find_all("option")[version_choice]["value"]
            page.select_option("#dl_version", selected_version)
            print(f"Selected version: {versions[version_choice]}")
        else:
            print("Version selector not found.")

        if select_format:
            formats = [option.text for option in select_format.find_all("option")]
            print("Available formats:")
            for idx, fmt in enumerate(formats):
                print(f"{idx}: {fmt}")
            format_choice = int(input("Choose format by number: "))
            selected_format = select_format.find_all("option")[format_choice]["value"]
            page.select_option("#dl_format", selected_format)
            print(f"Selected format: {formats[format_choice]}")
        else:
            print("Format selector not found.")

        page.evaluate(f"setMediaId('dl_form', allMedia)")
        page.evaluate(f"setFormat('dl_form', '{selected_format}', allMedia);")
        page.evaluate("confirmPopup(document.forms['dl_form'], 'tooltip4');")

        with page.expect_download() as download_info:
            page.evaluate("confirmPopup(document.forms['dl_form'], 'tooltip4');")

        download = download_info.value
        download_path = download.path()

        new_filename = "000011000.7z"
        new_path = os.path.join(os.path.dirname(download_path), new_filename)

        print("Download gestartet...")

        # Fortschrittsanzeige mit tqdm
        start_time = time.time()
        while not os.path.exists(download_path):
            time.sleep(1)  # Warte, bis die Datei existiert

        file_size = 0
        with tqdm(unit="B", unit_scale=True, desc="Downloading") as pbar:
            while True:
                try:
                    new_size = os.path.getsize(download_path)
                    pbar.update(new_size - file_size)
                    file_size = new_size

                    if download.state == "completed":
                        break
                except FileNotFoundError:
                    pass
                time.sleep(1)  # Warte auf Updates

        os.rename(download_path, new_path)
        print(f"File saved as: {new_path}")

        with zipfile.ZipFile(new_path, 'r') as zip_ref:
            extract_path = os.path.splitext(new_path)[0]
            zip_ref.extractall(extract_path)
            print(f"Extracted to: {extract_path}")

        input("Press Enter to close...")
        browser.close()


def get_gametdb_id(url):
    response = requests.get(url, timeout=15, verify=False)

    soup = BeautifulSoup(response.text, 'html.parser')
    serial_id = soup.find(id="serials").text
    middle_part = serial_id.split('-')[1]
    result = middle_part + "01"
    return result



if __name__ == "__main__":
    main()
    print(get_gametdb_id("https://vimm.net/vault/18172"))
