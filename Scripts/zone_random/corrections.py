from Util import tilePosToObjPos, objPosToTilePos, changeBytesAt, changeNibbleAt, getNibbleAt, nibblesToByte
from json import load
from collections import defaultdict
from os import listdir, getcwd
from copy import deepcopy

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
    # Orgin type : (To replace type, pos)
    "ZoneBound" : ("zone", 7),
    "topBackground" : ("zone", 11),
    "bottomBackground" : ("zone", 12),
    "zone" : {"entrance" , 6},
}

ID_MATCH_TABLE = load(open("./zone_random/id_match.json" if "id_match.json" in listdir(getcwd()) else "./Scripts/zone_random/id_match.json"))
# Extract a tuple of sprite IDs included
ID_MATCH_SPRID = set(key.replace("D","") for inner_dict in ID_MATCH_TABLE.values() if isinstance(inner_dict, dict) for key in inner_dict.keys() if "_Special" not in key)
# TODO /\ Untested
ID_MATCH_LIMIT16 = ["path", "location", "entrance"] # These IDs are limited to be 16 max dur to sprite limitation

used_ids_sprites = [defaultdict(list),defaultdict(list),defaultdict(list),defaultdict(list)]
new_ids_sprites = [defaultdict(int),defaultdict(int),defaultdict(int),defaultdict(int)]

used_ids = [{},{},{},{}]

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

