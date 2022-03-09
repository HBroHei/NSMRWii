import os
import shutil
import nsmbw
from nsmbw import NSMBWLoadSprite, NSMBWsprite
import u8_m
from sys import exit
from random import randint




########### MAIN ############

if not os.path.exists("Stage"):
    print("Stage folder not found. Exiting the program...")
    exit()
#Folder name
STG_OLD = "Stage_Unshuffled"
STG_NEW = "Stage_Shuffled"

shutil.rmtree(STG_OLD,True)
shutil.rmtree(STG_NEW,True)


print("Copying the Stage folder...")
shutil.copytree("Stage",STG_OLD)
# Move the files that needs to be in the orginal names
skipF = open("Skip List.txt","r")
skipL = skipF.read().split("\n")

for istr in skipL:
    print("MOVING",STG_OLD + "/" + istr,"to",STG_NEW + "/" + istr)
    shutil.move(STG_OLD + "/" + istr,STG_NEW + "/" + istr)

# Move the files that is bugged
skipF = open("Level to be fixed","r")
skipB = skipF.read().split("\n")

for istr in skipB:
    print("MOVING",STG_OLD + "/" + istr,"to",STG_NEW + "/" + istr)
    shutil.move(STG_OLD + "/" + istr,STG_NEW + "/" + istr)

odir = os.listdir(STG_OLD)
odir_c = odir[:]

#Load Preset files
nsmbw.readRandoRule()

#Loop through each levels
for istr in odir_c:
    rdm = randint(0,len(odir)-1)
    #rdm = odir.index(istr)
    print("Processing ",istr,": Renaming to ",odir[rdm])
    os.rename(STG_OLD + "/" + istr , STG_NEW + "/" + odir[rdm]) #Rename and move the file

    # U8 Archive Editting
    if istr not in skipB:
        u8list = u8_m.openFile(STG_NEW+"/"+odir[rdm],STG_OLD + "/" + istr)
        u8FileList = u8list["File Name List"]
        lvlSetting = nsmbw.readDef(u8list["course1.bin"]["Data"])
        spriteData = NSMBWsprite.phraseByteData(lvlSetting[7]["Data"])
        sprLoadData = NSMBWLoadSprite.phraseByteData(lvlSetting[8]["Data"])
        spriteData,sprLoadData = NSMBWsprite.randomEnemy(spriteData,sprLoadData,STG_NEW+"/"+odir[rdm])

        lvlSetting[7]["Data"] = NSMBWsprite.toByteData(spriteData,lvlSetting[7]["Size"])
        lvlSetting[8]["Data"] = NSMBWLoadSprite.toByteData(sprLoadData,lvlSetting[8]["Size"])
        u8list["course1.bin"]["Data"] = nsmbw.writeDef(lvlSetting)

        u8n = u8_m.repackToBytes(u8list)
        u8o = u8_m.openByteData(STG_NEW+"/"+odir[rdm])

        u8_m.saveByteData(STG_NEW + "/" + odir[rdm],u8n)

    #break #NOTE: break for debugging purpose

    del odir[rdm]
shutil.rmtree(STG_OLD)

input("Shuffle completed. Press Enter to continue...")