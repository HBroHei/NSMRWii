from copy import deepcopy

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

# Find all the enterables and non-enterables
def findExitEnt(zone):
    ret_pos = [] # Enterable
    ret_pos_noExit = [] # Non-enterable
    ent_179 = [] # Entrance IDs related to sprite 179
    # First, check for sprite 179
    spr_list = deepcopy(zone["sprites"])
    for spr in spr_list:
        if spr[0]==179: # Special Exit Controller
            # Get the 4th([3]) char, 1st digit and 6th([5]) char, 2nd digit
            ent_179.append(int((spr[3][3] & 0xF0) | (spr[3][5] & 0x0F)))

    for i in range(0,len(zone["entrance"])):
        # TODO Find if "Normal" Entrances have sprites associated with them
        #   Marked "enterable", Orginal Dest Area & ID!=0, Area Entrance Type can be entered
        print("Finding exit:",zone["entrance"][i][9]&128,zone["entrance"][i][5] in (27,3,4,5,6,16,17,18,19),zone["entrance"][i][5])
        if ((zone["entrance"][i][9]&128)==0 and\
            #((zone["entrance"][i][3]!=0 and zone["entrance"][i][4]!=0) and\
            zone["entrance"][i][5] in (27,2,3,4,5,6,16,17,18,19)) or\
            (zone["entrance"][i][2] in ent_179):
            ret_pos.append(i)
        else:
            ret_pos_noExit.append(i)
    return ret_pos,ret_pos_noExit

def findOpenArea(tiles, width=4, height=4):
    """
    Finds an open area of the specified width and height in a list of tiles.

    Args:
        tiles: A list of tiles, each represented as [id, x, y, width, height].
        width: The desired width of the open area.
        height: The desired height of the open area.

    Returns:
        A tuple containing the x and y coordinates of the top-left corner of the open area,
        or None if no such area is found.
    
    By Gemini
    """

    for y in range(0, max([tile[2] + tile[4] for tile in tiles])):
        for x in range(0, max([tile[1] + tile[3] for tile in tiles])):
            # Check if the current position is within any tile
            if any(
                x >= tile[1] and x < tile[1] + tile[3] and y >= tile[2] and y < tile[2] + tile[4]
                for tile in tiles
            ):
                continue

            # Check if the area is open
            if all(
                any(
                    x + w >= tile[1] and x < tile[1] + tile[3] and y + h >= tile[2] and y < tile[2] + tile[4]
                    for tile in tiles
                )
                for w in range(width)
                for h in range(height)
            ):
                return x, y

    return None

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