def alignToPos(zone,nx,ny,use_min = True):
    def bgdat_layer_check(zone):
        flag = True
        for l_no in range(0,3):
            if "bgdatL" + str(l_no) in zone:
                flag = flag and all(0<=til[1]<=1024 and 0<=til[2]<=512 for til in zone["bgdatL" + str(l_no)])
                if not flag:
                    print("layer",l_no,"failed")
                    for til in zone["bgdatL" + str(l_no)]:
                        if not (0<=til[1]<=16343 and 0<=til[2]<=16343):
                            return til
                    break
        return []
    def clamp(val):
        # if max(0, min(val, 16343))!=val:
        #     print("Clamp used" + str(val))
        #     input("This should not have beem called. Copy the last ~100 lines and report")
        # return max(0, min(val, 16343))
        return val
        if val<0:
            return val + 16343
        elif val>16343:
            return val - 16343
        else:
            return val
    passes = 0

    if use_min:
        nx = min(zone["zone"][0],nx)
        ny = min(zone["zone"][1],ny)

    diffx = zone["zone"][0] - nx
    diffy = zone["zone"][1] - ny

    diffx_tiles, diffy_tiles = objPosToTilePos((diffx,diffy))

    # Variables indicate if property passes check (*True if not passing*)
    check_spr = False
    check_loc = False
    check_ent = False
    check_pat = False
    check_zone = False
    check_tile = []

    while passes==0 or (check_spr or check_loc or check_pat or check_ent or check_zone
        or check_tile!=[]):
        # for spr in zone["sprites"]:
        #     if not (0<=spr[1]<=16384 and 0<=spr[2]<=16384):
        #         print(spr,"failed")
        #         break
        # else:
        #     print("All good")

        # We do not care if x + width / y + height exceeds limit as it does not overflow python
        zone["zone"][0] = clamp(zone["zone"][0] - diffx)
        zone["zone"][1] = clamp(zone["zone"][1] - diffy)
        #print("New zone",zone["zone"],diffy)
        zone["sprites"] =\
            [[spr[0],clamp(spr[1] - diffx),clamp(spr[2] - diffy),spr[3],spr[4],spr[5]] for spr in zone["sprites"]]
        zone["location"] =\
            [[clamp(loc[0] - diffx), clamp(loc[1] - diffy),loc[2],loc[3],loc[4]] for loc in zone["location"]]
        zone["pathNode"] =\
            [[clamp(loc[0] - diffx), clamp(loc[1] - diffy),loc[2],loc[3],loc[4]] for loc in zone["pathNode"]]
        for i in range(len(zone["entrance"])):
            zone["entrance"][i][0] = clamp(zone["entrance"][i][0] - diffx)
            zone["entrance"][i][1] = clamp(zone["entrance"][i][1] - diffy)
            # Check entrance type:
            #  - Door - get door sprite behind,
            #    - Boss : door pos x + 8, door pos y + 32
            #    - Ghost / Normal: door x + 0, door y + 32
            #    - Bowser: door x + 8, door y + 32
            #  - Pipe: Check if divisible by 16: -8 if no
            if zone["entrance"][i][5] in (27,2): # Type == door
                # Gets the door behind that ent (DISABLED)
                # for j in door_lists:
                #     print("Checking ", j, ":", zone["sprites"][j])
                pass
            elif zone["entrance"][i][5] in (3,4,5,6,16,17,18,19): # Type==pipe
                if zone["entrance"][i][0]%16 != 0:
                    zone["entrance"][i][0] -= 8
                if zone["entrance"][i][1]%16 != 0:
                    zone["entrance"][i][1] -= 8
        for layerNo in range(0,2):
            curLayerStr = "bgdatL" + str(layerNo)
            #print("checking",curLayerStr)
            if curLayerStr in zone:
                #print("adjusting",curLayerStr)
                zone[curLayerStr] =\
                    [[til[0],clamp(til[1] - diffx_tiles),clamp(til[2] - diffy_tiles),til[3],til[4]] for til in zone[curLayerStr]]
        passes += 1
        # if passes==1:
        #     diffx = 160
        #     diffy = 160
        #     diffx_tiles = 10
        #     diffy_tiles = 10
        if passes==100:
            print("Failed to align pos")
            exit()

        # Adjust based on the result
        
        change_x = 0
        change_y = 0

        check_spr = not all(0<=spr[1]<=16384 and 0<=spr[2]<=8192  for spr in zone["sprites"])
        check_loc = not all(0<=loc[0]<=16384 and 0<=loc[1]<=8192  for loc in zone["location"])
        check_pat = not all(0<=pat[0]<=16384 and 0<=pat[1]<=8192  for pat in zone["pathNode"])
        check_ent = not all(0<=ent[0]<=16384 and 0<=ent[1]<=8192  for ent in zone["entrance"])
        check_zone = not ((0<=zone["zone"][0]<=16384) and (0<=zone["zone"][1]<=8192 ) and (0<=zone["zone"][0]+zone["zone"][2]<=16384) and (0<=zone["zone"][1]+zone["zone"][3]<=8192 ))
        check_tile = bgdat_layer_check(zone)
        if passes>=1:
            if check_spr:
                for spr in zone["sprites"]:
                    if spr[1]<0: change_x = 1; break
                    elif spr[1]>8192 : change_x = 2; break
                    if spr[2]<0: change_y = 1; break
                    elif spr[2]>8192 : change_y = 2; break
            elif check_loc:
                for loc in zone["location"]:
                    if loc[0]<0: change_x = 1; break
                    elif loc[0]>16384: change_x = 2; break
                    if loc[1]<0: change_y = 1; break
                    elif loc[1]>8192 : change_y = 2; break
            elif check_pat:
                for pat in zone["pathNode"]:
                    if pat[0]<0: change_x = 1; break
                    elif pat[0]>16384: change_x = 2; break
                    if pat[1]<0: change_y = 1; break
                    elif pat[1]>8192 : change_y = 2; break
            elif check_ent:
                for ent in zone["entrance"]:
                    if ent[0]<0: change_x = 1; break
                    elif ent[0]>16384: change_x = 2; break
                    if ent[1]<0: change_y = 1; break
                    elif ent[1]>8192 : change_y = 2; break
            elif check_zone:
                #print("Zone failed:",zone["zone"])
                if zone["zone"][0]<0: change_x = 1
                elif zone["zone"][0]>16384: change_x = 2
                if zone["zone"][1]<0: change_y = 1
                elif zone["zone"][1]>8192 : change_y = 2
            elif check_tile!=[]:
                if check_tile[1]<0: change_x = 1
                elif check_tile[1]>1024: change_x = 2
                if check_tile[2]<0: change_y = 1
                elif check_tile[2]>512 : change_y = 2

            if change_x==1: diffx = -160; diffx_tiles = -10; diffy = 0; diffy_tiles = 0
            if change_x==2: diffx = 160; diffx_tiles = 10; diffy = 0; diffy_tiles = 0
            if change_y==1: diffy = -160; diffy_tiles = -10; diffx = 0; diffx_tiles = 0
            if change_y==2: diffy = 160; diffy_tiles = 10; diffx = 0; diffx_tiles = 0
            # print("Checklist",passes==0 or (check_spr or check_loc or check_pat or check_ent or check_zone or check_tile!=[]))

    return zone

