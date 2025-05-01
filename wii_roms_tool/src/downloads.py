import os
import platform
import subprocess
import sys
import tarfile
import zipfile
import cloudscraper
import py7zr
import urllib3

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from wii_roms_tool.src import get_vimms_id, download_file, get_gametdb_id

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def download_romsfun_rom(url):
    print("Preparing...")
    download_path = os.path.join(os.path.expanduser("~"), "Downloads")
    rom_downloader_path = os.path.join(download_path, "Rom-Downloader")
    os.makedirs(rom_downloader_path, exist_ok=True)

    scraper = cloudscraper.create_scraper()
    response = scraper.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')
    button = soup.select_one('.btn.btn-primary.btn-block.mx-auto.mb-4.small')

    if button:
        url = button.get('href')
    else:
        raise ValueError("Button-Element not found!")

    response = scraper.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    rom_links = soup.select('div.bg-white.border.rounded.shadow-sm.py-2.px-3.mb-4 table tbody tr td a')

    print("Choose the ROM file you want to download:")
    for index, rom in enumerate(rom_links, start=1):
        print(f"{index}. {rom.text.strip()}")

    selected_link = None
    try:
        choice = int(input("Enter the number of the ROM you want to download: "))
        if 1 <= choice <= len(rom_links):
            selected_link = rom_links[choice - 1]['href']
        else:
            print("Invalid choice. Please try again.")
    except ValueError:
        print("Invalid input. Please enter a number.")

    print("Starting to fetch...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto(selected_link, wait_until='domcontentloaded')
        page.wait_for_selector('a#download')
        download_link = page.query_selector('a#download').get_attribute('href')
        browser.close()

    game_id = 'game_id'
    zip_path = os.path.join(rom_downloader_path, game_id + ".zip")

    download_file(download_link, zip_path)

    extract_rename_folders(game_id, zip_path)


def download_vimms_rom(url):
    print("Preparing...")
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

        with page.expect_download() as download_info:
            page.evaluate("setMediaId('dl_form', allMedia)")
            page.evaluate(f"setFormat('dl_form', '{selected_format}', allMedia);")
            page.evaluate("confirmPopup(document.forms['dl_form'], 'tooltip4');")

        download = download_info.value
        download_url = download.url

        user_agent = page.evaluate("() => navigator.userAgent")

        cookies = context.cookies()
        cookie_header = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])

        headers = {
            "User-Agent": user_agent,
            "Referer": url,
            "Cookie": cookie_header,
        }

        game_id = get_vimms_id(url)
        zip_path = os.path.join(rom_downloader_path, game_id + ".7z")

        browser.close()

    download_file(download_url, zip_path, headers)

    extract_rename_folders(game_id, zip_path)


def download_and_extract_wit():
    def locate_wit(extract_dir):
        for root, dirs, files in os.walk(extract_dir):
            if dirs:
                first_folder = dirs[0]
                wit_dir = os.path.join(root, first_folder, "bin")
                for root2, _, files2 in os.walk(wit_dir):
                    for file in files2:
                        if file.lower() == "wit.exe" or file == "wit":
                            wit_executable = os.path.join(root2, file)
                            print(f"Found WIT at: {wit_executable}")
                            return wit_executable
        return None

    system = platform.system()
    base_url = "https://wit.wiimm.de/download"

    if system == "Windows":
        filename = "wit-v3.05a-r8638-cygwin64.zip"
    elif system == "Linux":
        filename = "wit-v3.05a-r8638-x86_64.tar.gz"
    elif system == "Darwin":
        filename = "wit-v3.05a-r8638-mac.tar.gz"
    else:
        raise OSError(f"Unsupported OS: {system}")

    download_url = f"{base_url}/{filename}"
    appdata_path = os.path.join(
        os.getenv("APPDATA") or os.path.expanduser("~"), "wii-roms-tool"
    )
    archive_path = os.path.join(appdata_path, filename)
    extract_dir = os.path.join(appdata_path, "wit_tool")
    os.makedirs(extract_dir, exist_ok=True)
    wit_executable = locate_wit(extract_dir)

    if wit_executable:
        return wit_executable

    print(f"Downloading WIT from...")
    download_file(download_url, archive_path)

    print("Extracting archive ...")
    if filename.endswith(".zip"):
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
    elif filename.endswith(".tar.gz"):
        with tarfile.open(archive_path, 'r:gz') as tar_ref:
            tar_ref.extractall(extract_dir)
    else:
        raise ValueError("Unsupported archive format")
    os.remove(archive_path)
    wit_executable = locate_wit(extract_dir)
    if wit_executable:
        return wit_executable

    raise FileNotFoundError("WIT executable not found in the archive.")


