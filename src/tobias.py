import requests

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

        page.evaluate("setMediaId('dl_form', allMedia)")
        page.evaluate(f"setFormat('dl_form', '{selected_format}', allMedia);")
        page.evaluate("confirmPopup(document.forms['dl_form'], 'tooltip4');")

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