# Correct incorrect sprite / entrance zone id
### USE AFTER corrDupID as it relies on zone ID ###
def corrSprEntZone(cur_zone):
    for j in range(0,len(cur_zone["sprites"])):
        cur_zone["sprites"][j][4] = cur_zone["zone"][6]
    # for j in range(0,len(cur_zone["entrance"])):
    #     print(f"Corrected from {cur_zone["entrance"][j]} to {cur_zone["zone"]}")
    #     cur_zone["entrance"][j][6] = cur_zone["zone"][6]
    #     print(f"Corrected to {cur_zone["entrance"][j]}")
    return cur_zone
    


### DUPLICATE REMOVAL THINGS ###
# I can't decide if using AI or thinking abt the algorithm and writing code by myself is faster lol but still, thanks AI
# Definitely needs modifying tho
######## TODO DUPLICATE REPLACEMNENT FUNCTION NOT DEBUGGED ######## 
## btw this is gonna be a hell to debug (and I dont even know an effective way to debug this lol(sign))
def generate_unique_id(used_ids, key_prop):
    new_id = 0
    failsafe_count = 0
    # loop until the id is not duplicated
    while new_id in used_ids:
        new_id += 1
        # Check if exceed 16
        # Also have it pass if it already looped around
        if key_prop in ID_MATCH_LIMIT16 and new_id>15 and failsafe_count<=2:
            failsafe_count+=1
            new_id = 0
    if failsafe_count>1: input("FAILSAFE ACTIVATED")
    return new_id

def update_references(data_list, position, old_id, new_id):
    if isinstance(data_list[0],list):
        for item in data_list:
            if item[position] == old_id:
                item[position] = new_id
    else:
        if data_list[position] == old_id:
            data_list[position] = new_id

