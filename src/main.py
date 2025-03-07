from common import download_vimms_rom
from search_vimms import search_for_rom_vimms


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
        print("Romsfun support is not yet available. Please choose another option.")
    else:
        print("Invalid input. Please enter 1 or 2.")
