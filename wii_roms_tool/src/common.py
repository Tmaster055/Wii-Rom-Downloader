import os
import sys
import requests
import urllib3

from tqdm import tqdm
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

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


def get_gametdb_id(query):
    def choose_region():
        print("Choose the right Region for the rom:")
        print("1. Europa (Australia)")
        print("2. USA")
        print("3. Japan")

        while True:
            region_choice = input("Choose (1/2/3): ")

            if region_choice == "1":
                return "P"
            elif region_choice == "2":
                return "E"
            elif region_choice == "3":
                return "J"
            else:
                print("Invalid Choice!")


    url = f"https://www.gametdb.com/Main/Results?q={query}"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto(url)

        page.wait_for_selector(".gsc-resultsbox-visible .gs-title", timeout=20000)

        url = page.locator(".gsc-resultsbox-visible .gs-title a").first.get_attribute("href")
        print(url)

        browser.close()

    if url:
        game_id = url.strip("/").split("/")[-1]
        trimmed_id = game_id[:-3]
        game_id = trimmed_id + choose_region() + "01"
        return game_id
    return None


if __name__ == "__main__":
    print(get_gametdb_id("Mario Kart Wii"))
