from copy import deepcopy

"""
    Sprite IDs:
    203 Chest
    113 Goal Pole
    434 World Cannon
    412 1UP Ballon Toad Hse
    428 Panel Toad Hse
    211 BJr 1st fight
    363 Tower Boss
    383 Kamek
    405 BJr 2nd fight
    406 BJr 3rd fight
    407 Castle Boss
    479 Final switch
    454 Ambush Controller
"""

def checkisCutsceneZone(zone):
    for i in range(0,len(zone["sprites"])):
        spr = zone["sprites"][i]
        if spr[0] in (408,409):
            return spr
    return -1

def checkExitSprite(zone):
    EXIT_SPRITES = [203,113,434,412,428,211,363,383,405,406,407,479]
    for i in range(0,len(zone["sprites"])):
        spr = zone["sprites"][i]
        if spr[0] in EXIT_SPRITES:
            return spr,i
    return -1,-1

# Check for any bosses
def checkBossSprite(zone):
    EXIT_SPRITES = [211,363,383,405,406,407,479]
    for i in range(len(zone["sprites"])):
        spr = zone["sprites"][i]
        if spr[0] in EXIT_SPRITES:
            return spr,i
    return -1,-1

# Check for koopalings
def checkBossChar(zone):
    BOSS_SPRITES = [189,192,336,337,340,341,344,347,348,349,364,365,372,375,381]
    for i in len(zone["sprites"]):
        spr = zone["sprites"][i]
        if spr[0] in BOSS_SPRITES:
            return spr,i
    return -1

def checkEntSpawn(zone):
    for ent in zone["entrance"]:
        assert len(zone["AreaSetting"])==1, "AreaSetting len is not 1"
        if ent[6] == zone["AreaSetting"][0][6]: # Check same entrance ID
            return ent
    return -1

def checkOnlyOneEnt(zone):
    return len(zone["entrance"])==1

# Find all the enterables and non-enterables
def findExitEnt(zone):
    ret_pos = [] # Enterable
    ret_pos_noExit = [] # Non-enterable
    ent_179 = [] # Entrance IDs related to sprite 179 OR rolling hills
    entspr_ref = [] # sprites position in list that needs altering
    # First, check for sprite 179
    spr_list = zone["sprites"]
    for spr in spr_list:
        if spr[0]==179: # Special Exit Controller
            # Get the 4th([3]) char, 1st digit and 6th([5]) char, 2nd digit
            ent_179.append(int((spr[3][3] & 0xF0) | (spr[3][5] & 0x0F)))
            if (spr[3][2] & 4)!=0:  # Remove "wrap back to map" function
                # print(spr[3])
                # input("Needed to make change")
                spr_pos = zone["sprites"].index(spr)
                tmp_bytearr = bytearray(zone["sprites"][spr_pos][3])
                tmp_bytearr[2] = 0x00
                zone["sprites"][spr_pos][3] = bytes(tmp_bytearr)
        elif spr[0]==355 or spr[0]==360: # Rolling hill pipes
            # Gets the 5th byte (4th pos), lower nibble
            ent_179.append(int((spr[3][4] & 0x0F)))
            spr_pos = zone["sprites"].index(spr)

    for i in range(0,len(zone["entrance"])):
        # TODO Find if "Normal" Entrances have sprites associated with them
        #   Marked "enterable", Orginal Dest Area & ID!=0, Area Entrance Type can be entered
        #print("Finding exit:",zone["orgLvl"],zone["entrance"][i][9]&128,zone["entrance"][i][5] in (27,3,4,5,6,16,17,18,19),zone["entrance"][i][5])
        print("Finding exit:",i,":",zone["orgLvl"],zone["entrance"][i])
        if ((zone["entrance"][i][9]&128)==0 and\
            #((zone["entrance"][i][3]!=0 and zone["entrance"][i][4]!=0) and\
            zone["entrance"][i][5] in (27,2,3,4,5,6,15,16,17,18,19)) or\
            (zone["entrance"][i][2] in ent_179):
            ret_pos.append(i)
        else:
            ret_pos_noExit.append(i)

    # Failsafe - if every entrance is enterable, copy ret_pos to ret_pos_noExt (to avoid zone have no exit)
    #if len(ret_pos_noExit)==0: ret_pos_noExit = deepcopy(ret_pos)
    return ret_pos,ret_pos_noExit

def checkPosInSpecificPos(hostPos, sprPos, width=0, height=0) -> int: # May also incoperate with the function above?
    # for every hosts, Check X pos, then Y pos
    #print("POS",zoneDat[1]+zoneDat[3]+16,sprPos[1])
    return hostPos[0] < sprPos[0]+width and hostPos[0]+hostPos[2] > sprPos[0]\
        and hostPos[1] < sprPos[1]+height and hostPos[1]+hostPos[3] > sprPos[1]

def checkPosInSpecificZone(zoneDat, sprPos, width=0, height=0) -> int: # May also incoperate with the function above?
    # for every zone, Check X pos, then Y pos
    #print("POS",zoneDat[1]+zoneDat[3]+16,sprPos[1])
    #              Min X                       Max X = min x + width
    return sprPos[0]+width>=(zoneDat[0]-(16**2)) and sprPos[0]<=(zoneDat[0]+zoneDat[2]+(16**2))\
        and sprPos[1]+height>=(zoneDat[1]-(16**2)) and sprPos[1]<=(zoneDat[1]+zoneDat[3]+(16**2))
def checkPosInZone(zoneData, sprPos, width=0, height=0) -> int:
    # for every zone, Check X pos, then Y pos
    for i in range(0,len(zoneData)):
        zoneDat = zoneData[i]["zone"]
        if checkPosInSpecificZone(zoneDat,sprPos,width,height):
            return i
    return -1