def download_and_extract_dolphin():
    def locate_dolphin(extract_dir):
        for root, dirs, files in os.walk(extract_dir):
            if dirs:
                first_folder = dirs[0]
                dolphin_dir = os.path.join(root, first_folder)
                for root2, _, files2 in os.walk(dolphin_dir):
                    for file in files2:
                        if file == "DolphinTool.exe":
                            dolphin_executable = os.path.join(root2, file)
                            print(f"Found dolphin at: {dolphin_executable}")
                            return dolphin_executable
        return None

    base_url = "https://dl.dolphin-emu.org/releases/2503/dolphin-2503-x64.7z"
    filename = "dolphin-2503-x64.7z"
    appdata_path = os.path.join(
        os.getenv("APPDATA") or os.path.expanduser("~"), "wii-roms-tool"
    )
    archive_path = os.path.join(appdata_path, filename)
    extract_dir = os.path.join(appdata_path, "dolphin")
    os.makedirs(extract_dir, exist_ok=True)
    dolphin_executable = locate_dolphin(extract_dir)

    if dolphin_executable:
        return dolphin_executable

    print(f"Downloading dolphin from...")
    download_file(base_url, archive_path)

    print("Extracting archive ...")
    with py7zr.SevenZipFile(archive_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    os.remove(archive_path)

    dolphin_executable = locate_dolphin(extract_dir)
    if dolphin_executable:
        return dolphin_executable

    raise FileNotFoundError("dolphin executable not found in the archive.")


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
    game = "NamingError"
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)

        if os.path.isfile(file_path):
            name, ext = os.path.splitext(file)
            if not ".txt" in ext:
                game = name.split("(")[0]
            else:
                os.remove(file_path)
                continue
            if game_id == "game_id":
                game_id = get_gametdb_id(game)

            new_name = f"{game_id}{ext}"
            new_path = os.path.join(folder_path, new_name)

            os.rename(file_path, new_path)
            print(f"Renamed: {file} → {new_name}")
    if "game_id" in folder_path:
        os.rename(folder_path, folder_path.replace("game_id", f"{game}[{game_id}]"))
        end_file = os.path.join(folder_path.replace("game_id", f"{game}[{game_id}]"), new_name)
    else:
        os.rename(folder_path, folder_path.replace(game_id, f"{game}[{game_id}]"))
        end_file = os.path.join(folder_path.replace(game_id, f"{game}[{game_id}]"), new_name)
    print("All files have been renamed.")

    convert_to_wbfs(end_file)


def convert_to_wbfs(file_path):
    while True:
        answer = input("Do you want to convert to wbfs? (Real wii hardware) (y/n): ").strip().lower()
        if answer in ("yes", "y"):
            break
        elif answer in ("no", "n"):
            return
        else:
            print("Please answer 'yes' or 'no'.")
    if file_path.endswith(".wbfs"):
        print("Provided file is already a wbfs file!")
        return
    if platform.system() != "Windows":
        print("Currently no support on your os!")
        return
    wit_path = download_and_extract_wit()
    dolphin_path = download_and_extract_dolphin()
    iso_path = file_path[:-4] + ".iso"

    print("Converting to iso!...")
    try:
        subprocess.run([dolphin_path, "convert", "-i", file_path, "-o", iso_path, "-f", "iso"], check=True)
        os.remove(file_path)
        print(f"Conversion complete: {iso_path}")
    except subprocess.CalledProcessError as e:
        print("WIT error:", e)
    except Exception as e:
        print("Unexpected error:", e)

    print("Converting to wbfs!...")
    try:
        subprocess.run([wit_path, "convert", iso_path, "--wbfs"], check=True)
        print(f"Conversion complete!")
    except subprocess.CalledProcessError as e:
        print("WIT error:", e)
    except Exception as e:
        print("Unexpected error:", e)
