### THIS IS A TEST SCRIPT TO TEST THE OUTPUTTED JSON CAN BE ASSEMBLED INTO A PROPER LEVEL.
### IT SHOULD BE USED FOR TESTING ONLY

import json
from os import listdir

import u8_m
import nsmbw
import globalVars
from Util import tilePosToObjPos, convertToDict

inJson = {}
levelToImport = "01-01.arc"

tileData = [[],[],[]]
u8_files_list = []

isDebug = False

def main():
    global inJson
    with open('out.json', 'r') as f:
        json_orginal = json.load(f)
    inJson = convertToDict(json_orginal)

    # Test zone data is working:
    print(inJson[levelToImport].keys())
    for areaNo in inJson[levelToImport].keys():
        #area = inJson[levelToImport][areaNo]
        area = inJson[levelToImport][areaNo]["0"] # Temp. replace ["0"] with the desired zone number
        areaRawSettings = []
        # Import settings one-by-one, in order from Section 0
        areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWtileset.toByteData(area["tileset"])))
        areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWAreaProp.toByteData(area["AreaSetting"])))
        areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWZoneBound.toByteData(area["ZoneBound"])))
        areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWZoneBG.toByteData(area["topBackground"])))
        areaRawSettings.append(nsmbw.generateSectionDef(area["AreaSetting2"]))
        areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWZoneBG.toByteData(area["bottomBackground"])))
        areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWEntrances.toByteData(area["entrance"])))
        areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWsprite.toByteData(area["sprites"])))
        areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWZones.toByteData([area["zone"]])))
        areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWLocations.toByteData(area["location"])))
        areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWCamProfile.toByteData(area["cameraProfile"])))
        areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWPathProperties.toByteData(area["path"])))
        areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWPathNode.toByteData(area["pathNode"])))
        
        # Write it to byte array
        u8_files_list.append(u8_m.constructArchiveFile_m("course" + areaNo + ".bin",nsmbw.writeDef(areaRawSettings)))

        #print("KEYS",area.keys())
        # Add tiles data
        for i in range(0,2): # Loop through each areas
            if "bgdatL"+str(i) in area.keys():
                #print("in area")
                for tiles in area["bgdatL" + str(i)]:
                    tileData[i].append(tiles)
                # Convert to byte data
                u8_files_list.append(u8_m.constructArchiveFile_m("course" + areaNo + "_bgdatL" + str(i) + ".bin",nsmbw.NSMBWbgDat.toByteData(tileData[i])))
        # TODO Output the file as a U8 archive
                
    # Create "course" folder
    u8_files_dir = u8_m.constructArchiveFile_m("course",b"",True,len(u8_files_list))
    u8_dict = u8_m.constructFromScratch(len(inJson[levelToImport].keys()),[u8_files_dir] + u8_files_list)
    #print(u8_dict)
    returnARC = u8_m.repackToBytes(u8_dict)
    with open('test_json.arc', 'wb') as f:
        f.write(returnARC)

    if isDebug:
        de_f = u8_m.openFile("test_json.arc")
        de_f["Raw Data"] = b""
        print(de_f["File Name List"])
        
    pass

if __name__=="__main__":
    isDebug = True
    main()