def corrDupID(areaNo,zone):
    global used_ids_sprites
    re_zone = zone

    # For each property in zones
    for key_prop, zone_prop_lst in re_zone.items():
        # IF there is stuff inside the list
        if isinstance(zone_prop_lst, list) and len(zone_prop_lst) > 0:
            # Check which position is the id
            try:
                id_position = ID_POS_LOOKUP[key_prop]
            except KeyError:
                # No id needed to replace - skip
                continue
            references = tuple()
            try:
                references = ID_REF_LOOKUP[key_prop]
            except KeyError:
                # May not have ref
                print("Info: Cannot find ref",key_prop)
                pass
            if key_prop=="zone": # The first item is not another list, Should be "zone"
                cur_id = zone_prop_lst[id_position]
                # Check if there is any zone exist
                if key_prop in used_ids[areaNo] and cur_id in used_ids[areaNo][key_prop]:
                    # Check in duplicated list
                    new_id = generate_unique_id(used_ids[areaNo][key_prop], key_prop)
                    print(f"duplicated {key_prop,cur_id,used_ids[areaNo][key_prop]}, new ID = {new_id}")
                    zone_prop_lst[id_position] = new_id
                    # Change other referenced items 
                    (ref_type, ref_pos) = references
                    print("REFERENCE", references)
                    update_references(re_zone[ref_type], ref_pos, cur_id, new_id)
                    cur_id = new_id # In the future make this better
                try:
                    used_ids[areaNo][key_prop].add(cur_id)
                except KeyError:
                    used_ids[areaNo][key_prop] = set()
                    used_ids[areaNo][key_prop].add(cur_id)
            else: # First item is another list, Anything other than "zone" prop
                for zone_item in zone_prop_lst:
                    cur_id = zone_item[id_position] % 32 # No way there are 32 entrances
                    keyErrored = False

                    # Check if set is found
                    try:
                        used_ids[areaNo][key_prop]
                    except KeyError:
                        # No set found implies no duplicates
                        used_ids[areaNo][key_prop] = set()
                        keyErrored = True
                    # Set found - check for potential duplicates
                    if not keyErrored:
                        #print("AREA NO", areaNo, key_prop, used_ids[areaNo][key_prop], "checking", cur_id)
                        # Check in duplicated list
                        if cur_id in used_ids[areaNo][key_prop]:
                            # Generate another ID
                            new_id = generate_unique_id(used_ids[areaNo][key_prop], key_prop)
                            #print(f"Duplicated {key_prop} ,ID {cur_id}, Used IDs {used_ids[areaNo][key_prop]}. Assigned new ID {new_id}")
                            zone_item[id_position] = new_id
                            # Check linked locations
                            if key_prop=="location":
                                #input(f"==================Updated location {cur_id}->{new_id}==========================")
                                re_zone["sprites"] = update_spr_value(re_zone["sprites"], cur_id, new_id, "Location ID")
                            # Check linked entrance
                            elif key_prop=="entrance":
                                re_zone["sprites"] = update_spr_value(re_zone["sprites"], cur_id, new_id, "Entrance ID")
                            # Check linked path
                            elif key_prop=="path":
                                re_zone["sprites"] = update_spr_value(re_zone["sprites"], cur_id, new_id, "Path ID")

                            if len(references)!=0:
                                #print("Reference",references,re_zone[references[0]])
                                (ref_key, ref_pos) = references
                                if ref_key in re_zone:
                                    update_references(re_zone[ref_key], ref_pos, cur_id, new_id)
                            cur_id = new_id
                    
                    # Add id to the list of used IDs
                    addID(areaNo,key_prop,cur_id)
    
    def update_sprid(spr_pos,id_type, old_val):
        # Generate a new ID
        while (new_id := new_ids_sprites[areaNo][id_type]+1) in used_ids_sprites[areaNo][to_check_ids]:
            new_ids_sprites[areaNo][id_type] = new_id
            pass
        re_zone["sprites"] = update_spr_value(re_zone["sprites"], old_val, new_id, id_type)
        used_ids_sprites_new[areaNo][to_check_ids].append(new_id)

    # Check for sprites shared ID duplicates
    # First, make a copy for the new one
    used_ids_sprites_new = deepcopy(used_ids_sprites)
    # For each sprites
    for i in range(len(re_zone["sprites"])):
        SPR_ID = str(re_zone["sprites"][i][0])
        # if sprite ID is in to-check list
        # print(f"SPR ID {SPR_ID}")
        if SPR_ID in ID_MATCH_SPRID:
            # TODO It should works for now, but oh man is this very unoptimised (time complexity wise)
            # Check for every IDs
            for to_check_ids in ID_MATCH_TABLE:
                # If it is in the to-check list
                if SPR_ID in ID_MATCH_TABLE[to_check_ids] and "_Special" not in to_check_ids:
                    # print(f"Checking {to_check_ids}")
                    # Check if has only 1 pos
                    npos_lst = (ID_MATCH_TABLE[to_check_ids][SPR_ID],) if isinstance(ID_MATCH_TABLE[to_check_ids][SPR_ID][0],int) else ID_MATCH_TABLE[to_check_ids][SPR_ID]
                    # For every pos pair
                    for npos in npos_lst:
                        joined_byte = nibblesToByte(
                            getNibbleAt(re_zone["sprites"][i][3],npos[0]),
                            getNibbleAt(re_zone["sprites"][i][3],npos[1])
                        ) if len(npos)==2\
                        else getNibbleAt(re_zone["sprites"][i][3],npos[0])
                        # If ID is used
                        if joined_byte in used_ids_sprites[areaNo][to_check_ids]:
                            # Assign new ID
                            update_sprid(i, to_check_ids, joined_byte)
                        else:
                            # Still add it to the used IDs pile
                            used_ids_sprites_new[areaNo][to_check_ids].append(joined_byte)
    # After iterating all the sprite, set used_ids_sprites to the new one
    used_ids_sprites = deepcopy(used_ids_sprites_new)

    #print("USED IDS",used_ids)
    return re_zone

