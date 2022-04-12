"""
Entity data: 2 bytes
"""


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
    
    def phraseByteData(byteData):
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
                print("WARNING: properties not in 8 bytes for object",ID)
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
                    if not (any(i_int[0] in range(enemyData[1]-50,enemyData[1]+50) for i_int in posList) and any(i_int[1] in range(enemyData[2]-50,enemyData[2]+50) for i_int in posList)):
                        #print("pass")
                        posList.append((enemyData[1],enemyData[2]))
                        enemyData[0] = eLis[randint(0,len(eLis)-1)] #randomize
                        if enemyData[0] not in relData: #Add to the sprite loading list
                            relData.append(enemyData[0])
                    else:
                        del reData[reData.index(enemyData)]
                        #print("Too many sprites! Sprite", enemyData[0], "will be deleted in",lvName)
        #print(len(reData)*16)
        return reData,relData,len(reData)*16




