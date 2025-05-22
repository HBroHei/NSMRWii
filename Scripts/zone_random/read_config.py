from random import seed
from json import loads
from os import listdir, getcwd
import shutil

import globalVars

log = ""

enemyList = []
enemyVarList = []
reduceLag = False
randomiseEntrance = []
skipLvl = []
lvlGroup = []
tileGroup = []
tiles0List = []
secret_exit = []

STAGE_DIR = "./Stage/" if "Stage" in listdir(getcwd()) else "./Scripts/Stage/"
CONFIG_PATH = "./config.json" if "config.json" in listdir(getcwd()) else "./Scripts/config.json"

stageList = listdir(STAGE_DIR)

rf = open(CONFIG_PATH)
rulesDict = loads(rf.read())
rf.close()
# Initalize seed
seed(rulesDict["Seed"])
# Read enemy randomization list and preference
enemyList = rulesDict["Enemies"]
try:
    enemyVarList = rulesDict["Enemy Variation"]
except KeyError:
    log += str("[i] 'Enemy Variation' not included" + "\n")
    pass
# Check the reduce lag option
reduceLag = rulesDict["Reduce Lag"]
# Check th "randomise entrance" option
try:
    randomiseEntrance = rulesDict["Entrance Randomization"]
except KeyError:
    pass

# Gets the levels with secret exits, defined in the config file
try:
    secret_exit = rulesDict["Secret Exit List"]
except KeyError:
    print("Secret Exit def not found, exiting")
    pass

# Move the files that needs to be in the orginal names (Skipped levels)
STG_TEMP = "Stage_temp"
STG_OUT = "Stage_output"
shutil.rmtree(STG_TEMP,True)
shutil.rmtree(STG_OUT,True)
shutil.copytree(STAGE_DIR,STG_TEMP)
skipLvl = rulesDict["Skip Level"]
try:
    skip_but_rando = rulesDict["Skip But Randomise"]
except KeyError:
    print("\"Skip But Randomise\" not found in the config file.")
    print("Make sure you have enabled 'Version 2' in the Generator's Experimential Tab.")
    print("Levels not randomised. Exiting...")
    exit() # TODO Remove all of the above when V2 officially comes out
# for istr in rulesDict["Skip Level"]:
#     log += str("Processing [S]"+STG_TEMP + "/" + istr+"to"+STG_TEMP + "/" + istr + "\n")
#     shutil.move(STG_TEMP + "/" + istr,STG_OUT + "/" + istr)

# Group blocks(Tiles)
try:
    tileGroup = rulesDict["Tile Group"]
except KeyError:
    log += str("[i] 'Tile Group' not included" + "\n")
    pass

# TIleset 0 rando
try:
    tiles0List = rulesDict["Tileset 0"]
except KeyError:
    log += str("[i] 'Tileset 0' not included" + "\n")
    pass

windChance = max(0, min(rulesDict["Wind Chance"], 100))
darkChance = max(0, min(rulesDict["Dark Chance"], 100))
if darkChance>0:
    darkTypes = rulesDict["Dark Types"]
rockChance = rulesDict["Rock Chance"]

panel_rand = rulesDict["Power-up Panel Shuffle"]

# Sound related config
try:
    musicList = rulesDict["Music"]
except KeyError:
    pass
try:
    ambientList = rulesDict["Ambient"]
except KeyError:
    pass

# Add them all to the global vars list
globalVars.enemyList = enemyList
globalVars.enemyVarList = enemyVarList
globalVars.reduceLag = reduceLag
globalVars.tileGroup = tileGroup
globalVars.tiles0List = tiles0List
globalVars.windChance = windChance
globalVars.darkChance = darkChance
globalVars.darkTypes = darkTypes
globalVars.rockChance = rockChance
globalVars.panel_rand = panel_rand
globalVars.musicList = musicList
globalVars.ambientList = ambientList

globalVars.skipLvl = skipLvl
globalVars.skip_but_rando = skip_but_rando