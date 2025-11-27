pyinstaller main.py ^
    --version-file version.txt ^
    --name "FishCalendar" ^
    --noconsole ^
    --icon="assets/icon.ico" ^
    --add-data "assets;assets" ^
    --add-data "libs/FCForms/FCForms.dll;libs/FCForms"