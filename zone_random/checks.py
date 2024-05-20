def checkExitSprite(zone):
    EXIT_SPRITES = [203,113,434,412,428,211,363,383,405,406,407,479]
    for spr in zone["sprites"]:
        if spr[0] in EXIT_SPRITES:
            return spr
    return -1

def checkBossSprite(zone):
    EXIT_SPRITES = [211,363,383,405,406,407,479]
    for spr in zone["sprites"]:
        if spr[0] in EXIT_SPRITES:
            return spr
    return -1

def checkEntSpawn(zone):
    for ent in zone["entrance"]:
        assert len(zone["AreaSetting"])==1, "AreaSetting len is not 1"
        if ent[6] == zone["AreaSetting"][0][6]: # Check same entrance ID
            return ent
    return -1

def checkOnlyOneEnt(zone):
    return len(zone)==1

def findExitEnt(zone):
    ret_pos = []
    ret_pos_noExit = []
    for i in range(0,len(zone["entrance"])):
        if (zone["entrance"][i][9]&128)==0 or (zone["entrance"][i][3]!=0 and zone["entrance"][i][4]!=0):
            ret_pos.append(i)
        else:
            ret_pos_noExit.append(i)
    return ret_pos,ret_pos_noExit



def checkPosInSpecificZone(zoneDat, sprPos, width=0, height=0) -> int: # May also incoperate with the function above?
    # for every zone, Check X pos, then Y pos
    #print("POS",zoneDat[1]+zoneDat[3]+16,sprPos[1])
    #              Min X                       Max X = min x + width
    return sprPos[0]+width>=(zoneDat[0]-(16**2)) and sprPos[0]<=(zoneDat[0]+zoneDat[2]+(16**2))\
        and sprPos[1]+height>=(zoneDat[1]-(16**2)) and sprPos[1]<=(zoneDat[1]+zoneDat[3]+(16**2))
def checkPosInZone(zoneData, sprPos, width=0, height=0) -> int:
    # for every zone, Check X pos, then Y pos
    for i in range(0,len(zoneData)):
        zoneDat = zoneData[i]
        if checkPosInSpecificZone(zoneDat,sprPos,width,height):
            return zoneDat[6]
    return -1