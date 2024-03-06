import json
from os import listdir

import u8_m
import nsmbw

def readRandoRule():
    # rf = open("config.json")
    # rulesDict = json.loads(rf.read())
    # rf.close()

    for filename in listdir("./Stage"):
        u8list = u8_m.openFile("Stage/" + filename)
        u8FileList = u8list["File Name List"]
        areaNo = u8list["Number of area"]
        areaNo %= 4
        if areaNo==0:
            areaNo = 4
        #print("AreaNo",areaNo,istr,newName)
        
        #Loop through every area
        for i in range(1,areaNo+1):
            lvlSetting = nsmbw.readDef(u8list["course"+ str(i) +".bin"]["Data"])
            #u8list = readAndrandomise(i,istr,u8list)
            



def main():
    pass

if __name__ == "__main__":
    main()