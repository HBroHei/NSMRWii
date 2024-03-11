import json
from os import listdir

import u8_m
import nsmbw
import globalVars
from Util import tilePosToObjPos, convertToJson

outJson = dict()
lvlSetting_arr = []

# Area settings
zoneBound = []
topBackground = []
bottomBackground = []
entrances = []
spriteData = []
sprLoadData = []
zoneData = []
locData = []
camProfile = []
pathProp = []
pathNode = []

# DEBUG FLAG TOGGLE
isDebug = True
# Format output JSON file?
jsonBeauty = False

# TODO Both checkPos functions needs to account for 16 blocks buffer.

def checkPosInZone(zoneData, sprPos, width=0, height=0) -> int:
    # for every zone, Check X pos, then Y pos
    for i in range(0,len(zoneData)-1):
        zoneDat = zoneData[i]
        #              Min X                       Max X = min x + width
        if checkPosInSpecificZone(zoneDat,sprPos,width,height):
            return zoneDat[6]
    return -1

def checkPosInSpecificZone(zoneDat, sprPos, width=0, height=0) -> int: # May also incoperate with the function above?
    # for every zone, Check X pos, then Y pos
    #              Min X                       Max X = min x + width
    return sprPos[0]+width>=(zoneDat[0]-16) and sprPos[0]<=(zoneDat[0]+zoneDat[2]+16)\
        or sprPos[1]+height>=(zoneDat[1]-16) and sprPos[1]<=(zoneDat[1]+zoneDat[2]+16)


def readAllSettings(raw_setting):
    # The function name lied. Only nessary settings will be read and stored.
    # Inseerted global here since IDK when the variable will disfunction like a local variable
    global zoneBound, topBackground, bottomBackground, entrances, spriteData, sprLoadData, zoneData, locData, camProfile, pathProp, pathNode
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
        # print(pathProp)
        # print(pathNode)
        print("-----------------")
        # raw_setting[2]["Data"] = nsmbw.NSMBWZoneBound.toByteData(zoneBound)
        # raw_setting[4]["Data"] = nsmbw.NSMBWZoneBG.toByteData(topBackground)
        # raw_setting[9]["Data"] = nsmbw.NSMBWZones.toByteData(zoneData)
        # raw_setting[10]["Data"] = nsmbw.NSMBWLocations.toByteData(locData)
        raw_setting[11]["Data"] = nsmbw.NSMBWCamProfile.toByteData(camProfile)
        # raw_setting[12]["Data"] = nsmbw.NSMBWPathProperties.toByteData(pathProp)
        # raw_setting[13]["Data"] = nsmbw.NSMBWPathNode.toByteData(pathNode)
        # print(nsmbw.NSMBWZoneBound.phraseByteData(raw_setting[2]["Data"]))
        # print(nsmbw.NSMBWZoneBG.phraseByteData(raw_setting[4]["Data"]))
        # print(nsmbw.NSMBWZones.phraseByteData(raw_setting[9]["Data"]))
        # print(nsmbw.NSMBWLocations.phraseByteData(raw_setting[10]["Data"]))
        print(nsmbw.NSMBWCamProfile.phraseByteData(raw_setting[11]["Data"]))
        # print(nsmbw.NSMBWPathProperties.phraseByteData(raw_setting[12]["Data"]))
        # print(nsmbw.NSMBWPathNode.phraseByteData(raw_setting[13]["Data"]))

def main():
    global lvlSetting_arr
    # rf = open("config.json")
    # rulesDict = json.loads(rf.read())
    # rf.close()

    for filename in listdir("./Stage"):
        if filename=="Texture":
            continue
        outJson[filename] = {}
        if isDebug:
            if filename!="02-02.arc":
                continue
        print(filename)
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
            outJson[filename][i] = {}
            # add zone to the output json
            for zone in zoneData:
                #print(zone)
                outJson[filename][i][zone[6]] = {
                    "topBackground" : [topBg for topBg in topBackground if topBg[0] == zone[7]],
                    "bottomBackground" : [bottomBg for bottomBg in bottomBackground if bottomBg[0] == zone[7]],
                    "entrance" : [ent for ent in entrances if checkPosInSpecificZone(zone,(ent[0],ent[1]))],
                    "sprites" : [ent for ent in spriteData if checkPosInSpecificZone(zone,(ent[0],ent[1]))],
                    "zone" : zone,
                    "location" : [loc for loc in locData if checkPosInSpecificZone(zone,(loc[0],loc[1]))],
                    "cameraProfile" : camProfile,
                    #"path" : [path for path in pathProp if checkPosInSpecificZone(zone,(node[0],node[1]))],
                    "pathNode" : [node for node in pathNode if checkPosInSpecificZone(zone,(node[0],node[1]))]
                }
                # Path
                outJson[filename][i][zone[6]]["path"] = [path for path in pathProp if pathNode[path[1]] in outJson[filename][i][zone[6]]["pathNode"]],

                

        # Read tiles
        for j in range(0,2): #Loop through every layers
            if ("course"+ str(i) +"_bgdatL" + str(j) + ".bin") in u8list: # if layer (j) exist
                # Get tiles info
                globalVars.tilesData[j] = nsmbw.NSMBWbgDat.phraseByteData(u8list["course"+ str(i) +"_bgdatL" + str(j) + ".bin"]["Data"])
                for tile in globalVars.tilesData[j]:
                    # Zones are in sprite coordinate system
                    zoneNo = checkPosInZone(zoneData,tilePosToObjPos((tile[1],tile[2])),*tilePosToObjPos((tile[3],tile[4])))
                    if zoneNo!=-1:
                        #print(i,j,outJson[filename][i].keys())
                        if "bgdatL" + str(j) not in outJson[filename][i][zoneNo]:
                            outJson[filename][i][zoneNo]["bgdatL" + str(j)] = []
                        outJson[filename][i][zoneNo]["bgdatL" + str(j)].append(tile)
                        #print(zoneNo,tile)
    with open('out.json', 'w', encoding='utf-8') as f:
        if not jsonBeauty:
            json.dump(convertToJson(outJson), f)
        else:
            json.dump(convertToJson(outJson), f, ensure_ascii=False, indent=4)
        
if __name__ == "__main__":
    isDebug = False
    jsonBeauty = False
    main()