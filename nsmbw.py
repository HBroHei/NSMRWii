"""
Entity data: 2 bytes
"""


from email.encoders import encode_noop
from random import randint
import globalVars


BinfileName = "Stage/Extract/course/course1_bgdatL1.bin"
BinfileName = "Stage/Extract/course/course1.bin"

erList = []


### OPEN FILE ###
"""bfile = open(BinfileName,"rb")
byteFile = bfile.read()
bfile.close()
print(byteFile)"""

def readDef(byteData):
    #print("Reading course data")

    offset={}
    size={}
    data = {}
    returnList = []
    
    ### READ DATA OFFSET ###
    for i_dum in range(0,14):
        i = i_dum*8
        offset[i_dum] = int.from_bytes(byteData[i:i+4],"big")
        size[i_dum] = int.from_bytes(byteData[i+4:i+8],"big")
        data[i_dum] = byteData[offset[i_dum]:offset[i_dum]+size[i_dum]]
        returnList.append({
            "Order":i_dum,
            "Offset":offset[i_dum],
            "Size":size[i_dum],
            "Data":data[i_dum]
        })
        #print(i,offset[i],size[i])

    return returnList
    
    ### ENTRANCE HANDLING ###

def writeDef(binList):
    bytearr_h = b""
    bytearr_c = b""

    i = 0
    offsets = 112   #112 = Header size
    for lis_i in binList:
        #TODO MAKE COMPACTABLE WITH REGGIE LEVEL DESCRIPTION (ON TODO LIST)
        bytearr_h += offsets.to_bytes(4,"big") + (len(lis_i["Data"])).to_bytes(4,"big")
        bytearr_c += lis_i["Data"]
        offsets += (len(lis_i["Data"]))

    bytearr = bytearr_h + bytearr_c
    return bytearr

### Sprites Limit check ###
def findSpritesInArea(enData,enPosList):
    #print("Endata",enData)
    return not (any(i_int[0] in range(enData[1]-50,enData[1]+50) for i_int in enPosList) and any(i_int[1] in range(enData[2]-50,enData[2]+50) for i_int in enPosList))

def isThwompAlwaysFalling(enData):
    if enData[3]==b"":
        return False
    return (int.from_bytes(enData[3],"big") & 131072)==131072 and (enData[0]==47 or enData[0]==48)
    # Using bitwise as we do not want to change the 4th "place"

class NSMBWbgDat:
    def phraseByteData(byteData):
        tilesData = []
        i = 0
        while i<=len(byteData)-2: #The last 2 bytes is always FFFF
            tileData = []
            tileData.append(int.from_bytes(byteData[i:i+2],"big"))
            tileData.append(int.from_bytes(byteData[i+2:i+4],"big"))
            tileData.append(int.from_bytes(byteData[i+4:i+6],"big"))
            tileData.append(int.from_bytes(byteData[i+6:i+8],"big"))
            tileData.append(int.from_bytes(byteData[i+8:i+10],"big"))
            tilesData.append(tileData)
            i += 10
        return list(filter(None,tilesData))
    
    def toByteData(tilesData):
        byteData = b""
        for i_lis in tilesData[:-2]:
            for int_val in i_lis:
                byteData += int_val.to_bytes(2,"big")

        return byteData + b"\xff\xff"
    ############## RANDO ###############
    def processTiles(tData):
        reData = tData
        
        for tilesData in reData:
            for tLis in globalVars.tileGroup:
                if tilesData[0] in tLis: # Tile in the group
                    tilesData[0] = tLis[randint(0,len(tLis)-1)] #randomize
        return reData
            

class NSMBWtileset:
    #Only implemented this to fix problematic level
    def phraseByteData(byteData):
        i = 0
        returnList = []
        while i<=len(byteData):
            #print(byteData[0+i:2+i])
            if byteData[0+i:2+i] != b"":
                #print("".join(list(filter(lambda l: l!=b"\x00",byteData[0+i:32+i]))))
                returnList.append(byteData[0+i:32+i].strip(b"\x00"))
            i+=32
        return returnList


class NSMBWLoadSprite:
    def __init__(self):
        pass

    def phraseByteData(byteData):
        i = 0
        returnList = []
        while i<=len(byteData):
            #print(byteData[0+i:2+i])
            if byteData[0+i:2+i] != b"":
                returnList.append(int.from_bytes(byteData[0+i:2+i],"big"))
            i+=4
            #print(returnList[-1])
        return returnList

    def toByteData(sprList,orgLen):
        i = 0
        returnByte = b""
        for ID in sprList:
            #print(ID)
            returnByte += ID.to_bytes(2,"big") + b"\x00\x00"

        #Fill in some padding data to match the orginal data length.
        #while len(returnByte)<orgLen:
        #    returnByte += b"\x00"
        return returnByte



class NSMBWsprite:
    def __init__(self,ID=None,x=None,y=None,prop=None):
        self.ID = ID
        self.x = x
        self.y = y
        self.prop = prop
    
    def phraseByteData(byteData): #TODO UNTESTED, NEED TO DEBUG
        i = 0
        returnList = []
        while i<=len(byteData):
            #print(byteData[0+i:2+i])
            returnList.append(
                [int.from_bytes(byteData[0+i:2+i],"big"), #ID
                int.from_bytes(byteData[2+i:4+i],"big"),  #X
                int.from_bytes(byteData[4+i:6+i],"big"),  #Y
                byteData[6+i:14+i]]                       #Properties
            )
            i+=16
        
        return returnList
    
    def toByteData(sprList,orgLen):
        returnByte = b""
        for ID,x,y,prop in sprList:
            #print(int(ID).to_bytes(2,"big")+int(x).to_bytes(2,"big")+int(y).to_bytes(2,"big")+prop+b"\x00\x00")
            #print(ID,x,y)
            if len(prop)==8:
                returnByte += (ID).to_bytes(2,"big")+(x).to_bytes(2,"big")+(y).to_bytes(2,"big")+prop+b"\x00\x00"
            else:
                #print("WARNING: properties not in 8 bytes for object",ID)
                orgLen -=16
        
        returnByte += b"\xff\xff\xff\xff"

        #TODO Fill in some padding data to match the orginal data length.
        while len(returnByte)<orgLen:
            returnByte += b"\x00"
        return returnByte

    ################## RANDO ####################
    def processSprites(eData,leData,lvName):
        reData = eData
        relData = leData

        posList = []
        
        for enemyData in reData:
            for eLis in globalVars.enemyList:
                if enemyData[0] in eLis: # Enemy in the list
                    # Sprite Limit check
                    #print(any(i_int[0] in range(enemyData[1]-50,enemyData[1]+50) for i_int in posList))
                    if (findSpritesInArea(enemyData,posList)) or (not globalVars.reduceLag):
                        #print("pass")
                        posList.append((enemyData[1],enemyData[2]))
                        enemyData[0] = eLis[randint(0,len(eLis)-1)] #randomize
                        if enemyData[0] not in relData: #Add to the sprite loading list
                            relData.append(enemyData[0])
                    else:
                        del reData[reData.index(enemyData)]

                # TODO MAKE THIS A TOGGIBLE OPTION
                if isThwompAlwaysFalling(enemyData):
                    enemyData[3] = enemyData[3][:5] + (enemyData[3][5]-2).to_bytes(1,"big") + enemyData[3][6:]
                    #print("Thwomp_A",enemyData[3])

                    
        #print(len(reData)*16)
        return reData,relData,len(reData)*16




