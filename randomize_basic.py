import os
import shutil
import nsmbw
from nsmbw import NSMBWLoadSprite, NSMBWsprite, NSMBWtileset
import u8_m
from sys import exit
from random import randint
from random import seed
from json import loads
import globalVars

tileList1b = [b"Pa1_obake",b"Pa1_sabaku",b"Pa1_toride_sabaku",b'Pa1_shiro',b'Pa1_gake']

#Folder name
STG_OLD = "Stage_Unshuffled"
STG_NEW = "Stage_Shuffled"

def readRandoRule():
    global erList
    rf = open("config.json")
    rulesDict = loads(rf.read())
    rf.close()
    # Initalize seed
    seed(rulesDict["Seed"])
    #Read enemy randomization list
    globalVars.enemyList = rulesDict["Enemies"]
    # Move the files that needs to be in the orginal names
    globalVars.skipLvl = rulesDict["Skip Level"]
    for istr in rulesDict["Skip Level"]:
        print("Processing [S]",STG_OLD + "/" + istr,"to",STG_NEW + "/" + istr)
        shutil.move(STG_OLD + "/" + istr,STG_NEW + "/" + istr)
        if not istr=="Texture":
            editArcFile(istr,istr)
    # Group levels
    try:
        globalVars.lvlGroup = rulesDict["Level Group"]
    except KeyError:
        pass


def editArcFile(istr,newName):
    #print(istr)
    u8list = u8_m.openFile(STG_NEW+"/"+newName,STG_OLD + "/" + istr)
    u8FileList = u8list["File Name List"]
    areaNo = u8list["Number of area"]
    if areaNo==0:
        areaNo = 4
    for i in range(1,areaNo+1):
        lvlSetting = nsmbw.readDef(u8list["course"+ str(i) +".bin"]["Data"])
        tilesetInfo = NSMBWtileset.phraseByteData(lvlSetting[0]["Data"])
        
        spriteData = NSMBWsprite.phraseByteData(lvlSetting[7]["Data"])
        sprLoadData = NSMBWLoadSprite.phraseByteData(lvlSetting[8]["Data"])
        spriteData,sprLoadData = NSMBWsprite.randomEnemy(spriteData,sprLoadData,STG_NEW+"/"+newName)

        lvlSetting[7]["Data"] = NSMBWsprite.toByteData(spriteData,lvlSetting[7]["Size"])
        lvlSetting[8]["Data"] = NSMBWLoadSprite.toByteData(sprLoadData,lvlSetting[8]["Size"])
        u8list["course"+ str(i) +".bin"]["Data"] = nsmbw.writeDef(lvlSetting)

    u8n = u8_m.repackToBytes(u8list,(tilesetInfo[1] in tileList1b))
    u8o = u8_m.openByteData(STG_NEW+"/"+newName)

    #u8_m.saveTextData("U8N.txt",u8_m.splitWithEachEle(u8n))
    #u8_m.saveTextData("U8O.txt",u8_m.splitWithEachEle(u8o))

    u8_m.saveByteData(STG_NEW + "/" + newName,u8n)


########### MAIN ############

if not os.path.exists("Stage"):
    print("Stage folder not found. Please place the 'Stage' folder and try again.")
    exit()

shutil.rmtree(STG_OLD,True)
shutil.rmtree(STG_NEW,True)


print("Copying the Stage folder...")
shutil.copytree("Stage",STG_OLD)

#Load Preset files
readRandoRule()

# Move the files that needs to be in the orginal names
#skipF = open("Skip List.txt","r")
#skipL = skipF.read().split("\n")
#
#for istr in skipL:
#    print("MOVING",STG_OLD + "/" + istr,"to",STG_NEW + "/" + istr)
#    shutil.move(STG_OLD + "/" + istr,STG_NEW + "/" + istr)
#
# Move the files that is bugged
#skipF = open("Level to be fixed","r")
skipB = []
#skipB = skipF.read().split("\n")
#
#for istr in skipB:
#    print("MOVING",STG_OLD + "/" + istr,"to",STG_NEW + "/" + istr)
#    shutil.move(STG_OLD + "/" + istr,STG_NEW + "/" + istr)

odir = os.listdir(STG_OLD)
odir_c = odir[:]
print("Processing grouped levels...")
#Randomizing Grouped levels first
for ilis in globalVars.lvlGroup:
    ilis_c = ilis[:]
    for istr in ilis_c:
        if not istr in odir_c:
            print(istr,": File not found in Stage folder. Please check if the file is missing or misspelled")
            if istr in globalVars.skipLvl:
                print("Hint: This level also appears in the Skip List. Do you still wish to randomize it?")
            exit()
        rdm = randint(0,len(ilis)-1)
        print("Processing [G] ",istr,": Renaming to ",ilis[rdm])
        os.rename(STG_OLD + "/" + istr , STG_NEW + "/" + ilis[rdm]) #Rename and move the file

        # U8 Archive Editting
        if istr not in skipB:
            editArcFile(istr,ilis[rdm])
        
        del odir[odir.index(ilis[rdm])]
        del ilis[rdm]
        
odir_c = odir[:]

#Loop through each levels
for istr in odir_c:
    rdm = randint(0,len(odir)-1)
    print("Processing ",istr,": Renaming to ",odir[rdm])
    os.rename(STG_OLD + "/" + istr , STG_NEW + "/" + odir[rdm]) #Rename and move the file

    # U8 Archive Editting
    if istr not in skipB:
        editArcFile(istr,odir[rdm])

    del odir[rdm]
shutil.rmtree(STG_OLD)

#input("Shuffle completed. Press Enter to continue...")