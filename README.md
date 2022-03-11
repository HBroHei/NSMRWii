# New Super Mario Randomizer Wii
 A New Super Mario Bros Wii Randomizer for general use such as enemy randomization\
 Currently the project is a work-in-progress.
***DISCLAMER: This program only received limited testing. The game may crash or get bugged at any time***

## Features
- Shuffle levels
- RAndomize enemies

## Usage
 ### Prerequest
 - Python 3.x (Only tested on 3.9 or above): https://www.python.org/downloads/ 
   - Windows store version can be installed instead
 - NSMBW Stage folder (The one that would be used for the Reggie! Editor)
 - This project (Download this as zip, and unzip on the local computer)
 ### Procedure
 **This instruction is for Windows only. MacOS and Linux command will be created shortly.** \
 **Type python3 randomize_basic.py directly into the terminal for now**
 1. Place the "Stage" folder at the root directory (Obtained in the game's file: DATA/files/)
 2. Open the file "Start.bat"
 3. The folder "Stage_Shuffled" will appear. Replace the "Stage" folder in NSMBW with that generated folder.\
 ### Randomize enemies
 Insert the Sprite ID in "Enemy Shuffle List.txt"
 - **New line for each Sprite ID entry**
 - **Empty line will cause error. Remove empty lines in the file**
 - IDs can be found in the Spreadsheet file "Enemy ID.xls", or in the Reggie Editor
 - **This feature only received limited testing. Crashes or bugs may be expected in current stage**

## Planned Features
Note: Planned features may be changed or removed at anytime
- Configuration file
- Full support for enemy randomization
- Unique enemies (Randomize properties)
- Block randomization
- Tileset randomizaion
- Area / Entrance randomization
- Support for level description for levels made by Reggie!
- Seed system

## Notes
 - Although this project was not based on the Reggie! NSMBW level editor,
 Some U8 / Level data phrasing procedure were written with the help from the source code of the Reggie! Editor. \
Reggie! Editor: https://www.github.com/roadrunnerwmc/reggie-updated and https://www.github.com/clf78/reggie-next \
Information about U8 archive is provided from https://wiki.tockdom.com/wiki/U8_(File_Format) and https://wiibrew.org/wiki/U8_archive \
 ***Due to an upcoming IRL event, updates to this project will be slowed down or paused at times until Late May***
