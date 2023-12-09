######################### FOR DEBUGGING PURPOSE ONLY #####################
################# USE randomize_basic.py FOR ACTUAL RANDO ################

import os
import shutil
import nsmbw
from nsmbw import NSMBWEntrances, NSMBWLoadSprite, NSMBWsprite, NSMBWtileset, NSMBWbgDat
from dolphinAutoTransfer import dolphinAutoTransfer
import u8_m
from sys import exit
from random import randint
from random import seed
from json import loads
import globalVars

tileList1b = [b"Pa1_obake",b"Pa1_sabaku",b"Pa1_toride_sabaku",b'Pa1_shiro',b'Pa1_gake']

isDebugging = False

#Folder name
STG_OLD = "Stage"
STG_NEW = "Stage"

def editArcFile(istr,newName):
    #print(istr)
    globalVars.tileData = [[],[],[]]

    #Read the U8 archive content
    u8list = u8_m.openFile(newName,istr)
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
                print("********************course"+ str(i) +"_bgdatL" + str(j))
                print("TilesData: \n",globalVars.tilesData)
                de_t = globalVars.tilesData[:] ## DEBUG VARIABLE TO STORE TILESDATA
        
        # Sprite Handling (Section 7,8)
        # "Decode" to Python array
        spriteData = NSMBWsprite.phraseByteData(lvlSetting[7]["Data"])
        print("SpriteData: \n")
        for spr in spriteData:
            print("ID:" , spr[0] , "X, Y:" , spr[1:3] , "Prop:" , spr[3] , "ZoneID:" , spr[4] , "extraByte:" , spr[5])
        sprLoadData = NSMBWLoadSprite.phraseByteData(lvlSetting[8]["Data"])
        print("SpriteLoadData: \n",sprLoadData)
        entrances = NSMBWEntrances.phraseByteData(lvlSetting[6]["Data"])
        print("EntranceData: \n",entrances)




########### MAIN ############

editArcFile("",input("Enter file name: "))