import curses
import cloudscraper
import urllib3
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def fetch_links(query):
    url = f"https://romsfun.com/roms/nintendo-wii/?s={query}"
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    links = []
    for div in soup.find_all('div', class_='col-archive-rom'):
        a = div.find('a', href=True)
        title_tag = div.find('h3')
        if a and title_tag:
            title = title_tag.text.strip()
            link = a['href']
            if not link.startswith("http"):
                link = "https://romsfun.com" + link
            links.append((title, link))

    if not links:
        raise ValueError("No results found.")

    return links


def curses_menu(stdscr, links):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    current_row = 0

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Top 16 Results:", curses.A_BOLD)

        for idx, (title, _) in enumerate(links[:20]):
            stdscr.addstr(idx + 2, 0, title, curses.color_pair(1) if idx == current_row else 0)

        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(links[:16]) - 1:
            current_row += 1
        elif key in (10, 13):
            return links[current_row][1]
        elif key == 27:
            return None


def main(query):
    links = fetch_links(query)
    return curses.wrapper(curses_menu, links)


def search_for_rom_romsfun():
    while True:
        answer = input("What rom do you want to download? ")
        if len(answer.replace(" ", "")) >= 3:
            url = main(answer)
            break
        else:
            print("You need to type in 3 or more letters!")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        stealth_sync(page)

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
    print(search_for_rom_romsfun())
