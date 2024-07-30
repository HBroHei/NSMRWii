from Util import objPosToTilePos

ID_POS_LOOKUP = {
    "ZoneBound" : 4,
    "topBackground" : 0,
    "bottomBackground" : 0,
    "entrance" : 2,
    "zone" : 6,
    "location" : 4,
    "path" : 0
}
ID_REF_LOOKUP = {
    "ZoneBound" : ("zone", 7),
    "topBackground" : ("zone", 11),
    "bottomBackground" : ("zone", 12),
}

used_ids = [{},{},{}]

DOOR_TYPE_3X2 = 0
DOOR_TYPE_BOSS = 1
# Check if the door sprite and door entrance match
def isEntranceDoorMatch(doorType:int, doorSpr:list, doorEnt:list):
    if doorType==0: # Normal
        doorRange = (range(doorSpr[1]-8,doorSpr[1]+8 ),range(doorSpr[2]+24,doorSpr[2]+40)) # +0, +32
    elif doorType==1: # Boss
        doorRange = (range(doorSpr[2]+0,doorSpr[2]+16),range(doorSpr[2]+24,doorSpr[2]+40)) # +8, +32
    else: # Unknown? This should not be called
        doorRange = (0,0)
    return doorEnt[0] in doorRange[0] and doorEnt[1] in doorRange[1]

def alignToPos(zone,x,y):
    # Assuming x and y are > 16

    # Gets Section 9[0], [1] for start of zone
    # Gets the diff to x,y
    diffx = zone["zone"][0] - x
    diffy = zone["zone"][1] - y
    # Do not change the order of these 4 statements
    # ^ For future me, my brain liked to swap things
    #print(zone["zone"], x, y, diffx, diffy)
    # Put the zone to the new pos
    zone["zone"][0] = x
    zone["zone"][1] = y

    door_lists = []
    # Iterate through every section to convert them to be relative to x, y
    # Only section 6, 7, 9, 10, 13 only actually. But still, works, and for loops.
    for i in range(len(zone["sprites"])):
        zone["sprites"][i][1] -= diffx
        zone["sprites"][i][2] -= diffy
        # Check if sprite is door
        if zone["sprites"][i][0] in [182, 259, 276, 277, 278, 452]:
            door_lists.append(i)

    # Zones covered above
    for i in range(len(zone["location"])):
        zone["location"][i][0] -= diffx
        zone["location"][i][1] -= diffy
    for i in range(len(zone["pathNode"])):
        zone["pathNode"][i][0] -= diffx
        zone["pathNode"][i][1] -= diffy

    # Tiles section
    diffx_tiles, diffy_tiles = objPosToTilePos((diffx,diffy))
    for layerNo in range(0,2):
        curLayerStr = "bgdatL" + str(layerNo)
        if curLayerStr not in zone: # Skip; non-existing tiles layer
            continue
        for i in range(len(zone[curLayerStr])):
            zone[curLayerStr][i][1] -= diffx_tiles
            zone[curLayerStr][i][2] -= diffy_tiles

    # SPECIAL: need to align entrances to specific pos
    # Boss doors: half a tile
    # Everything else (unless I missed sth): full tile
    for i in range(len(zone["entrance"])):
        zone["entrance"][i][0] -= diffx
        zone["entrance"][i][1] -= diffy
        # Check entrance type:
        #  - Door - get door sprite behind,
        #    - Boss : door pos x + 8, door pos y + 32
        #    - Ghost / Normal: door x + 0, door y + 32
        #    - Bowser: door x + 8, door y + 32
        #  - Pipe: Check if divisible by 16: -8 if no
        if zone["entrance"][i][5] in (27,2): # Type == door
            # Gets the door behind that ent
            for j in door_lists:
                print("Checking ", j, ":", zone["sprites"][j])
                """if isEntranceDoorMatch(1,zone["sprites"][j],zone["entrance"][i]): # Boss door
                    # Correct x pos?
                    if (zone["entrance"][i][0]-zone["sprites"][j][0]+8)!=0:
                        zone["entrance"][i][0] = zone["sprites"][j][0]+8
                    # Correct y pos?
                    if (zone["entrance"][i][1]-zone["sprites"][j][1]+32)!=0:
                        zone["entrance"][i][1] = zone["sprites"][j][1]+32
                elif isEntranceDoorMatch(0,zone["sprites"][j],zone["entrance"][i]): # Normal door
                    # Correct x pos?
                    if zone["entrance"][i][0]!=zone["sprites"][j][0]:
                        zone["entrance"][i][0] = zone["sprites"][j][0]
                    # Correct y pos?
                    if (zone["entrance"][i][1]-zone["sprites"][j][1]+32)!=0:
                        zone["entrance"][i][1] = zone["sprites"][j][1]+32"""
        elif zone["entrance"][i][5] in (3,4,5,6,16,17,18,19): # Type==pipe
            if zone["entrance"][i][0]%16 != 0:
                zone["entrance"][i][0] -= 8
            if zone["entrance"][i][1]%16 != 0:
                zone["entrance"][i][1] -= 8

    return zone

