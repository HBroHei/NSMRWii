# NSMRWii
 A New Super Mario Bros Wii Randomizer for general use such as enemy randomization\
 Currently the project is a work-in-progress.

## Features
- Shuffle levels
- Shuffle enemies (Partial, may crash with some enemy)

## Usage
 A very temporary documentation about how to use this.
 1. Place the "Stage" folder at the root directory (Obtained in the game's file)
 2. Compile randomize_basic.py: Open the terminal and type \
   a. <code>python randomizer_basic.py</code> or\
   b. <code>python3 randomizer_basic.py</code> \
   (Make sure python 3 is installed)
 3. The folder "Stage_Shuffled" will appear. Replace the "Stage" folder in NSMBW with that generated folder.
### Randomize enemies
 Insert the Sprite ID in "Enemy Shuffle List.txt"
 - IDs can be found in the Spreadsheet file "Enemy ID.xls", or in the Reggie Editor
 - **New line for each Sprite ID entry**
 - **Empty line will cause error. Remove empty lines in the file**
 - **Some sprite will cause crashes in the game. Testing is in progress for which (and how) sprite will crash the game**

## Planned Features
Note: Planned features may be changed or removed at anytime
- Full support for enemy randomization
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
