import json
from os import listdir

import u8_m
import nsmbw
import globalVars
from Util import tilePosToObjPos

outJson = dict()
lvlSetting_arr = []

# DEBUG FLAG TOGGLE
isDebug = True

def checkInZone(zoneData, tilePos):
    # for every zone, Check X pos, then Y pos
    for i in range(0,len(zoneData)-1):
        zoneDat = zoneData[i]
        #              Min X                       Max X = min x + width
        if tilePos[0]>=zoneDat[0] and tilePos[0]<=(zoneDat[0]+zoneDat[2])\
            or tilePos[1]>=zoneDat[1] and tilePos[1]<=(zoneDat[1]+zoneDat[2]):
            return i
    return -1

def readAllSettings(raw_setting):
    # The function name lied. Only nessary settings will be read and stored.
    # TODO Add phrasing function to the following sections

    # Section 2
    zoneBound = nsmbw.NSMBWZoneBound.phraseByteData(raw_setting[2]["Data"])
    # Section 4
    topBackground = nsmbw.NSMBWZoneBG.phraseByteData(raw_setting[4]["Data"])
    # Section 5
    bottomBackground = nsmbw.NSMBWZoneBG.phraseByteData(raw_setting[5]["Data"])
    # Phrase Entrance Info (Section 6)
    entrances = nsmbw.NSMBWEntrances.phraseByteData(raw_setting[6]["Data"])
    # Sprite Handling (Section 7,8)
    # "Decode" to Python array
    spriteData = nsmbw.NSMBWsprite.phraseByteData(raw_setting[7]["Data"])
    sprLoadData = nsmbw.NSMBWLoadSprite.phraseByteData(raw_setting[8]["Data"])
    # Section 9
    zoneData = nsmbw.NSMBWZones.phraseByteData(raw_setting[9]["Data"])
    # Section 10
    locData = nsmbw.NSMBWLocations.phraseByteData(raw_setting[10]["Data"])
    # Section 11
    camProfile = nsmbw.NSMBWCamProfile.phraseByteData(raw_setting[11]["Data"])
    # Section 12
    pathProp = nsmbw.NSMBWPathProperties.phraseByteData(raw_setting[12]["Data"])
    # Section 13
    pathNode = nsmbw.NSMBWPathNode.phraseByteData(raw_setting[13]["Data"])

    # DEBUG
    if isDebug:
        # print(zoneBound)
        # print(topBackground)
        # print(zoneData)
        # print(locData)
        print(camProfile)
        print(pathProp)
        print(pathNode)
        print("-----------------")
        # raw_setting[2]["Data"] = nsmbw.NSMBWZoneBound.toByteData(zoneBound)
        # raw_setting[4]["Data"] = nsmbw.NSMBWZoneBG.toByteData(topBackground)
        # raw_setting[9]["Data"] = nsmbw.NSMBWZones.toByteData(zoneData)
        # raw_setting[10]["Data"] = nsmbw.NSMBWLocations.toByteData(locData)
        raw_setting[11]["Data"] = nsmbw.NSMBWCamProfile.toByteData(camProfile)
        raw_setting[12]["Data"] = nsmbw.NSMBWPathProperties.toByteData(pathProp)
        raw_setting[13]["Data"] = nsmbw.NSMBWPathNode.toByteData(pathNode)
        # print(nsmbw.NSMBWZoneBound.phraseByteData(raw_setting[2]["Data"]))
        # print(nsmbw.NSMBWZoneBG.phraseByteData(raw_setting[4]["Data"]))
        # print(nsmbw.NSMBWZones.phraseByteData(raw_setting[9]["Data"]))
        # print(nsmbw.NSMBWLocations.phraseByteData(raw_setting[10]["Data"]))
        print(nsmbw.NSMBWCamProfile.phraseByteData(raw_setting[11]["Data"]))
        print(nsmbw.NSMBWPathProperties.phraseByteData(raw_setting[12]["Data"]))
        print(nsmbw.NSMBWPathNode.phraseByteData(raw_setting[13]["Data"]))

def main():
    global lvlSetting_arr
    # rf = open("config.json")
    # rulesDict = json.loads(rf.read())
    # rf.close()

    for filename in listdir("./Stage"):
        if isDebug:
            if filename!="05-05.arc":
                continue
        u8list = u8_m.openFile("Stage/" + filename)
        u8FileList = u8list["File Name List"]
        areaNo = u8list["Number of area"]
        areaNo %= 4
        if areaNo==0:
            areaNo = 4
        
        lvlSetting_arr = []

        #Loop through every area
        for i in range(1,areaNo+1):
            lvlSetting_raw = nsmbw.readDef(u8list["course"+ str(i) +".bin"]["Data"])
            readAllSettings(lvlSetting_raw)
            exit()

        # Read tiles
        for j in range(0,2): #Loop through every layers
            if ("course"+ str(i) +"_bgdatL" + str(j) + ".bin") in u8list: # if layer (j) exist
                # Get tiles info
                globalVars.tilesData[j] = nsmbw.NSMBWbgDat.phraseByteData(u8list["course"+ str(i) +"_bgdatL" + str(j) + ".bin"]["Data"])
                for tile in globalVars.tilesData[j]:
                    zoneNo = checkInZone(tilePosToObjPos((tile[1],tile[2])))
                    if zoneNo!=-1:
                        print(zoneNo,tile)
        
if __name__ == "__main__":
    main()