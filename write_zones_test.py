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

def main():
    global inJson
    with open('out.json', 'r') as f:
        json_orginal = json.load(f)
    inJson = convertToDict(json_orginal)

    # Test zone data is working:
    print(inJson[levelToImport].keys())
    for areaNo in inJson[levelToImport].keys():
        area = inJson[levelToImport][areaNo]
        
    pass

if __name__=="__main__":
    main()