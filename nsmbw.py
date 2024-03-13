"""
Entity data: 2 bytes
"""

from random import randint, shuffle
import globalVars
from copy import deepcopy

from struct import unpack, pack


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

    return returnList

# Generate definition dict for sections
def generateSectionDef(data):
    # All other attributes are useless. Only Data is useful
    # why did I code in that many attributes lol
    return {"Data":data}

def writeDef(binList):
    bytearr_h = b""
    bytearr_c = b""

    i = 0
    offsets = 112   #112 = Header size
    for lis_i in binList:
        #TODO MAKE COMPACTABLE WITH REGGIE LEVEL DESCRIPTION (ON TODO LIST)
        # Add header offset info
        bytearr_h += offsets.to_bytes(4,"big") + (len(lis_i["Data"])).to_bytes(4,"big")
        # Add the actual data
        bytearr_c += lis_i["Data"]
        offsets += (len(lis_i["Data"]))

    #bytearr = bytearr_h + bytearr_c
    bytearr = bytearr_h.ljust(111,b"\x00") + bytearr_c
    return bytearr

### Sprites Limit check ###
def findSpritesInArea(enData,enPosList):
    # Check if there are sprite within 100 blocks (square)
    return not (any(i_int[0] in range(enData[1]-50,enData[1]+50) for i_int in enPosList) and any(i_int[1] in range(enData[2]-50,enData[2]+50) for i_int in enPosList))

def isThwompAlwaysFalling(enData):
    if enData[3]==b"":
        return False
    return (int.from_bytes(enData[3],"big") & 131072)==131072 and (enData[0]==47 or enData[0]==48)
    # Using bitwise as we do not want to change the 4th "place"

def genPadding(num):
    returnPadding = b""
    for _ in range(1,num):
        returnPadding += b"\x00"
    return returnPadding

def checkNonEnterableEntrance(entdata):
    REROLL_LIST = [0,1,7,8,9,10]
    #           Contains 0x80?          destination not set?
    re_bool = (entdata[9]&128)!=0 or (entdata[3]==0 and entdata[4]==0)
    return re_bool or (entdata[5] in REROLL_LIST)# or ((entdata[9]&128)==0 and entdata[5] in [20,24])

# Level tiles data
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
        for i_lis in tilesData[:-1]:
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
    # WIP, Only implemented this to fix problematic level
    def phraseByteData(byteData):
        i = 0
        returnList = []
        while i<=len(byteData):
            if byteData[0+i:2+i] != b"":
                returnList.append(byteData[0+i:32+i].strip(b"\x00"))
            i+=32
        assert len(returnList) == 4, str(returnList) + " is not length in 4" # Length must be 4
        return returnList
    
    def toByteData(tilesetData):
        byteArray = b""
        assert len(tilesetData)==4
        for tilesetName in tilesetData:
            tilesetName = tilesetName.ljust(32, b"\x00")
            byteArray += tilesetName
        return byteArray

# Section 1 Level Properties goes here if necessary
class NSMBWAreaProp:
    def phraseByteData(byteData):
        i = 0
        returnList = []
        while i<len(byteData):
            #print(byteData[0+i:2+i])
            returnList.append(
                [int.from_bytes(byteData[0+i:4+i],"big"), # Event A
                int.from_bytes(byteData[4+i:8+i],"big"),  # Event B
                int.from_bytes(byteData[8+i:10+i],"big"),  # Wrap Byte
                int.from_bytes(byteData[10+i:12+i],"big"),  # Time Limit
                bool(byteData[12+i:13+i]),  # is Credit?
                int.from_bytes(byteData[13+i:14+i],"big"),  # unknown
                # 2 padding bytes
                int.from_bytes(byteData[16+i:17+i],"big"),  # Spawn Entrance ID
                bool(byteData[17+i:18+i]),  # is Ambush level?
                int.from_bytes(byteData[18+i:19+i],"big"),  # Toad House Flag
                # 1 padding byte
                ]
            )
            i+=20 #Entry length

        return returnList
    
    def toByteData(entranceData):
        byteData = b""
        for i_lis in entranceData:
            byteData += i_lis[0].to_bytes(4,"big")
            byteData += i_lis[1].to_bytes(4,"big")
            byteData += i_lis[2].to_bytes(2,"big")
            byteData += i_lis[3].to_bytes(2,"big")
            byteData += int(i_lis[4]).to_bytes(1,"big")
            byteData += i_lis[5].to_bytes(1,"big")
            byteData += b"\x00\x00"
            byteData += i_lis[6].to_bytes(1,"big")
            byteData += i_lis[7].to_bytes(1,"big")
            byteData += i_lis[8].to_bytes(1,"big")
            byteData += b"\x00"

        return byteData

