import curses
import urllib3
import requests
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def fetch_links(query):
    url = f"https://vimm.net/vault/?p=list&system=Wii&q={query}"
    response = requests.get(url, timeout=15, verify=False)
    soup = BeautifulSoup(response.content, "html.parser")

    links = []
    for a in soup.find_all('a', href=True):
        if a.parent.name == 'td' and 'width:auto' in a.parent.get('style', ''):
            title = a.text.strip()
            link = f"https://vimm.net{a['href']}"

            row = a.find_parent('tr')
            if row:
                regions = [img['title'] for img in row.find_all('img', class_='flag') if 'title' in img.attrs]
                region_text = ", ".join(regions) if regions else "Unknown"
                extras_box = row.find('b', class_='redBorder')
                extras_text = f" ({extras_box['title']})" if extras_box and 'title' in extras_box.attrs else ""
            else:
                region_text = "Unknown"
                extras_text = ""
            if "manual" not in link:
                links.append((f"{title} ({region_text}){extras_text}", link))

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
        stdscr.addstr(0, 0, "Top 20 Results:", curses.A_BOLD)

        for idx, (title, _) in enumerate(links[:20]):
            stdscr.addstr(idx + 2, 0, title, curses.color_pair(1)
                          if idx == current_row else 0)

        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(links[:20]) - 1:
            current_row += 1
        elif key in (10, 13):
            return links[current_row][1]
        elif key == 27:
            return None


def main(query):
    links = fetch_links(query)
    return curses.wrapper(curses_menu, links)


def search_for_rom_vimms():
    while True:
        answer = input("What rom do you want to download? ")
        if len(answer.replace(" ", "")) >= 3:
            return main(answer)
        else:
            print("You need to type in 3 or more letters!")


if __name__ == "__main__":
    search_for_rom_vimms()
