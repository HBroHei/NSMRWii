import glob
import os
import shutil
import nsmbw
from nsmbw import NSMBWEntrances, NSMBWLoadSprite, NSMBWsprite, NSMBWtileset, NSMBWbgDat
import u8_m
from sys import exit
from random import randint
from random import seed
from json import loads
import globalVars

tileList1b = [b"Pa1_obake",b"Pa1_sabaku",b"Pa1_toride_sabaku",b'Pa1_shiro',b'Pa1_gake']

isDebugging = False

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

    # Read enemy randomization list and preference
    globalVars.enemyList = rulesDict["Enemies"]
    try:
        globalVars.enemyVarList = rulesDict["Enemy Variation"]
    except KeyError:
        globalVars.log += str("[i] 'Enemy Variation' not included" + "\n")
        pass

    # Check the reduce lag option
    globalVars.reduceLag = rulesDict["Reduce Lag"]

    # Check th "randomise entrance" option
    try:
        globalVars.randomiseEntrance = rulesDict["Entrance Randomization"]
    except KeyError:
        pass

    # Move the files that needs to be in the orginal names (Skipped levels)
    globalVars.skipLvl = rulesDict["Skip Level"]
    for istr in rulesDict["Skip Level"]:
        globalVars.log += str("Processing [S]"+STG_OLD + "/" + istr+"to"+STG_NEW + "/" + istr + "\n")
        shutil.move(STG_OLD + "/" + istr,STG_NEW + "/" + istr)
        if not istr=="Texture" and not isDebugging:
            editArcFile(istr,istr)

    # Group levels
    try:
        globalVars.lvlGroup = rulesDict["Level Group"]
    except KeyError:
        globalVars.log += str("[i] 'Level Group' not included" + "\n")
        pass

    # Group blocks(Tiles)
    try:
        globalVars.tileGroup = rulesDict["Tile Group"]
    except KeyError:
        globalVars.log += str("[i] 'Tile Group' not included" + "\n")
        pass