class NSMBWZoneBound:
    def phraseByteData(byteData):
        i = 0
        returnList = []
        while i<len(byteData):
            #print(byteData[0+i:2+i])
            returnList.append(
                [int.from_bytes(byteData[0+i:4+i],"big"), # Cam Upper Bound
                int.from_bytes(byteData[4+i:8+i],"big"),  # Cam Lower Bound
                int.from_bytes(byteData[8+i:12+i],"big"),  # Cam Cloud Upper Bound
                int.from_bytes(byteData[12+i:16+i],"big"),  # Cam Cloud Lower Bound

                int.from_bytes(byteData[16+i:18+i],"big"),  # Entry ID
                int.from_bytes(byteData[18+i:20+i],"big"),  # Map Camera Zoom adjust
                int.from_bytes(byteData[20+i:22+i],"big"),  # Multiplayer Upper Bound
                int.from_bytes(byteData[22+i:24+i],"big"),  # Multiplayer Lower Bound
                ]
            )
            i+=24 #Entry length

        return returnList
    
    def toByteData(entranceData):
        byteData = b""
        for i_lis in entranceData:
            byteData += i_lis[0].to_bytes(4,"big")
            byteData += i_lis[1].to_bytes(4,"big")
            byteData += i_lis[2].to_bytes(4,"big")
            byteData += i_lis[3].to_bytes(4,"big")
            byteData += i_lis[4].to_bytes(2,"big")
            byteData += i_lis[5].to_bytes(2,"big")
            byteData += i_lis[6].to_bytes(2,"big")
            byteData += i_lis[7].to_bytes(2,"big")

        return byteData# + b"\xff\xff"
    
# Applies to both top and bottom background
class NSMBWZoneBG:
    def phraseByteData(byteData):
        i = 0
        returnList = []
        while i<len(byteData):
            returnList.append(
                [
                # 1 padding byte
                int.from_bytes(byteData[1+i:2+i],"big"),  # ID
                int.from_bytes(byteData[2+i:4+i],"big"),  # X Scroll rate
                int.from_bytes(byteData[4+i:6+i],"big"),  # Y Scroll rate
                int.from_bytes(byteData[6+i:8+i],"big"),  # Default Image Scroll Y Pos (inverted?)
                int.from_bytes(byteData[8+i:10+i],"big"),  # Default Image Scroll X Pos
                int.from_bytes(byteData[10+i:12+i],"big"),  # First background
                int.from_bytes(byteData[12+i:14+i],"big"),  # Middle background
                int.from_bytes(byteData[14+i:16+i],"big"),  # Last background
                # 3 Padding byte
                int.from_bytes(byteData[19+i:20+i],"big"),  # Zoom levels
                # 4 padding bytes
                ]
            )
            i+=24 #Entry length

        return returnList
    
    def toByteData(entranceData):
        byteData = b""
        for i_lis in entranceData:
            byteData += b"\x00"
            byteData += i_lis[0].to_bytes(1,"big")
            byteData += i_lis[1].to_bytes(2,"big")
            byteData += i_lis[2].to_bytes(2,"big")
            byteData += i_lis[3].to_bytes(2,"big")
            byteData += i_lis[4].to_bytes(2,"big")
            byteData += i_lis[5].to_bytes(2,"big")
            byteData += i_lis[6].to_bytes(2,"big")
            byteData += i_lis[7].to_bytes(2,"big")
            byteData += b"\x00\x00\x00"
            byteData += i_lis[8].to_bytes(1,"big")

        return byteData# + b"\xff\xff"

