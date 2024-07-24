from random import seed
from json import loads
from os import listdir
import shutil

log = ""

enemyList = []
enemyVarList = []
reduceLag = False
randomiseEntrance = []
skipLvl = []
lvlGroup = []
tileGroup = []
secret_exit = []
stageList = listdir("./Stage/")

rf = open("config.json")
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
shutil.copytree("Stage",STG_TEMP)
skipLvl = rulesDict ["Skip Level"]
for istr in rulesDict["Skip Level"]:
    log += str("Processing [S]"+STG_TEMP + "/" + istr+"to"+STG_TEMP + "/" + istr + "\n")
    shutil.move(STG_TEMP + "/" + istr,STG_OUT + "/" + istr)

# Group blocks(Tiles)
try:
    tileGroup = rulesDict["Tile Group"]
except KeyError:
    log += str("[i] 'Tile Group' not included" + "\n")
    pass