from common import download_vimms_rom
from search_vimms import search_for_rom_vimms


print("Welcome to Wii-Rom-Downloader!")
print("1: Vimms Lair")
print("2: Romsfun")

while True:
    answer = input("Which do you choose? ")

    if answer == "1":
        url = search_for_rom_vimms()
        download_vimms_rom(url)
        break
    elif answer == "2":
        print("Romsfun support is not yet available. Please choose another option.")
    else:
        print("Invalid input. Please enter 1 or 2.")

