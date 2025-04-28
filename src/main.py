from common import download_vimms_rom
from search_vimms import search_for_rom_vimms
from src.common import download_romsfun_rom
from src.search_romsfun import search_for_rom_romsfun

print("Welcome to Wii-Rom-Downloader!")
print("1: Vimms Lair")
print("2: Romsfun")

while True:
    answer = input("Which do you choose? ")

    if answer == "1":
        while True:
            url = search_for_rom_vimms()
            if url is None:
                pass
            else:
                download_vimms_rom(url)
                break
        break
    elif answer == "2":
        while True:
            url = search_for_rom_romsfun()
            if url is None:
                pass
            else:
                download_romsfun_rom(url)
                break
        break
    else:
        print("Invalid input. Please enter 1 or 2.")