class NSMBWEntrances:
    def phraseByteData(byteData):
        i = 0
        returnList = []
        while i<len(byteData):
            #print(byteData[0+i:2+i])
            returnList.append(
                [int.from_bytes(byteData[0+i:2+i],"big"), #X
                int.from_bytes(byteData[2+i:4+i],"big"),  #Y
                # 5-7 Padding
                int.from_bytes(byteData[8+i:9+i],"big"),  #ID
                int.from_bytes(byteData[9+i:10+i],"big"),  #Dest ID (Area)
                int.from_bytes(byteData[10+i:11+i],"big"),  #Dest ID (Entrance)
                int.from_bytes(byteData[11+i:12+i],"big"),  #Type
                # 1 padding byte
                int.from_bytes(byteData[13+i:14+i],"big"),  #Zone ID?
                int.from_bytes(byteData[14+i:15+i],"big"),  #Layer
                int.from_bytes(byteData[15+i:16+i],"big"),  #Path
                int.from_bytes(byteData[16+i:18+i],"big"),  #Settings Bytes (e.g. Enterable, Spawn half a tile, etc.)
                int.from_bytes(byteData[18+i:19+i],"big"),  #Sends to World Map Bool
                int.from_bytes(byteData[19+i:20+i],"big"),  #?
                ]
            )
            i+=20 #Entry length

        return returnList
    def toByteData(entranceData):
        byteData = b""
        for i_lis in entranceData:
            byteData += i_lis[0].to_bytes(2,"big")
            byteData += i_lis[1].to_bytes(2,"big")
            byteData += b"\x00\x00\x00\x00"
            byteData += i_lis[2].to_bytes(1,"big")
            byteData += i_lis[3].to_bytes(1,"big")
            byteData += i_lis[4].to_bytes(1,"big")
            byteData += i_lis[5].to_bytes(1,"big")
            byteData += b"\x00"
            byteData += i_lis[6].to_bytes(1,"big")
            byteData += i_lis[7].to_bytes(1,"big")
            byteData += i_lis[8].to_bytes(1,"big")
            byteData += i_lis[9].to_bytes(2,"big")
            byteData += i_lis[10].to_bytes(1,"big")
            byteData += i_lis[11].to_bytes(1,"big")

        return byteData# + b"\xff\xff"
    
    ############### RANDO #################
    
    #Possible code optimisation: lvlName to lvlType (Number)
    def processEntrances(_entData,olvlName,curArea):
        entData = deepcopy(_entData)

        # Randomise Starting point (Area 1 only)
        if curArea==1:
            start_rand = randint(0,len(entData)-1)
            dum = entData[start_rand][2]
            entData[start_rand][2] = entData[0][2]
            entData[0][2] = dum

        # Randomise rest of entrances
        
        tmp_dest_list = []
        tmp_nonshuffle_list = []

        for i in range(0,len(entData)):
            i_dat = entData[i]
            if checkNonEnterableEntrance(i_dat) or ("24" in olvlName and i_dat[2]==3): # If it cannot be entered
                tmp_nonshuffle_list.append((i,i_dat))
            else:
                # Only replaces the Entrance ID and Destination ID ********* (i_dat[3],i_dat[4])
                tmp_dest_list.append(i_dat)

        shuffle(tmp_dest_list)
        
        for i_dat in tmp_nonshuffle_list:
            tmp_dest_list.insert(i_dat[0],i_dat[1])

        # Change back to the oirginal destination after ID swap
        for i in range(len(tmp_dest_list)): #TODO bugged here for duplicate destnation entrance
            tmp_dest_list[i][3] = _entData[i][3]
            tmp_dest_list[i][4] = _entData[i][4]

        entData = tmp_dest_list[:]

        return entData

