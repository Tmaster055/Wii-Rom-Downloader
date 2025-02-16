from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://vimm.net/vault/81222")

        soup = BeautifulSoup(page.content(), "html.parser")
        select_tag = soup.find("select", {"id": "dl_format"})

        if select_tag:
            options = [option.text for option in select_tag.find_all("option")]
            print("Available formats:")
            for idx, option in enumerate(options):
                print(f"{idx}: {option}")

            choice = int(input("Choose format by number: "))
            selected_value = select_tag.find_all("option")[choice]["value"]

            page.select_option("#dl_format", selected_value)
            print(f"Selected format: {options[choice]}")

            page.evaluate(f"setFormat('dl_form', '{selected_value}', allMedia);")
            page.evaluate("confirmPopup(document.forms['dl_form'], 'tooltip4');")

        else:
            print("Format selector not found.")

        input("Press Enter to close...")
        browser.close()


if __name__ == "__main__":
    main()
