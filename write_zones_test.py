### THIS IS A TEST SCRIPT TO TEST THE OUTPUTTED JSON CAN BE ASSEMBLED INTO A PROPER LEVEL.
### IT SHOULD BE USED FOR TESTING ONLY

import json
from os import listdir

import u8_m
import nsmbw
import globalVars
from Util import tilePosToObjPos, convertToDict

inJson = {}
# levelToImport = "Stage/05-36.arc"
levelToImport = input("Level name: ")
json_inp_filename = "out_debug.json" if input("Debug? (y/n): ")=="y" else "out.json"

tileData = [[],[],[]]
u8_files_list = []

isDebug = False

def importZone(areaNo,zoneNo):
    area = inJson[levelToImport][areaNo][zoneNo] # NOTE Temp. replace ["0"] with the desired zone number
    areaRawSettings = []
    # Prepare for Sprite loading list
    loadSprList = nsmbw.NSMBWLoadSprite.addLoadSprites(area["sprites"])
    # Import settings one-by-one, in order from Section 0
    areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWtileset.toByteData(area["tileset"])))
    areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWAreaProp.toByteData(area["AreaSetting"])))
    areaRawSettings.append(nsmbw.generateSectionDef(area["ZoneBound"])) # TODO Convert this to list if needed
    #print(area["ZoneBound"],nsmbw.NSMBWZoneBound.toByteData(area["ZoneBound"]))
    areaRawSettings.append(nsmbw.generateSectionDef(area["AreaSetting2"]))
    areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWZoneBG.toByteData(area["topBackground"])))
    areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWZoneBG.toByteData(area["bottomBackground"])))
    areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWEntrances.toByteData(area["entrance"])))
    areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWsprite.toByteData(area["sprites"])))
    areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWLoadSprite.toByteData(loadSprList)))
    areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWZones.toByteData([area["zone"]])))
    areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWLocations.toByteData(area["location"])))
    areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWCamProfile.toByteData(area["cameraProfile"])))
    areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWPathProperties.toByteData(area["path"])))
    areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWPathNode.toByteData(area["pathNode"])))
            
    # Write it to byte array
    u8_files_list.append(u8_m.constructArchiveFile_m("course" + "1" + ".bin",nsmbw.writeDef(areaRawSettings)))

    # Add tiles data
    for i in range(0,2): # Loop through each layer
        if "bgdatL"+str(i) in area.keys():
            for tiles in area["bgdatL" + str(i)]:
                tileData[i].append(tiles)
            # Convert to byte data
            u8_files_list.append(u8_m.constructArchiveFile_m("course" + "1" + "_bgdatL" + str(i) + ".bin",nsmbw.NSMBWbgDat.toByteData(tileData[i])))
            # TODO Output the file as a U8 archive
            if isDebug:
                with open("course" + "1" + "_bgdatL" + str(i) + ".bin", 'wb') as f:
                    f.write(nsmbw.NSMBWbgDat.toByteData(tileData[i]))

def main():
    global inJson
    with open(json_inp_filename, 'r') as f:
        json_orginal = json.load(f)
    inJson = convertToDict(json_orginal)

    sec_import = input("Area to import (1,2,3,4)(Other = all): ")

    if sec_import not in ("1","2","3","4"):
        # Test zone data is working:
        for areaNo in inJson[levelToImport].keys():
            print("AREA",areaNo)
            #area = inJson[levelToImport][areaNo]
            for zoneNo in inJson[levelToImport][areaNo].keys():
                print("Zone",zoneNo)
                importZone(areaNo,zoneNo)
    else:
        print("Available zones: " + ", ".join(inJson[levelToImport][sec_import].keys()))
        zone_no_import = input("Zone to import: ")
        importZone(sec_import,zone_no_import)
                
    # Create "course" folder
    u8_files_dir = u8_m.constructArchiveFile_m("course",b"",True,len(u8_files_list)+2) # +2 for itself + root folder
    # Create u8_m dict for repacking
    u8_dict = u8_m.constructFromScratch(len(inJson[levelToImport].keys()),[u8_files_dir] + u8_files_list)

    returnARC = u8_m.repackToBytes(u8_dict)
    with open("test_" + levelToImport + ".arc", 'wb') as f:
        f.write(returnARC)
        print("Test level written to " + "test_" + levelToImport + ".arc")

    # if isDebug:
    #     de_f = u8_m.openFile("test_json.arc")
    #     de_f["Raw Data"] = b""
    #     print(de_f["File Name List"])
        
    pass

if __name__=="__main__":
    isDebug = True
    main()