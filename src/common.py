import os
import sys

import py7zr
import requests
import urllib3


from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def download_vimms_rom(url):
    with sync_playwright() as p:
        download_path = os.path.join(os.path.expanduser("~"), "Downloads")
        rom_downloader_path = os.path.join(download_path, "Rom-Downloader")
        os.makedirs(rom_downloader_path, exist_ok=True)

        browser = p.chromium.launch(headless=False)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()
        page.goto(url)

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
            if len(versions) != 1:
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
            if len(formats) != 1:
                page.select_option("#dl_format", selected_format)
            print(f"Selected format: {formats[format_choice]}")
        else:
            print("Format selector not found.")
            print("This rom is currently not downloadable!")
            sys.exit()

        game_id = get_vimms_id(url)
        zip_path = os.path.join(rom_downloader_path, game_id + ".7z")
        with page.expect_download() as download_info:
            page.evaluate("setMediaId('dl_form', allMedia)")
            page.evaluate(f"setFormat('dl_form', '{selected_format}', allMedia);")
            page.evaluate("confirmPopup(document.forms['dl_form'], 'tooltip4');")

        print("Downloading...")
        download = download_info.value
        download_path = download.path()
        download.save_as(zip_path)
        print(f"Download successful: {zip_path}")
        browser.close()

        print("Extracting Folders...")
        folder_path = zip_path.replace(".7z", "")
        with py7zr.SevenZipFile(zip_path, mode="r") as archive:
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

                if not "Vimm" in name:
                    game = name.split("(")[0]
                else:
                    os.remove(new_path)

        os.rename(folder_path, folder_path.replace(game_id, f"{game}[{game_id}]"))

        print("All files have been renamed.")


def get_vimms_id(url):
    response = requests.get(url, timeout=15, verify=False)

    soup = BeautifulSoup(response.text, 'html.parser')
    serial_id = soup.find(id="serials").text
    middle_part = serial_id.split('-')[1]
    result = middle_part + "01"
    return result


def download_romsfun_rom(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto(url)

        page.wait_for_selector('.btn.btn-primary.btn-block.mx-auto.mb-4.small')

        download_page_url = page.query_selector('.btn.btn-primary.btn-block.mx-auto.mb-4.small').get_attribute('href')
        print(f"Download page URL: {download_page_url}")

        page.goto(download_page_url)

        page.wait_for_selector('div.bg-white.border.rounded.shadow-sm.py-2.px-3.mb-4 table')

        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')

        rom_links = soup.select('div.bg-white.border.rounded.shadow-sm.py-2.px-3.mb-4 table tbody tr td a')

        print("Choose the ROM file you want to download:")
        for index, rom in enumerate(rom_links, start=1):
            print(f"{index}. {rom.text.strip()}")

        try:
            choice = int(input("Enter the number of the ROM you want to download: "))
            if 1 <= choice <= len(rom_links):
                selected_link = rom_links[choice - 1]['href']
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

        browser.close()
        return selected_link


if __name__ == "__main__":
    pass