class NSMBWLoadSprite:
    def __init__(self):
        pass

    def phraseByteData(byteData):
        i = 0
        returnList = []
        while i<=len(byteData):
            if byteData[0+i:2+i] != b"":
                returnList.append(int.from_bytes(byteData[0+i:2+i],"big"))
            i+=4
        return returnList

    def toByteData(sprList,orgLen):
        i = 0
        returnByte = b""
        for ID in sprList:
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
        while i<len(byteData)-4:
            returnList.append(
                [int.from_bytes(byteData[0+i:2+i],"big"), #ID
                int.from_bytes(byteData[2+i:4+i],"big"),  #X
                int.from_bytes(byteData[4+i:6+i],"big"),  #Y
                byteData[6+i:12+i],                        #Properties
                int.from_bytes(byteData[12+i:13+i],"big"), #Zone ID
                byteData[13+i:14+i] #an extra byte data?
                ]
            )
            i+=16
        
        return returnList
    
    def toByteData(sprList,orgLen=0):
        # TODO orgLen does nothing atm
        returnByte = b""
        for ID,x,y,prop,zone,extraByte in sprList:
            if len(prop)==6:
                returnByte += (ID).to_bytes(2,"big")+(x).to_bytes(2,"big")+(y).to_bytes(2,"big")+prop+(zone).to_bytes(1,"big")+extraByte+b"\x00\x00"
            else:
                #print("WARNING: properties not in 6 bytes for object",ID)
                orgLen -=16
                
        
        returnByte += b"\xff\xff\xff\xff"

        #TODO Fill in some padding data to match the orginal data length.
        #while len(returnByte)<orgLen:
        #    returnByte += b"\x00"
        return returnByte

    ################## RANDO ####################
    def processSprites(eData,leData,lvName):
        reData = deepcopy(eData)
        relData = []#deepcopy(leData)

        posList = []
        
        #print("=========== " + lvName)

        for enemyData in reData:
            randomised = False
            #Randomize enemy
            for eLis in globalVars.enemyList:
                if enemyData[0] in eLis: # Enemy in the list
                    posList.append((enemyData[1],enemyData[2]))
                    enemyData[0] = eLis[randint(0,len(eLis)-1)] #randomize
                    # Sprite Limit check, kinda buggy but I will let it slide for the time being
                    if (findSpritesInArea(enemyData,posList) or randint(0,2)==1) and (globalVars.reduceLag):
                        try:
                            del reData[reData.index(enemyData)]
                            continue
                        except ValueError:
                            print("WARNING: Cannot remove sprite",enemyData)
                    else:
                        if enemyData[0] not in globalVars.SKIP_SPRITES:
                            enemyData[3] = b"\x00\x00\x00\x00\x00\x00" #Reset enemy state to default

            #Randomize enemy variation
            if str(enemyData[0]) in globalVars.enemyVarList:
                varList = globalVars.enemyVarList[str(enemyData[0])]
                enemyData[3] = bytes.fromhex(varList[randint(0,len(varList)-1)])

            if enemyData[0] not in relData: #Add to the sprite loading list
                relData.append(enemyData[0])
            
        del reData[-1] # This is the most hacky way to fix a bug but it works.

        return reData,relData,len(reData)*16

class NSMBWZones:
    def __init__(self):
        pass
    def phraseByteData(byteData):
        i = 0
        returnList = []
        while i<len(byteData):
            #print(byteData[0+i:2+i])
            returnList.append(
                [int.from_bytes(byteData[0+i:2+i],"big"), #X
                int.from_bytes(byteData[2+i:4+i],"big"),  #Y
                int.from_bytes(byteData[4+i:6+i],"big"),  #Width
                int.from_bytes(byteData[6+i:8+i],"big"),  #Height
                int.from_bytes(byteData[8+i:10+i],"big"),  #Zone theme
                int.from_bytes(byteData[10+i:12+i],"big"),  #Terrain Lighting theme

                int.from_bytes(byteData[12+i:13+i],"big"),  #Zone ID
                int.from_bytes(byteData[13+i:14+i],"big"),  #Zone bound settings?
                int.from_bytes(byteData[14+i:15+i],"big"),  #Camera Mode
                int.from_bytes(byteData[15+i:16+i],"big"),  #Camera Zoom Level
                # 1 padding byte
                int.from_bytes(byteData[17+i:18+i],"big"),  #Darkness effect type
                int.from_bytes(byteData[18+i:19+i],"big"),  #Top background (ref section 3)
                int.from_bytes(byteData[19+i:20+i],"big"),  #Bottom background (ref section 4)
                int.from_bytes(byteData[20+i:21+i],"big"),  #Autoscroll track path ID
                # 2 padding bytes
                int.from_bytes(byteData[23+i:24+i],"big"),  #Music ID
                int.from_bytes(byteData[24+i:25+i],"big"),  #Sound effects
                ]
            )
            i+=25 #Entry length

        return returnList
    def toByteData(entranceData):
        byteData = b""
        for i_lis in entranceData:
            byteData += i_lis[0].to_bytes(2,"big")
            byteData += i_lis[1].to_bytes(2,"big")
            byteData += i_lis[2].to_bytes(2,"big")
            byteData += i_lis[3].to_bytes(2,"big")
            byteData += i_lis[4].to_bytes(2,"big")
            byteData += i_lis[5].to_bytes(2,"big")
            byteData += i_lis[6].to_bytes(1,"big")
            byteData += i_lis[7].to_bytes(1,"big")
            byteData += i_lis[8].to_bytes(1,"big")
            byteData += i_lis[9].to_bytes(1,"big")
            # 1 padding byte
            byteData += i_lis[10].to_bytes(1,"big")
            byteData += i_lis[11].to_bytes(1,"big")
            byteData += i_lis[12].to_bytes(1,"big")
            byteData += i_lis[13].to_bytes(1,"big")
            # 2 padding bytes
            byteData += i_lis[14].to_bytes(1,"big")
            byteData += i_lis[15].to_bytes(1,"big")

        return byteData
    
