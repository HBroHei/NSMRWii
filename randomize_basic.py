import os
import shutil
import nsmbw
from nsmbw import NSMBWsprite
import u8_m
import u8
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
# Texture Folder
shutil.move(STG_OLD + "/" + "Texture",STG_NEW + "/" + "Texture")
# 02-24.arc: 2-Castle, contains hard-coded stuff that will break the game if editted
shutil.move(STG_OLD + "/" + "02-24.arc",STG_NEW + "/" + "02-24.arc")

odir = os.listdir(STG_OLD)
odir_c = odir[:]

#Load Preset files
nsmbw.readRandoRule()

#Loop through each levels
for istr in odir_c:
    rdm = randint(0,len(odir)-1)
    print("Processing ",istr,": Renaming to ",odir[rdm])
    os.rename(STG_OLD + "/" + istr , STG_NEW + "/" + odir[rdm]) #Rename and move the file

    # U8 Archive Editting
    u8list = u8_m.openFile(STG_NEW+"/"+odir[rdm],STG_OLD + "/" + istr)
    u8FileList = u8list["File Name List"]
    lvlSetting = nsmbw.readDef(u8list["course1.bin"]["Data"])
    spriteData = NSMBWsprite.phraseByteData(lvlSetting[7]["Data"])
    spriteData = NSMBWsprite.randomEnemy(spriteData,STG_NEW+"/"+odir[rdm])

    lvlSetting[7]["Data"] = NSMBWsprite.toByteData(spriteData,lvlSetting[7]["Size"])
    u8list["course1.bin"]["Data"] = nsmbw.writeDef(lvlSetting)
    
    u8n = u8_m.repackToBytes(u8list)
    u8o = u8_m.openByteData(STG_NEW+"/"+odir[rdm])

    u8_m.saveByteData(STG_NEW + "/" + odir[rdm],u8n)
    
    #break #NOTE: break for debugging purpose

    del odir[rdm]
shutil.rmtree(STG_OLD)

