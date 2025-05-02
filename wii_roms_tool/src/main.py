from wii_roms_tool.src import download_vimms_rom, download_romsfun_rom, search_for_rom_vimms, search_for_rom_romsfun


def main():
    print("Welcome to Wii-Rom-Downloader!")
    print("1: Vimms Lair")
    print("2: Romsfun (Recommended)")

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


if __name__ == "__main__":
    main()