class NSMBWLocations:
    def phraseByteData(byteData):
        i = 0
        returnList = []
        while i<len(byteData):
            #print(byteData[0+i:2+i])
            returnList.append(
                [
                # 1 padding byte
                int.from_bytes(byteData[1+i:2+i],"big"),  # X
                int.from_bytes(byteData[2+i:3+i],"big"),  # Y
                int.from_bytes(byteData[3+i:4+i],"big"),  # Width
                int.from_bytes(byteData[4+i:5+i],"big"),  # Height
                int.from_bytes(byteData[5+i:6+i],"big"),  # ID
                # 3 Padding byte
                ]
            )
            i+=11 #Entry length

        return returnList
    
    def toByteData(entranceData):
        byteData = b""
        for i_lis in entranceData:
            byteData += b"\x00"
            byteData += i_lis[0].to_bytes(2,"big")
            byteData += i_lis[1].to_bytes(2,"big")
            byteData += i_lis[2].to_bytes(2,"big")
            byteData += i_lis[3].to_bytes(2,"big")
            byteData += i_lis[4].to_bytes(2,"big")
            byteData += b"\x00\x00\x00"

        return byteData

class NSMBWCamProfile: #TODO Untested
    def phraseByteData(byteData):
        i = 0
        returnList = []
        while i<len(byteData):
            #print(byteData[0+i:2+i])
            returnList.append(
                [
                # 11 padding byte
                int.from_bytes(byteData[12+i:13+i],"big"),  # Movement type
                int.from_bytes(byteData[13+i:14+i],"big"),  # Zoom Scale
                int.from_bytes(byteData[14+i:15+i],"big"),  # ???
                # 2 Padding byte
                int.from_bytes(byteData[18+i:19+i],"big"),  # Event ID
                ]
            )
            i+=11 #Entry length

        return returnList
    
    def toByteData(entranceData):
        byteData = b""
        for i_lis in entranceData:
            byteData += b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
            byteData += i_lis[0].to_bytes(1,"big")
            byteData += i_lis[1].to_bytes(1,"big")
            byteData += i_lis[2].to_bytes(1,"big")
            byteData += b"\x00\x00"
            byteData += i_lis[3].to_bytes(1,"big")

        return byteData
    
class NSMBWPathProperties:
    def phraseByteData(byteData:list):
        i = 0
        returnList = []
        while i<len(byteData):
            #print(byteData[0+i:2+i])
            returnList.append(
                [
                int.from_bytes(byteData[0+i:1+i],"big"),  # Path ID
                # 1 padding byte
                int.from_bytes(byteData[2+i:4+i],"big"),  # Starting path node ID
                int.from_bytes(byteData[4+i:6+i],"big"),  # Number of nodes
                int.from_bytes(byteData[6+i:8+i],"big"),  # Path loops?
                ]
            )
            i+=8 #Entry length

        return returnList
    
    def toByteData(entranceData:list):
        byteData = b""
        for i_lis in entranceData:
            if i_lis == []:
                continue
            byteData += i_lis[0].to_bytes(1,"big")
            byteData += b"\x00"
            byteData += i_lis[1].to_bytes(2,"big")
            byteData += i_lis[2].to_bytes(2,"big")
            byteData += i_lis[3].to_bytes(2,"big")

        return byteData
    
class NSMBWPathNode: #TODO Untested
    def phraseByteData(byteData:list):
        i = 0
        returnList = []
        while i<len(byteData):
            # due to struct being the only way vanilla python can read byte array to float, here is the struct
            returnList_item = unpack(">HHffhxx",byteData[i:i+16])
            returnList.append(returnList_item)
            
            i+=16 #Entry length

        return returnList
    
    def toByteData(entranceData):
        byteData = b""
        for i_lis in entranceData:
            print(i_lis)
            byteData += pack(">HHffhxx",*i_lis)

        return byteData