def update_spr_value(re_zone_sprites, old_value, new_value, id_type):
    # Check if sprite id in ID_MATCH_TABLE[id_type]
    # Update direct reference
    for i in range(len(re_zone_sprites)):
        SPR_ID = str(re_zone_sprites[i][0])
        # Update value if sprite id is in the relavent match table
        #print(f"Checking {SPR_ID} : {ID_MATCH_TABLE[id_type]}, {SPR_ID in ID_MATCH_TABLE[id_type]}")
        if SPR_ID in ID_MATCH_TABLE[id_type]:
            # Check if has only 1 pos
            npos_lst = (ID_MATCH_TABLE[id_type][SPR_ID],) if isinstance(ID_MATCH_TABLE[id_type][SPR_ID][0],int) else ID_MATCH_TABLE[id_type][SPR_ID]
            # For every position
            for npos in npos_lst:
                # Check for pos (also checks if only 1 byte needs to change)
                if len(npos)==2:
                    joined_byte = nibblesToByte(
                        getNibbleAt(re_zone_sprites[i][3],npos[0]),
                        getNibbleAt(re_zone_sprites[i][3],npos[1])
                    )
                    #input(f"CHECKING Byte: {re_zone_sprites[i][3]} -- {joined_byte}=={old_value}")
                    if joined_byte==old_value:
                        re_zone_sprites[i][3] = changeNibbleAt(re_zone_sprites[i][3],npos[0],new_value)
                        re_zone_sprites[i][3] = changeNibbleAt(re_zone_sprites[i][3],npos[1],new_value)
                else: # Only 1 byte needs changing
                    joined_byte = getNibbleAt(re_zone_sprites[i][3],npos[0])
                    #input(f"CHECKING Byte: {re_zone_sprites[i][3]} -- {joined_byte}=={old_value}")
                    if joined_byte==old_value:
                        re_zone_sprites[i][3] = changeNibbleAt(re_zone_sprites[i][3],npos[0],new_value)
        elif SPR_ID in ID_MATCH_TABLE["_Special ID"]:
            for special in ID_MATCH_TABLE["_Special"]:
                # Check if matching sprite id and the value at the position matches the id type we are processing
                if SPR_ID in special["ids"] and special["value"][getNibbleAt(re_zone_sprites[i][3],special["pos"][0])]==id_type:
                    joined_byte = nibblesToByte(
                        getNibbleAt(re_zone_sprites[i][3],ID_MATCH_TABLE[id_type][f"D{SPR_ID[0]}"]),
                        getNibbleAt(re_zone_sprites[i][3],ID_MATCH_TABLE[id_type][f"D{SPR_ID[1]}"])
                    )
                    if joined_byte==old_value:
                        changeNibbleAt(re_zone_sprites[i][3],ID_MATCH_TABLE[id_type][f"D{SPR_ID[0]}"],new_value)
                        changeNibbleAt(re_zone_sprites[i][3],ID_MATCH_TABLE[id_type][f"D{SPR_ID[1]}"],new_value)
    return re_zone_sprites


# Alright but these are written by myself okay?
# Add the IDs to the list of repeated IDs
def addID(areaNo,key,cur_id):
    try:
        used_ids[areaNo][key].add(cur_id)
    except KeyError:
        used_ids[areaNo][key] = set()
        used_ids[areaNo][key].add(cur_id)

# THIS ISNT USED FOR ANYTHING
def addIDsFromZone(areaNo,zone):
    for key,value in zone.items():
        try:
            addID(areaNo,key,value)
        except KeyError:
            # No id needed to replace - skip
            continue


def reset_vars():
    global used_ids_sprites, new_ids_sprites, used_ids
    used_ids_sprites = [defaultdict(list),defaultdict(list),defaultdict(list),defaultdict(list)]
    new_ids_sprites = [defaultdict(int),defaultdict(int),defaultdict(int),defaultdict(int)]

    used_ids = [{},{},{},{}]