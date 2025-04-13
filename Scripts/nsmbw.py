"""
Entity data: 2 bytes
"""

from random import randint, shuffle, random, randbytes, choice
import globalVars
from copy import deepcopy
from Util import changeBytesAt, hex_to_str, matches_pattern

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
        #            Data section offsets        Data section size
        bytearr_h += offsets.to_bytes(4,"big") + (len(lis_i["Data"])).to_bytes(4,"big")
        #print(i,offsets,(len(lis_i["Data"])))
        # Add the actual data
        bytearr_c += lis_i["Data"]
        offsets += (len(lis_i["Data"]))
        i+=1

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
        for i_lis in tilesData:
            if i_lis[0]>60000: continue
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
                bool(int.from_bytes(byteData[12+i:13+i],"big")),  # is Credit?
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
            returnList.append(unpack(">4lHHhh",byteData[i:i+24]))
            i+=24 #Entry length

        return returnList
    
    def toByteData(zoneBndData):
        byteData = b""
        for i_lis in zoneBndData:
            byteData += pack(">4lHHhh",*i_lis)

        return byteData# + b"\xff\xff"
    
# Applies to both top and bottom background
class NSMBWZoneBG:
    def phraseByteData(byteData):
        i = 0
        returnList = []
        while i<len(byteData):
            returnList.append(unpack(">xBhhhhHHHxxxBxxxx",byteData[i:i+24]))
            i+=24 #Entry length

        return returnList
    
    def toByteData(entranceData):
        byteData = b""
        for i_lis in entranceData:
            byteData += pack(">xBhhhhHHHxxxBxxxx",*i_lis)

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
        try:
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
        except OverflowError:
            print("ERROR: OVERFLOW FOR LIST",entranceData)
            exit()
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

    # Generate Load Sprite List based on sprites list
    def addLoadSprites(sprData):
        sprLoadList = set(spr[0] for spr in sprData)
        return list(sprLoadList)
            

    def toByteData(sprList):
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
    
    # Function to replace org_item with replacement, retaining original values for 'x'
    def replace_varient(org_item, replacement):
        hex_str = hex_to_str(org_item)
        new_hex = []
        hex_str_clean = hex_str.replace(' ', '')  # Clean hex string
        
        # Iterate over the replacement pattern
        replacement_clean = replacement.replace(' ', '')  # Clean the replacement pattern
        for i, char in enumerate(replacement_clean):
            if char == 'x':
                new_hex.append(hex_str_clean[i])  # Keep original hex value
            else:
                new_hex.append(char)  # Replace with new value

        # Convert the list of characters back to bytes
        return bytes.fromhex(''.join(new_hex))

    ################## RANDO ####################
    def processSprites(eData:list,leData:list,lvName):
        reData = deepcopy(eData)
        relData = set(deepcopy(leData))
        # relData = set()  # Temp disabled for temp bug fixing

        posList = []
        is_panel = False # Is power-up panel level

        if len(eData)==0:
            print("Info: No sprites for this list")
            return reData,relData,len(reData)*16
        
        #print("=========== " + lvName)

        for enemyData in reData:
            # if enemyData[0]==408:
            #     print(lvName,enemyData)
            randomised = False
            #Randomize enemy
            for eLis in globalVars.enemyList:
                if enemyData[0] in eLis: # Enemy in the list
                    # Sprite Limit check, kinda buggy but I will let it slide for the time being
                    if globalVars.reduceLag and (findSpritesInArea(enemyData,posList) and randint(0,2)==1):
                        try:
                            reData.remove(enemyData)
                            continue
                        except ValueError:
                            print("WARNING: Cannot remove sprite",enemyData)
                        pass
                    posList.append((enemyData[1],enemyData[2]))
                    enemyData[0] = eLis[randint(0,len(eLis)-1)] #randomize
                    if enemyData[0] not in globalVars.SKIP_SPRITES:
                        enemyData[3] = b"\x00\x00\x00\x00\x00\x00" #Reset enemy state to default
                elif globalVars.panel_rand and enemyData[0]==428: # It is a power-up panel level
                    is_panel = True
                    break
            #Randomize enemy variation
            # Check if Rise / Fall Launcher
            if enemyData[0]==338:
                varList = globalVars.enemyVarList[str(enemyData[0])]
                enemyData[3] = bytes.fromhex(varList[randint(0,len(varList)-1)])
            # Check if checkpoint - set 1st / 2nd CP
            elif enemyData[0]==188:
                enemyData[3] = changeBytesAt(enemyData[3],5,((randint(0,1) << 4) | (0 if globalVars.cp1 else 1)))
                globalVars.cp1 = not globalVars.cp1
            # Enemy Variant
            elif str(enemyData[0]) in globalVars.enemyVarList:
                varient_string = hex_to_str(enemyData[3])
                for pattern in globalVars.enemyVarList[str(enemyData[0])]:
                    if matches_pattern(varient_string, pattern):
                        new_varient = choice(globalVars.enemyVarList[str(enemyData[0])])
                        # Replace the pattern
                        enemyData[3] = NSMBWsprite.replace_varient(varient_string, new_varient)
                        break  # Exit after first match; remove this if you want to check all patterns
            if is_panel and globalVars.panel_rand: # Power-up Panel level
                #input("PANEL TIME")
                # Set up matching combo
                combo_lis = []
                for __ in range(1,7):
                    combo_lis.append([randint(0,8) for _ in range(0,9)]*2)
                # Look for panels sprites
                cur_combo_item_idx = 0
                for spr_data in reData:
                    if spr_data[0]==428: # Assign randomised items
                        raw_bytes = b""
                        for cur_combo_lis_idx in range(0,len(combo_lis),2):
                            #print("Assigning item panel",cur_combo_lis_idx,cur_combo_item_idx)
                            cur_combo_lis1 = combo_lis[cur_combo_lis_idx]
                            cur_combo_lis2 = combo_lis[cur_combo_lis_idx+1]
                            raw_bytes += ((cur_combo_lis1[cur_combo_item_idx]<<4) | cur_combo_lis2[cur_combo_item_idx]).to_bytes(1,"big")
                        # Append orginal panel ID
                        spr_data[3] = b"\x00\x00" + raw_bytes + (bytearray(spr_data[3])[5]).to_bytes(1,"big")
                        cur_combo_item_idx+=1
                break

            # Add to load sprite list set
            relData.add(enemyData[0])

        # Add winds
        if randint(0,100)<globalVars.windChance:
            # Gets the pos of first sprite
            first_spr = reData[0]
            # Add wind effect
            reData.append([374,first_spr[1]+16,first_spr[2],b"\x00\x00\x00\x00\x00\x01",first_spr[4],first_spr[5]])
            # Determine strength of wind
            wind_stre = randint(0,3)
            # Determine Active and inactive length
            wind_time_len = randbytes(1)
            # Determine wind direction
            wind_dir = randint(0,1)
            # Piece them together
            wind_raw = b"\x00\x00" + wind_time_len + wind_dir.to_bytes(1,"big") + b"\x00" + wind_stre.to_bytes(1,"big")
            # append to list
            reData.append([90,first_spr[1]+32,first_spr[2],wind_raw,first_spr[4],first_spr[5]])
            #input("Wind added")
            relData.add(90)
            relData.add(374)

        # Add rocks
        if randint(0,100)<globalVars.rockChance:
            # Gets the pos of first sprite
            first_spr = reData[0]
            # Add falling rocks
            reData.append([293,first_spr[1]+16,first_spr[2],b"\x00\x00\x00\x00\x00\x00",first_spr[4],first_spr[5]])
            relData.add(293)
            
        #print(reData[-1])

        #del reData[-1] # This is the most hacky way to fix a bug but it works.

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
                # 1 padding byte
                int.from_bytes(byteData[22+i:23+i],"big"),  #Music ID
                int.from_bytes(byteData[23+i:24+i],"big"),  #Sound effects
                ]
            )
            i+=24 #Entry length

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
            byteData += b"\x00"
            byteData += i_lis[10].to_bytes(1,"big")
            byteData += i_lis[11].to_bytes(1,"big")
            byteData += i_lis[12].to_bytes(1,"big")
            byteData += i_lis[13].to_bytes(1,"big")
            byteData += b"\x00"
            byteData += i_lis[14].to_bytes(1,"big")
            byteData += i_lis[15].to_bytes(1,"big")

        return byteData

    def processZones(z_data):
        # Set level dark or not
        if randint(0,100) <= globalVars.darkChance:
            #TODO
            if z_data[10] & 0xF0 == 0x19: # Check for layer 0 spotlight
                z_data[10] = 0x30 # Always 0x30
            elif z_data[10] & 0x0F == 0x00: # No set - start randomising!
                z_data[10] = randint(0x20,0x25)
            else:
                z_data[10] = 0x01 # Set to layer 1 on top
        return z_data
    
class NSMBWLocations:
    def phraseByteData(byteData):
        i = 0
        returnList = []
        while i<len(byteData):
            #print(byteData[0+i:2+i])
            returnList.append(
                [
                int.from_bytes(byteData[0+i:2+i],"big"),  # X
                int.from_bytes(byteData[2+i:4+i],"big"),  # Y
                int.from_bytes(byteData[4+i:6+i],"big"),  # Width
                int.from_bytes(byteData[6+i:8+i],"big"),  # Height
                int.from_bytes(byteData[8+i:9+i],"big"),  # ID
                # 3 Padding byte
                ]
            )
            i+=12 #Entry length

        return returnList
    
    def toByteData(entranceData):
        byteData = b""
        for i_lis in entranceData:
            byteData += i_lis[0].to_bytes(2,"big")
            byteData += i_lis[1].to_bytes(2,"big")
            byteData += i_lis[2].to_bytes(2,"big")
            byteData += i_lis[3].to_bytes(2,"big")
            byteData += i_lis[4].to_bytes(1,"big")
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
            #print(i_lis)
            byteData += pack(">HHffhxx",*i_lis)

        return byteData