# Correct incorrect sprite zone id
### USE AFTER corrDupID as it relies on zone ID ###
def corrSprZone(cur_zone):
    #print(list(cur_zone.keys()))
    for j in range(0,len(cur_zone["sprites"])):
        cur_zone["sprites"][j][4] = cur_zone["zone"][6]
    return cur_zone

### DUPLICATE REMOVAL THINGS ###
# I can't decide if using AI or thinking abt the algorithm and writing code by myself is faster lol but still, thanks AI
# Definitely needs modifying tho
######## TODO DUPLICATE REPLACEMNENT FUNCTION NOT DEBUGGED ######## 
## btw this is gonna be a hell to debug (and I dont even know an effective way to debug this lol(sign))
def generate_unique_id(used_ids):
    new_id = max(used_ids) + 1 if used_ids else 1
    while new_id in used_ids:
        new_id += 1
    return new_id

def update_references(data_list, position, old_id, new_id):
    #item[position] = (new_id for item in data_list if item[position] == old_id else item[position])
    for item in data_list:
        if item[position] == old_id:
            item[position] = new_id

def corrDupID(areaNo,zone):
    re_zone = zone

    # for cur_dict in area:
    for key_prop, zone_prop_lst in re_zone.items():
        if isinstance(zone_prop_lst, list) and len(zone_prop_lst) > 0:
            """
                if key == "bound":
                    id_position = 4
                    references = ["zone", 7]
                elif key == "background1":
                    id_position = 0
                    references = ["zone", 11]
                elif key == "background2":
                    id_position = 0
                    references = ["zone", 12]
                elif key == "entrance":
                    id_position = 2
                    references = []
                elif key == "location":
                    id_position = 4
                    references = []
                elif key == "path":
                    id_position = 0
                    references = ["path", 2]
                elif key == "pathNode":
                    id_position = 0
                    references = ["path", 2]
                else:
                    continue
                """
            try:
                id_position = ID_POS_LOOKUP[key_prop]
            except KeyError:
                # No id needed to replace - skip
                continue
            try:
                references = ID_REF_LOOKUP[key_prop]
            except KeyError:
                # May not have ref
                pass
            if not isinstance(zone_prop_lst[0],list): # Should be "zone"
                cur_id = zone_prop_lst[6]
                try:
                    # Check in duplicated list
                    if cur_id in used_ids[areaNo][key_prop]:
                        print("duplicated",key_prop,cur_id,used_ids[areaNo][key_prop])
                        new_id = generate_unique_id(used_ids)
                        zone_prop[id_position] = new_id
                        for ref_key, ref_pos in references:
                            if ref_key in re_zone:
                                update_references(re_zone[ref_key], ref_pos, cur_id, new_id)
                except KeyError:
                    # No set found - no duplicates
                    used_ids[areaNo][key_prop] = set()
                try:
                    used_ids[areaNo][key_prop].add(cur_id)
                except KeyError:
                    used_ids[areaNo][key_prop] = set()
                    used_ids[areaNo][key_prop].add(cur_id)
            else: # Anything other than "zone" prop
                for zone_prop in zone_prop_lst:
                    cur_id = zone_prop[id_position]
                    try:
                        # Check in duplicated list
                        if cur_id in used_ids[areaNo][key_prop]:
                            print("duplicated",key_prop,cur_id,used_ids[areaNo][key_prop])
                            new_id = generate_unique_id(used_ids)
                            zone_prop[id_position] = new_id
                            for ref_key, ref_pos in references:
                                if ref_key in re_zone:
                                    update_references(re_zone[ref_key], ref_pos, cur_id, new_id)
                    except KeyError:
                        # No set found - no duplicates
                        used_ids[areaNo][key_prop] = set()
                    addID(areaNo,key_prop,zone_prop_lst)

    return re_zone

# Alright but these are written by myself okay?
# Add the IDs to the list of repeated IDs
def addID(areaNo,key,zone_prop_lst):
    id_position = ID_POS_LOOKUP[key]
    for item in zone_prop_lst:
        cur_id = item[id_position]
        try:
            used_ids[areaNo][key].add(cur_id)
        except KeyError:
            used_ids[areaNo][key] = set()
            used_ids[areaNo][key].add(cur_id)
def addIDsFromZone(areaNo,zone):
    for key,value in zone.items():
        try:
            addID(areaNo,key,value)
        except KeyError:
            # No id needed to replace - skip
            continue