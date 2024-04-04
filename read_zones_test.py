##### FILE FOR TESTING ONLY. NEW FILE WILL BE CREATED FOR ACTUAL USE #####

import json
from os import listdir

import u8_m
import nsmbw
import globalVars
from Util import tilePosToObjPos, convertToJson

outJson = dict()
lvlSetting_arr = []

tileset = []
areaSetting = []
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
    for i in range(0,len(zoneData)):
        zoneDat = zoneData[i]
        if checkPosInSpecificZone(zoneDat,sprPos,width,height):
            return zoneDat[6]
    return -1

def checkPosInSpecificZone(zoneDat, sprPos, width=0, height=0) -> int: # May also incoperate with the function above?
    # for every zone, Check X pos, then Y pos
    #print("POS",zoneDat[1]+zoneDat[3]+16,sprPos[1])
    #              Min X                       Max X = min x + width
    return sprPos[0]+width>=(zoneDat[0]-16) and sprPos[0]<=(zoneDat[0]+zoneDat[2]+16)\
        and sprPos[1]+height>=(zoneDat[1]-16) and sprPos[1]<=(zoneDat[1]+zoneDat[3]+16)


def readAllSettings(raw_setting):
    # The function name lied. Only nessary settings will be read and stored.
    # Inseerted global here since IDK when the variable will disfunction like a local variable
    global tileset, areaSetting, zoneBound, topBackground, bottomBackground, entrances, spriteData, sprLoadData, zoneData, locData, camProfile, pathProp, pathNode
    # TODO Add phrasing function to the following sections

    # Section 0
    tileset = nsmbw.NSMBWtileset.phraseByteData(raw_setting[0]["Data"])
    # Section 1
    areaSetting = nsmbw.NSMBWAreaProp.phraseByteData(raw_setting[1]["Data"])
    # Section 2
    zoneBound = nsmbw.NSMBWZoneBound.phraseByteData(raw_setting[2]["Data"])
    # zoneBound = raw_setting[2]["Data"] # Apperantly Python struct don't like long val stored in JSON sooo... Raw data it is
    # Section 4
    topBackground = nsmbw.NSMBWZoneBG.phraseByteData(raw_setting[4]["Data"])
    # Section 5
    bottomBackground = nsmbw.NSMBWZoneBG.phraseByteData(raw_setting[5]["Data"])
    # Phrase Entrance Info (Section 6)
    entrances = nsmbw.NSMBWEntrances.phraseByteData(raw_setting[6]["Data"])
    # Sprite Handling (Section 7,8)
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
        print("============================")
        print("TILESET",len(tileset))
        print("AREASET",areaSetting)
        print("ZONEBND",zoneBound)
        print("TOP  BG",topBackground)
        print("ENTDATA",entrances)
        print("ZONEDAT",zoneData)
        print("LOCDATA",locData)
        print("CAMPROF",camProfile)
        print("PATHPRO",pathProp)
        print("PATHNOD",pathNode)
        print("-----------------")
        raw_setting[0]["Data"] = nsmbw.NSMBWtileset.toByteData(tileset)
        raw_setting[1]["Data"] = nsmbw.NSMBWAreaProp.toByteData(areaSetting)
        raw_setting[2]["Data"] = raw_setting[2]["Data"]
        raw_setting[4]["Data"] = nsmbw.NSMBWZoneBG.toByteData(topBackground)
        raw_setting[9]["Data"] = nsmbw.NSMBWZones.toByteData(zoneData)
        raw_setting[10]["Data"] = nsmbw.NSMBWLocations.toByteData(locData)
        raw_setting[11]["Data"] = nsmbw.NSMBWCamProfile.toByteData(camProfile)
        raw_setting[12]["Data"] = nsmbw.NSMBWPathProperties.toByteData(pathProp)
        raw_setting[13]["Data"] = nsmbw.NSMBWPathNode.toByteData(pathNode)
        raw_setting = nsmbw.readDef(nsmbw.writeDef(raw_setting))
        print("TILESET",nsmbw.NSMBWtileset.phraseByteData(raw_setting[0]["Data"]))
        print("AREASET",nsmbw.NSMBWAreaProp.phraseByteData(raw_setting[1]["Data"]))
        print("ZONEBND",nsmbw.NSMBWZoneBound.phraseByteData(raw_setting[2]["Data"]))
        print("TOP  BG",nsmbw.NSMBWZoneBG.phraseByteData(raw_setting[4]["Data"]))
        print("ZONEDAT",nsmbw.NSMBWZones.phraseByteData(raw_setting[9]["Data"]))
        print("LOCDATA",nsmbw.NSMBWLocations.phraseByteData(raw_setting[10]["Data"]))
        print("CAMPROF",nsmbw.NSMBWCamProfile.phraseByteData(raw_setting[11]["Data"]))
        print("PATHPRO",nsmbw.NSMBWPathProperties.phraseByteData(raw_setting[12]["Data"]))
        print("PATHNOD",nsmbw.NSMBWPathNode.phraseByteData(raw_setting[13]["Data"]))