def editArcFile(istr,newName):
    #print(istr)
    globalVars.tileData = [[],[],[]]

    #Read the U8 archive content
    u8list = u8_m.openFile(STG_NEW+"/"+newName,STG_OLD + "/" + istr)
    u8FileList = u8list["File Name List"]
    areaNo = u8list["Number of area"]
    areaNo %= 4
    if areaNo==0:
        areaNo = 4
    #print("AreaNo",areaNo,istr,newName)
    
    #Loop through every area
    for i in range(1,areaNo+1):
        # Main area settings file
        lvlSetting = nsmbw.readDef(u8list["course"+ str(i) +".bin"]["Data"])
        # Phrase area tileset (Section 0)
        tilesetInfo = NSMBWtileset.phraseByteData(lvlSetting[0]["Data"])

        # Read tiles
        for j in range(0,2): #Loop through every layers
            if ("course"+ str(i) +"_bgdatL" + str(j) + ".bin") in u8list: # if layer (j) exist
                #Get tiles info
                globalVars.tilesData[j] = NSMBWbgDat.phraseByteData(u8list["course"+ str(i) +"_bgdatL" + str(j) + ".bin"]["Data"])
                globalVars.tilesData[j] = NSMBWbgDat.processTiles(globalVars.tilesData[j])
                de_t = globalVars.tilesData[:] ## DEBUG VARIABLE TO STORE TILESDATA
                # "Encode" and Save the layer tile data
                u8list["course"+ str(i) +"_bgdatL" + str(j) + ".bin"]["Data"] = NSMBWbgDat.toByteData(globalVars.tilesData[j])
        
        # Sprite Handling (Section 7,8)
        # "Decode" to Python array
        spriteData = NSMBWsprite.phraseByteData(lvlSetting[7]["Data"])
        sprLoadData = NSMBWLoadSprite.phraseByteData(lvlSetting[8]["Data"])
        # Process the sprites, i.e. randomize it
        if len(spriteData)>0:
            spriteData,sprLoadData,lvlSetting[7]["Size"] = NSMBWsprite.processSprites(spriteData,sprLoadData,istr)
        if globalVars.randomiseEntrance:
            # Phrase and randomise Entrance Info (Section 6)
            entrances = NSMBWEntrances.phraseByteData(lvlSetting[6]["Data"])
            entrances = NSMBWEntrances.processEntrances(entrances,istr,i)
            # "Encode" back to byte data for NSMBW
            lvlSetting[6]["Data"] = NSMBWEntrances.toByteData(entrances)
        #print("ENT_RAW ",lvlSetting[6]["Data"])
        lvlSetting[7]["Data"] = NSMBWsprite.toByteData(spriteData,lvlSetting[7]["Size"])
        lvlSetting[8]["Data"] = NSMBWLoadSprite.toByteData(sprLoadData,lvlSetting[8]["Size"])
        u8list["course"+ str(i) +".bin"]["Data"] = nsmbw.writeDef(lvlSetting)

    # "Encode" and Save the modified file
    u8n = u8_m.repackToBytes(u8list)
    u8_m.saveByteData(STG_NEW + "/" + newName,u8n)



    ## DEBUGGING CODE
    if isDebugging:
        print("\n============DEBUG INFO============\n")
        u8_de = u8_m.openFile(STG_NEW+"/"+newName,STG_NEW+"/"+newName)
        areaNo = u8list["Number of area"]
        if areaNo==0:
            areaNo = 4
        for i in range(1,areaNo+1):
            lvlSetting = nsmbw.readDef(u8list["course"+ str(i) +".bin"]["Data"])
            tilesetInfo = NSMBWtileset.phraseByteData(lvlSetting[0]["Data"])
            spriteData = NSMBWsprite.phraseByteData(lvlSetting[7]["Data"])
            
            for j in range(0,2):
                if ("course"+ str(i) +"_bgdatL" + str(j) + ".bin") in u8list:
                    #u8_m.saveTextData(newName + " course"+ str(i) +"_bgdatL" + str(j) + ".txt",str(u8list["course"+ str(i) +"_bgdatL" + str(j) + ".bin"]["Data"]))
                    globalVars.tilesData[j] = NSMBWbgDat.phraseByteData(u8list["course"+ str(i) +"_bgdatL" + str(j) + ".bin"]["Data"])
                    print(len(de_t[j])==len(globalVars.tilesData[j]))
                    for tilesData in de_t:
                        for blockData in tilesData:
                            print(blockData, blockData in globalVars.tilesData[j])
                    #u8list["course"+ str(i) +"_bgdatL" + str(j) + ".bin"]["Data"] = NSMBWbgDat.toByteData(globalVars.tilesData[j])
            


    


########### MAIN ############
if not os.path.exists("Stage"):
    print("Stage folder not found. Please place the 'Stage' folder and try again.")
    exit()

shutil.rmtree(STG_OLD,True)
shutil.rmtree(STG_NEW,True)


print("Copying the Stage folder...")
shutil.copytree("Stage",STG_OLD)

# NOTE DEBUG TAG
#isDebugging = True
#Load Preset files
readRandoRule()

### NOTE DEBUG TAG ### RE-COMMENT WHEN DONE ###

#os.rename(STG_OLD + "/test_entrance.arc" , STG_NEW + "/DEBUG.arc") #Rename and move the file
#editArcFile("","DEBUG.arc")
#exit()

skipB = []

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
        globalVars.log += ("Processing [G] "+istr+": Renaming to "+ilis[rdm] + "\n")
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
    globalVars.log += ("Processing "+istr+": Renaming to "+odir[rdm] + "\n")
    os.rename(STG_OLD + "/" + istr , STG_NEW + "/" + odir[rdm]) #Rename and move the file

    # U8 Archive Editting
    if istr not in skipB:
        editArcFile(istr,odir[rdm])

    del odir[rdm]
shutil.rmtree(STG_OLD)

lf = open("log.txt","w")
lf.write(globalVars.log)
lf.close()
print("Log file is written in log.txt")

#input("Shuffle completed. Press Enter to continue...")