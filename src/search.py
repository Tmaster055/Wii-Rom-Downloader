import requests
import curses

from bs4 import BeautifulSoup

def get_search_results(answer: str):
    result = f"https://vimm.net/vault/?p=list&system=Wii&q={answer}"

    response = requests.get(result, timeout=15)
    soup = BeautifulSoup(response.content, "html.parser")

    links = []

    for a_tag in soup.find_all('a', href=True):
        parent = a_tag.parent
        if parent.name == 'td' and 'width:auto' in parent.get('style', ''):
            title = a_tag.text.strip()
            link = result + a_tag['href']
            links.append((title, link))

    if not links:
        raise ValueError("No results found.")

    for link in links:
        print(link)

    def curses_menu(stdscr, links):
        curses.curs_set(0)
        current_row = 0

        while True:
            try:
                stdscr.clear()

                stdscr.addstr(0, 0, "Top 20 Results:", curses.A_BOLD)

                for idx, (title, _) in enumerate(links):
                    if idx == current_row:
                        stdscr.addstr(idx + 2, 0, title.encode("utf-8"), curses.color_pair(1))
                    else:
                        stdscr.addstr(idx + 2, 0, title.encode("utf-8"))

                stdscr.refresh()

                key = stdscr.getch()

                if key == curses.KEY_UP and current_row > 0:
                    current_row -= 1
                elif key == curses.KEY_DOWN and current_row < len(links) - 1:
                    current_row += 1
                elif key == curses.KEY_ENTER or key in [10, 13]:
                    return links[current_row][1]
                elif key == 27:
                    return None
            except Exception:
                raise ValueError("Please increase terminal size!")

    def main(stdscr):
        curses.start_color()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        return curses_menu(stdscr, links)

    selected_link = curses.wrapper(main)
    return selected_link

print(get_search_results("Just"))