def main():
    global lvlSetting_arr
    # rf = open("config.json")
    # rulesDict = json.loads(rf.read())
    # rf.close()

    filename = "Stage/02-04.arc"
    outJson[filename] = {}
    
    print(filename)
    u8list = u8_m.openFile(filename)
    u8FileList = u8list["File Name List"]
    areaNo = u8list["Number of area"]
    #print("AREANO",areaNo)
    areaNo %= 4
    if areaNo==0:
        areaNo = 4
    
    lvlSetting_arr = []
    #print(u8list["course1.bin"],u8list["File Name List"])
    #Loop through every area
    for i in range(1,areaNo+1):
        print("\nREADING AREA",i,"of",areaNo)
        lvlSetting_raw = nsmbw.readDef(u8list["course"+ str(i) +".bin"]["Data"])
        readAllSettings(lvlSetting_raw)
        outJson[filename][i] = {}
        # add zone to the output json
        for zone in zoneData:
            print("ZONE NUMBER",zone[6],zone)
            # Preprocess zone bound due to llong val
            zoneBnd = [zoneB for zoneB in zoneBound if zoneB[4] == zone[7]]
            outJson[filename][i][zone[6]] = {
                "tileset" : tileset,
                "AreaSetting" : areaSetting,
                "ZoneBound" : nsmbw.NSMBWZoneBound.toByteData(zoneBound),
                "topBackground" : [topBg for topBg in topBackground if topBg[0] == zone[11]],
                "AreaSetting2" : lvlSetting_raw[3]["Data"], # They aren't that useful atm so I will leave them just as is
                "bottomBackground" : [bottomBg for bottomBg in bottomBackground if bottomBg[0] == zone[12]],
                "entrance" : [ent for ent in entrances if checkPosInSpecificZone(zone,(ent[0],ent[1]))],
                "sprites" : [spr for spr in spriteData if checkPosInSpecificZone(zone,(spr[1],spr[2]))],
                "zone" : zone,
                "location" : [loc for loc in locData if checkPosInSpecificZone(zone,(loc[0],loc[1]))],
                "cameraProfile" : camProfile,
                #"path" : [path for path in pathProp if checkPosInSpecificZone(zone,(node[0],node[1]))],
                "pathNode" : [node for node in pathNode if checkPosInSpecificZone(zone,(node[0],node[1]))]
            }
            # Path
            outJson[filename][i][zone[6]]["path"] = [path for path in pathProp if pathNode[path[1]] in outJson[filename][i][zone[6]]["pathNode"]]
            # print(outJson[filename][i][zone[6]]["path"])
        # Read tiles
        for j in range(0,2): #Loop through every layers
            #print(u8list.keys(),"course"+ str(i) +"_bgdatL" + str(j) + ".bin")
            #print("course"+ str(i) +"_bgdatL" + str(j) + ".bin")
            if ("course"+ str(i) +"_bgdatL" + str(j) + ".bin") in u8list.keys(): # if layer (j) exist
                # Get tiles info
                globalVars.tilesData[j] = nsmbw.NSMBWbgDat.phraseByteData(u8list["course"+ str(i) +"_bgdatL" + str(j) + ".bin"]["Data"])
                #print(globalVars.tilesData[j])
                for tile in globalVars.tilesData[j]:
                    # Zones are in sprite coordinate system
                    #print(tile,tilePosToObjPos((tile[1],tile[2])),zoneData)
                    zoneNo = checkPosInZone(zoneData,tilePosToObjPos((tile[1],tile[2])),*tilePosToObjPos((tile[3],tile[4])))
                    #print(zoneNo)
                    if zoneNo!=-1:
                        #print(i,j,outJson[filename][i].keys())
                        if "bgdatL" + str(j) not in outJson[filename][i][zoneNo]:
                            outJson[filename][i][zoneNo]["bgdatL" + str(j)] = []
                        outJson[filename][i][zoneNo]["bgdatL" + str(j)].append(tile)
        #print("END OF AREA")
    
    #print(outJson["01-01.arc"][1][0]["bgdatL1"])
    
    with open('out_debug.json', 'w', encoding='utf-8') as f:
        if not jsonBeauty:
            json.dump(convertToJson(outJson), f)
        else:
            json.dump(convertToJson(outJson), f, ensure_ascii=False, indent=4)
        
if __name__ == "__main__":
    isDebug = True
    jsonBeauty = True
    main()