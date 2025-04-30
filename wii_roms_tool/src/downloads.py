import os
import sys
import cloudscraper
import urllib3

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from wii_roms_tool.src import get_vimms_id, download_file, extract_rename_folders

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

        game_id = 'game_id' # TODO Fetch game id for romsfun
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
