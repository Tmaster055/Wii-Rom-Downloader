import curses
import cloudscraper
import urllib3
from bs4 import BeautifulSoup

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
            return main(answer)
        else:
            print("You need to type in 3 or more letters!")


if __name__ == "__main__":
    pass
