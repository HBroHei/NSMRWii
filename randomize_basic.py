import os
import shutil
import nsmbw
from nsmbw import NSMBWLoadSprite, NSMBWsprite, NSMBWtileset
import u8_m
from sys import exit
from random import randint
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
    # Move the files that needs to be in the orginal names
    for istr in rulesDict["Skip Level"]:
        print("MOVING",STG_OLD + "/" + istr,"to",STG_NEW + "/" + istr)
        shutil.move(STG_OLD + "/" + istr,STG_NEW + "/" + istr)
    globalVars.enemyList = rulesDict["Enemies"]


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

#Loop through each levels
for istr in odir_c:
    rdm = randint(0,len(odir)-1)
    #rdm = 0
    #istr = "05-21.arc"
    #odir[rdm] = istr
    print("Processing ",istr,": Renaming to ",odir[rdm])
    os.rename(STG_OLD + "/" + istr , STG_NEW + "/" + odir[rdm]) #Rename and move the file

    # U8 Archive Editting
    if istr not in skipB:
        u8list = u8_m.openFile(STG_NEW+"/"+odir[rdm],STG_OLD + "/" + istr)

        u8_m.saveTextData("U8s.txt",u8_m.splitWithEachEle(u8list["Raw Data"][:520]))

        u8FileList = u8list["File Name List"]
        areaNo = u8list["Number of area"]
        if areaNo==0:
            areaNo = 4
        for i in range(1,areaNo+1):
            #print("i",i)
            lvlSetting = nsmbw.readDef(u8list["course"+ str(i) +".bin"]["Data"])
            #print(lvlSetting)
            tilesetInfo = NSMBWtileset.phraseByteData(lvlSetting[0]["Data"])
            
            spriteData = NSMBWsprite.phraseByteData(lvlSetting[7]["Data"])
            sprLoadData = NSMBWLoadSprite.phraseByteData(lvlSetting[8]["Data"])
            spriteData,sprLoadData = NSMBWsprite.randomEnemy(spriteData,sprLoadData,STG_NEW+"/"+odir[rdm])

            lvlSetting[7]["Data"] = NSMBWsprite.toByteData(spriteData,lvlSetting[7]["Size"])
            lvlSetting[8]["Data"] = NSMBWLoadSprite.toByteData(sprLoadData,lvlSetting[8]["Size"])
            u8list["course"+ str(i) +".bin"]["Data"] = nsmbw.writeDef(lvlSetting)

            #print(b"Pa1_obake" in tilesetInfo)
        u8n = u8_m.repackToBytes(u8list,(tilesetInfo[1] in tileList1b))
        u8o = u8_m.openByteData(STG_NEW+"/"+odir[rdm])

        u8_m.saveTextData("U8N.txt",u8_m.splitWithEachEle(u8n))
        u8_m.saveTextData("U8O.txt",u8_m.splitWithEachEle(u8o))

        u8_m.saveByteData(STG_NEW + "/" + odir[rdm],u8n)
        #u8_m.saveByteData(odir[rdm],u8n)

    
    #u8list = u8_m.openFile(odir[rdm],None)
    #u8FileList = u8list["File Name List"]
    #lvlSetting = nsmbw.readDef(u8list["course1.bin"]["Data"])
    #print(u8list["Raw Data"][:520])
    #u8_m.saveTextData("u8r.txt",u8_m.splitWithEachEle(u8list["Raw Data"][:520]))
    #break #NOTE: break for debugging purpose

    del odir[rdm]
shutil.rmtree(STG_OLD)

#input("Shuffle completed. Press Enter to continue...")