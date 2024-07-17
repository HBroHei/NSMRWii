### THIS IS A TEST SCRIPT TO TEST THE OUTPUTTED JSON CAN BE ASSEMBLED INTO A PROPER LEVEL.
### IT SHOULD BE USED FOR TESTING ONLY

import json

import u8_m
import nsmbw
import globalVars
from Util import tilePosToObjPos, convertToDict, objPosToTilePos
from zone_random import checks,corrections

from random import randint, shuffle, choice
from copy import deepcopy
import traceback

inJson = {}

groupTilesetJson = {}
addedZone = {}

levelToImport = "01-01.arc"

zoneAddedNo = 0

entrance_list = [[],[],[],[]] # entrance_list[area_no][zone_no]["enterable"|"nonenterable"], no need to complicated things
area_enterable_count = [0,0,0,0]
area_nonenterable_count = [0,0,0,0]
area_zone = [[],[],[],[]]
area_zone_size = [[],[],[],[]]
area_tileset = ["","","",""]
area_len = 1

tileData = [[],[],[]]
u8_files_list = []

isDebug = False

def writeArea():
    pass

def addEntranceData(areaNo : int, zoneToFind:list):
    assert type(zoneToFind)==list or type(zoneToFind)==dict
    allEnt, allNonEnt = checks.findExitEnt(zoneToFind)
    entrance_list[areaNo].append({
        "enterable" : allEnt,
        "nonenterable" : allNonEnt
    })
    area_enterable_count[areaNo] += len(allEnt)
    area_nonenterable_count[areaNo] += len(allNonEnt)

# Adds a zone to the level
def addRandomZone(tilesetList:list,types:list):
    global zoneAddedNo, area_len, area_zone
    print("Determine extra")
    # Need an exit zone, and a "main" zone
    generated_zone, gen_zone_tileset, gen_zone_type = genZone(tilesetList,types)
    print("[D] Extra zone =",generated_zone["zone"])
    zoneAddedNo += 1
    # Check for overlap with zones
    if gen_zone_tileset==area_tileset[0]:
        # TODO Alright the statements below are repeated, but I am not bothering with it now.
        overlap_zone_no = checks.checkPosInZone(area_zone[0], *generated_zone[0:4])
        if overlap_zone_no!=-1:
            overlap_zone = area_zone[overlap_zone_no]
            if (overlap_zone[0]+overlap_zone[2]+64+generated_zone[2])>16000: # Should be a horizontal zone
                new_y = overlap_zone[1]+overlap_zone[3]+64
            if (overlap_zone[1]+overlap_zone[3]+64+generated_zone[3])>7800: # Should be a vertical zone
                # Both if statement needs to run in case of full area (To be implemented)
                new_x = overlap_zone[0]+overlap_zone[2]+64
            generated_zone = corrections.alignToPos(generated_zone,*tilePosToObjPos((new_x,new_y)))
        # Check and correct duplicated zones
        generated_zone = corrections.corrDupID(generated_zone)
        generated_zone = corrections.corrSprZone(generated_zone)
        generated_zone["type"] = "main"
        area_zone[0].append(generated_zone)

        return 0, gen_zone_tileset, gen_zone_type
    elif gen_zone_tileset==area_tileset[1]:
        overlap_zone_no = checks.checkPosInZone(area_zone[1], *generated_zone[0:4])
        if overlap_zone_no!=-1:
            overlap_zone = area_zone[overlap_zone_no]
            if (overlap_zone[0]+overlap_zone[2]+64+generated_zone[2])>16000: # Should be a horizontal zone
                new_y = overlap_zone[1]+overlap_zone[3]+64
            if (overlap_zone[1]+overlap_zone[3]+64+generated_zone[3])>7800: # Should be a vertical zone
                # Both if statement needs to run in case of full area (To be implemented)
                new_x = overlap_zone[0]+overlap_zone[2]+64
            generated_zone = corrections.alignToPos(generated_zone,*tilePosToObjPos((new_x,new_y)))
        # Check and correct duplicated zones
        generated_zone = corrections.corrDupID(generated_zone)
        generated_zone = corrections.corrSprZone(generated_zone)
        area_zone[1].append(generated_zone)

        return 1, gen_zone_tileset, gen_zone_type
    elif gen_zone_tileset==area_tileset[2]: # Area 3
        overlap_zone_no = checks.checkPosInZone(area_zone[2], *generated_zone[0:4])
        if overlap_zone_no!=-1:
            overlap_zone = area_zone[overlap_zone_no]
            if (overlap_zone[0]+overlap_zone[2]+64+generated_zone[2])>16000: # Should be a horizontal zone
                new_y = overlap_zone[1]+overlap_zone[3]+64
            if (overlap_zone[1]+overlap_zone[3]+64+generated_zone[3])>7800: # Should be a vertical zone
                # Both if statement needs to run in case of full area (To be implemented)
                new_x = overlap_zone[0]+overlap_zone[2]+64
            generated_zone = corrections.alignToPos(generated_zone,*tilePosToObjPos((new_x,new_y)))
        # Check and correct duplicated zones
        generated_zone = corrections.corrDupID(generated_zone)
        generated_zone = corrections.corrSprZone(generated_zone)
        area_zone[2].append(generated_zone)

        return 2, gen_zone_tileset, gen_zone_type
    else: # Esort to Area 4 I guess
        generated_zone = corrections.alignToPos(generated_zone,*tilePosToObjPos((32,32)))
        generated_zone = corrections.corrSprZone(generated_zone)
        area_zone[3].append(generated_zone)
        area_tileset[3] = gen_zone_tileset
        area_len+=1

        return 3, gen_zone_tileset, gen_zone_type
        # All that is done, back out from the if statement.
    

# NOTE This will remove the zone from the list
def getRandomZone(tilesetName:str, zone_type:str) -> dict:
    zone_json_idx = randint(0,len(groupTilesetJson[tilesetName][zone_type])-1)
    # zone_json_idx = 0
    # print(len(groupTilesetJson[area1_tileset][zone_ent_type]))
    return_zone = groupTilesetJson[tilesetName][zone_type][zone_json_idx]
    del groupTilesetJson[tilesetName][zone_type][zone_json_idx] # Remove added zone
    return return_zone

def getRandomTileset(tilesetList:list):
    return_tileset = tilesetList[randint(0,len(tilesetList)-1)]
    print("Using",return_tileset)
    # Seperating return statement since I never know I would be seperating them in the future
    return return_tileset

def getRandomEntrance(area_zone:list):
    area = choice(area_zone)
    while len(area)==0:
        area = choice(area_zone)
    zone = choice(area)
    while len(zone["entrance"])==0:
        zone = choice(area)
    return choice(zone["entrance"])

def checkDictListEmpty(d:dict,lst:list):
    for i_str in lst:
        if len(d[i_str])!=0: return False
    return True

# Generates a random zone from existing pool
def genZone(tilesetList:list,types:list):
    cur_tileset = getRandomTileset(tilesetList)
    #area_tileset[0] = "Pa0_jyotyuPa1_daishizen" ### DEBUG

    # Prevent area without an entrance
    while checkDictListEmpty(groupTilesetJson[cur_tileset],types):
        cur_tileset = getRandomTileset(tilesetList)
    
    # Check for only 1 specific entrance zone type
    # TODO Below unfinished
    try:
        if len(groupTilesetJson[cur_tileset][types[0]])==0:
            zone_ent_type = types[1]
        elif len(groupTilesetJson[cur_tileset][types[1]])==0:
            zone_ent_type = types[0]
        else:
            # zone_ent_type = "entrance" ### DEBUG
            zone_ent_type = choice(types) # Entrance only / Entranbce + exit
    except IndexError:
        zone_ent_type = types[0]
    #zone_ent_type = "full" ### DEBUG

    # Add the entrance zone
    ret_zone = getRandomZone(cur_tileset, zone_ent_type)
    #area_zone[0].append(ret_zone)

    # Adjust coordinates relative to the new level
    ret_zone = corrections.alignToPos(ret_zone,*tilePosToObjPos((32,32)))
    ret_zone = corrections.corrSprZone(ret_zone)

    # Add info
    #ret_zone["tileset"] = cur_tileset
    ret_zone["type"] = zone_ent_type

    # Return: zone, tileset, type
    return ret_zone, cur_tileset, ret_zone["type"]

def D_writeToFile(lvlData:list, areaNo = 1):
    no_of_areas = 0
    # List always starts with 0, so +1 needed
    for area_i in range(1,areaNo+1):
        area_arr_i = area_i-1 # To be used in lists
        areaData = lvlData[area_arr_i]
        print("len",len(areaData))
        areaRawSettings = []
        tileData = [[],[],[]]
        loadSprList = []
        for zoneNo in range(0,len(areaData)):
            print("[D] outputting area",area_i,"zone",zoneNo)
            cur_zone = areaData[zoneNo]
            if areaRawSettings==[]: # Area First-timer, add configs
                loadSprList += nsmbw.NSMBWLoadSprite.addLoadSprites(cur_zone["sprites"])
                pass
            ## finished adding config
            # Add tiles data
            for i in range(0,2): # Loop through each layer
                if "bgdatL"+str(i) in cur_zone.keys():
                    for tiles in cur_zone["bgdatL" + str(i)]:
                        tileData[i].append(tiles)
                    # Convert to byte data
                    u8_files_list.append(u8_m.constructArchiveFile_m("course" + str(area_i) + "_bgdatL" + str(i) + ".bin",nsmbw.NSMBWbgDat.toByteData(tileData[i])))
                    with open("course" + str(area_i) + "_bgdatL" + str(i) + ".bin", 'wb') as f:
                        f.write(nsmbw.NSMBWbgDat.toByteData(tileData[i]))
        # Add config
        # Prepare for Sprite loading list
        # TODO do this for all zones
        loadSprList = tuple(set(loadSprList))
        # Import settings one-by-one, in order from Section 0
        #print(cur_zone["tileset"])
        areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWtileset.toByteData(cur_zone["tileset"])))
        areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWAreaProp.toByteData(cur_zone["AreaSetting"])))
        areaRawSettings.append(nsmbw.generateSectionDef(cur_zone["ZoneBound"])) # TODO Convert this to list if needed
        areaRawSettings.append(nsmbw.generateSectionDef(cur_zone["AreaSetting2"]))
        areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWZoneBG.toByteData(cur_zone["topBackground"])))
        areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWZoneBG.toByteData(cur_zone["bottomBackground"])))
        areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWEntrances.toByteData(cur_zone["entrance"])))
        areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWsprite.toByteData(cur_zone["sprites"])))
        areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWLoadSprite.toByteData(loadSprList)))
        areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWZones.toByteData([cur_zone["zone"]])))
        areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWLocations.toByteData(cur_zone["location"])))
        areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWCamProfile.toByteData(cur_zone["cameraProfile"])))
        # areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWPathProperties.toByteData(cur_zone["path"])))
        # areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWPathNode.toByteData(cur_zone["pathNode"])))
        # Path: Special processing
        path_list = []
        path_node_list = []
        cur_start_node = 0
        for cur_pathzone in areaData:
            for cur_path in cur_pathzone["path"]:
                # Set the star node num
                cur_path[1] = cur_start_node
                # "Predict" next node pos
                cur_start_node += cur_path[2]
                path_list.append(cur_path)
            # Add path nodes
            path_node_list += cur_pathzone["pathNode"]
        # Check if len(path_node_list)+len(last_path)==cur_start_node
        print("[D]final list",path_list)
        print("[D]final path node",path_node_list)
        assert len(path_node_list)==cur_start_node, str(len(path_node_list)) + "!=" + str(cur_start_node)
        # Now they are ready to be added back to the list
        areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWPathProperties.toByteData(path_list)))
        areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWPathNode.toByteData(path_node_list)))
        # Write it to byte array
        u8_files_list.append(u8_m.constructArchiveFile_m("course" + str(area_i) + ".bin",nsmbw.writeDef(areaRawSettings)))
        no_of_areas +=1
    # Create "course" folder
    u8_files_dir = u8_m.constructArchiveFile_m("course",b"",True,len(u8_files_list)+2) # +2 for itself + root folder
    # Create u8_m dict for repacking
    u8_dict = u8_m.constructFromScratch(no_of_areas,[u8_files_dir] + u8_files_list)
    #print(u8_dict)

    returnARC = u8_m.repackToBytes(u8_dict)
    with open("test_json.arc", 'wb') as f:
        f.write(returnARC)

def main():
    global inJson, zoneAddedNo, area_zone, entrance_list
    with open('out.json', 'r') as f:
        json_orginal = json.load(f)
    inJson = convertToDict(json_orginal)

    # Group similar tilesets
    for key_lvl in inJson:
        for key_area in inJson[key_lvl]:
            for key_zone in inJson[key_lvl][key_area]:
                cur_zone = inJson[key_lvl][key_area][key_zone]
                cur_tileset_str = "".join([ba.decode() for ba in cur_zone["tileset"]]) # All tilesets
                # Add key to dict if dict does not have the key
                if cur_tileset_str not in groupTilesetJson.keys():
                    groupTilesetJson[cur_tileset_str] = {
                        "normal" : [] , # No Entrance / Exit
                        "entrance" : [], # Level entrance only
                        "full" : [], # Level entrance and exit
                        "exit" : [], # Level exit only
                        "boss" : [], # Boss in zone
                        "bonus" : [], # Only 1 entrance / same ent and exit
                        "count" : 0
                    }
                # Calculate number of zones for each tilesets
                groupTilesetJson[cur_tileset_str]["count"] += len(inJson[key_lvl][key_area].keys())

                # Check zone has exit / entrances
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
                """
                exit_flag = checks.checkExitSprite(cur_zone)
                ent_flag = checks.checkEntSpawn(cur_zone)
                boss_flag = checks.checkBossSprite(cur_zone)
                oneent_flag = checks.checkOnlyOneEnt(cur_zone)
                # Add the zone to its category
                if boss_flag==-1:
                    if exit_flag!=-1 and ent_flag!=-1:
                        groupTilesetJson[cur_tileset_str]["full"].append(cur_zone)
                    elif exit_flag!=-1:
                        groupTilesetJson[cur_tileset_str]["exit"].append(cur_zone)
                    elif ent_flag!=-1:
                        groupTilesetJson[cur_tileset_str]["entrance"].append(cur_zone)
                    elif oneent_flag:
                        groupTilesetJson[cur_tileset_str]["bonus"].append(cur_zone)
                    else:
                        groupTilesetJson[cur_tileset_str]["normal"].append(cur_zone)
                else:
                    groupTilesetJson[cur_tileset_str]["exit"].append(cur_zone)
    # print(groupTilesetJson["Pa0_jyotyuPa1_noharaPa2_doukutu"]["full"][1])
    # These will always be area 1, with exit zone as zone 0 in the level
    # TODO need to somehow equally divide each zones for all levels. Hoo boy

    """
        FOR EACH LEVEL
        1. Randomise and determine Area 1 tileset (will be Entrance and exit)
        2. Copy exit zone
        3. if exit zone = entrance zone, good. Skip to step 7
        4. if exit zone != entrance zone, find and copy an entrance zone
        5. Find zone that has 1 entrance and 1 exit (or more), and copy that zone (Create another area if necessary e.g. for tileset)
        6. Assign 1 entrance (from entrance zone) and 1 exit (to exit zone) randomly
        7. Fill out rest of entrance / exit randomly (Create another area if necessary e.g. for tileset)
        7a. For each sub-area exit, find an entrance in the previous zone, with PRIORITY for unassigned entrances
    """
    # TODO Set goal pole: normal / secret
    notFinished = True  #Temp
    tilesetList = list(groupTilesetJson.keys())
    zoneAddedNo = 0
    normal_exit_area_id = -1
    secret_exit_area_id = -1
    normal_exit_zone_id = -1
    secret_exit_zone_id = -1
    totNoEnt = 0 # Total number of enterables
    totNoNonEnt = 0 # Total number of non-enterables
    # copy dict template for addedZone
    addedZone = deepcopy(groupTilesetJson)
    while notFinished:
        entrance_list = [[],[],[],[]] # entrance_list[area_no][zone_no]["enterable"|"nonenterable"], no need to complicated things
        area_zone = [[],[],[],[]]
        area_zone_size = [[],[],[],[]]
        area_tileset = ["","","",""]
        area_len = 1
        only_main = False

        # Generate the entrance zone
        generated_ent_zone, gen_ent_zone_tileset, gen_ent_zone_type = genZone(tilesetList,["full","entrance"])
        spawn_zone = deepcopy(generated_ent_zone)    
        
        print("[D] Entrance Data",spawn_zone["entrance"])

        area_zone[0].append(spawn_zone)
        area_tileset[0] = gen_ent_zone_tileset
        zoneAddedNo += 1 # Number of zones added
        print("[D] Ent zone =",area_zone[0][-1]["zone"])
        addEntranceData(0,spawn_zone)

        if gen_ent_zone_type=="entrance":
            print("Determine exit")
            # Need an exit zone, and a "main" zone
            generated_exit_zone, gen_exit_zone_tileset, gen_exit_zone_type = genZone(tilesetList,["full","exit"])

            exit_zone = deepcopy(generated_exit_zone)
            print("[D] Exit zone =",exit_zone["zone"])
            exit_tileset = deepcopy(gen_exit_zone_tileset)
            # Check for overlap with zones
            if exit_tileset==area_tileset[0]:
                overlap_zone_no = checks.checkPosInZone(area_zone[0], *exit_zone[0:4])
                if overlap_zone_no!=-1:
                    overlap_zone = area_zone[overlap_zone_no]
                    if (overlap_zone[0]+overlap_zone[2]+64+exit_zone[2])>16000: # Should be a horizontal zone
                        new_y = overlap_zone[1]+overlap_zone[3]+64
                    if (overlap_zone[1]+overlap_zone[3]+64+exit_zone[3])>7800: # Should be a vertical zone
                        # Both if statement needs to run in case of full area (To be implemented)
                        new_x = overlap_zone[0]+overlap_zone[2]+64
                    exit_zone = corrections.alignToPos(exit_zone,*tilePosToObjPos((new_x,new_y)))
                # Check and correct duplicated zones
                exit_zone = corrections.corrDupID(exit_zone)
                exit_zone = corrections.corrSprZone(exit_zone)
                area_zone[0].append(exit_zone)
                # Add entrances of this zone to known entrances list
                addEntranceData(0,exit_zone)
                normal_exit_area_id = 0
                normal_exit_zone_id = len(area_zone[0])-1
            else:
                exit_zone = corrections.alignToPos(exit_zone,*tilePosToObjPos((32,32)))
                area_zone[1].append(exit_zone)
                area_tileset[1] = exit_tileset
                addEntranceData(1,exit_zone)
                normal_exit_zone_id = len(area_zone[1])-1
                normal_exit_area_id = 1
                area_len+=1

            zoneAddedNo += 1

            # Generate the main area
            print("Determine main")
            main_tileset = getRandomTileset(tilesetList)
            # Prevent area without exit
            while len(groupTilesetJson[main_tileset]["normal"])==0:
                main_tileset = getRandomTileset(tilesetList)
            ### DEBUGGING
            # zone_ent_type = "full"
            # exit_tileset = "Pa0_jyotyuPa2_sora"

            # Gets the random zone
            main_zone = getRandomZone(main_tileset,"normal")
            print("[D] Main zone =",main_zone["zone"])
            # Check for overlap with zones
            if main_tileset==area_tileset[0]:
                # TODO Alright the statements below are repeated, but I am not bothering with it now.
                overlap_zone_no = checks.checkPosInZone(area_zone[0], *main_zone[0:4])
                if overlap_zone_no!=-1:
                    overlap_zone = area_zone[overlap_zone_no]
                    if (overlap_zone[0]+overlap_zone[2]+64+main_zone[2])>16000: # Should be a horizontal zone
                        new_y = overlap_zone[1]+overlap_zone[3]+64
                    if (overlap_zone[1]+overlap_zone[3]+64+exit_zone[3])>7800: # Should be a vertical zone
                        # Both if statement needs to run in case of full area (To be implemented)
                        new_x = overlap_zone[0]+overlap_zone[2]+64
                    main_zone = corrections.alignToPos(main_zone,*tilePosToObjPos((new_x,new_y)))
                # Check and correct duplicated zones
                main_zone = corrections.corrDupID(main_zone)
                main_zone = corrections.corrSprZone(main_zone)
                main_zone["type"] = "main"
                area_zone[0].append(main_zone)
                # Add entrances in zone to list of entrances
                addEntranceData(0,main_zone)
            elif main_tileset==area_tileset[1]:
                overlap_zone_no = checks.checkPosInZone(area_zone[1], *main_zone[0:4])
                if overlap_zone_no!=-1:
                    overlap_zone = area_zone[overlap_zone_no]
                    if (overlap_zone[0]+overlap_zone[2]+64+main_zone[2])>16000: # Should be a horizontal zone
                        new_y = overlap_zone[1]+overlap_zone[3]+64
                    if (overlap_zone[1]+overlap_zone[3]+64+exit_zone[3])>7800: # Should be a vertical zone
                        # Both if statement needs to run in case of full area (To be implemented)
                        new_x = overlap_zone[0]+overlap_zone[2]+64
                    main_zone = corrections.alignToPos(main_zone,*tilePosToObjPos((new_x,new_y)))
                # Check and correct duplicated zones
                main_zone = corrections.corrDupID(main_zone)
                main_zone = corrections.corrSprZone(main_zone)
                area_zone[1].append(main_zone)
                # Add entrances in zone to list of entrances
                addEntranceData(1,main_zone)
            else: # Esort to Area 3 I guess
                main_zone = corrections.alignToPos(main_zone,*tilePosToObjPos((32,32)))
                main_zone = corrections.corrSprZone(main_zone)
                area_zone[2].append(main_zone)
                area_tileset[2] = main_tileset
                # Add entrances in zone to list of entrances
                addEntranceData(2,main_zone)
                area_len+=1
                # All that is done, back out from the if statement.

            zoneAddedNo += 1
        else:
            main_zone = spawn_zone # Only for programmer's viewing sake, shouldn't do anything lol
            only_main = True # This, however, is to mark which entrance will be prioritised to be randomised
        
        #### END OF ADDING THE NECESSARY ZONES ####
        ### Check if new zones is needed to be added
        # I believe there is a better wauy to do this, but this will do for now
        for area_no in range(0,4):
            # GEts a list of non-enterables excluding the current one
            lst_nonent_wo_myself = deepcopy(area_nonenterable_count)
            del lst_nonent_wo_myself[area_no]
            print("Checking new zone:",lst_nonent_wo_myself,area_enterable_count[area_no])
            # if the sum of non-enterables < enterable, new zone needed
            if sum(lst_nonent_wo_myself)<area_enterable_count[area_no]:
                print("NEW ZONE NEEDED, PLEASE ADD CODE HERE")
                added_area_no, added_tileset, added_type= addRandomZone([tileset_ for tileset_ in area_tileset if tileset_!=""],["full"])
                print("Extra:",added_area_no)
                print("Extra:",area_zone[added_area_no][-1]["zone"],)
                addEntranceData(area_no,area_zone[added_area_no][-1])

        print("Nonenterable list",area_nonenterable_count)
        print("   enterable list",area_enterable_count)
        #### CALCULATE THE NECESSARRY ENTRANCES / EXITS, AND ADDITIONAL ZONES ####
        # Well first, if there are no enterables, we can skip all "these codes"
        if sum(area_enterable_count)!=0:
            # First is Area 1 (0), which is always the spawn of the level
            cur_start_area = 0
            cur_start_zone = 0
            cur_start_ent_pos = entrance_list[cur_start_area][cur_start_zone]["enterable"][-1]
            cur_dest_area = -1
            cur_dest_zone = -1
            cur_dest_ent_pos = -1
            prev_start_area = 0
            prev_start_zone = 0
            processed_ent_count = 0
            processed_enterable_id = [
                [[] for _ in range(len(entrance_list[0]))],
                [[] for _ in range(len(entrance_list[1]))],
                [[] for _ in range(len(entrance_list[2]))],
                [[] for _ in range(len(entrance_list[3]))]
            ] # Storing randomised entrance ids
            print("Processed_Ent_Ids",processed_enterable_id)
            processed_nonent_id = [[],[],[],[]] # Storing randomised exit ids
            processed_normal_exit_zone = False
            processed_secret_exit_zone = False # For future use, dont implement it just yet

            entrance_assign_list = []

            if only_main:
                rando_priority_lst = []
            else:
                rando_priority_lst = [2,1]

            # Add nonents to the nonent list
            nonent_list = [[],[],[],[]]
            for area_id in range(0,3):
                for zone_pos in range(0,len(entrance_list[area_id])):
                    nonent_list[area_id] = [(zone_pos, exit_pos) for exit_pos in entrance_list[area_id][zone_pos]["nonenterable"]]

            # Assign entrances
            for area_id in range(0,3):
                for zone_pos in range(0,len(area_zone[area_id])):
                    #for zone_info in area_zone[area_id][zone_pos]:
                        for entrance_pos in entrance_list[area_id][zone_pos]["enterable"]:
                            # Find suitable exit
                            exit_found = False
                            # Check assigned
                            ent_key = str(area_id) + "_" + str(zone_pos) + "_" + str(entrance_pos)
                            if ent_key in entrance_assign_list:
                                continue
                            # 1. Destination Area
                            # find random area'
                            # Check if there are priority
                            if len(rando_priority_lst)==0:
                                area_lists_choice = [0,1,2,3]
                                dest_area_id = choice(area_lists_choice)
                                round_count = 0
                                while dest_area_id==area_id or len(nonent_list[dest_area_id])==0:
                                    dest_area_id += 1
                                    if dest_area_id>3: dest_area_id = 0
                                    round_count+=1
                                    if round_count == 4: break
                            else:
                                dest_area_id = rando_priority_lst.pop(0)
                                print("Priority: Area set to",dest_area_id)
                                
                            if len(nonent_list[dest_area_id])!=0: # Area exist?
                                exit_key = choice(nonent_list[dest_area_id])
                                print("Ent key",ent_key)
                                print("exit key",exit_key)
                                # Set value to exit_key
                                area_zone[area_id][zone_pos]["entrance"][entrance_pos][3] = dest_area_id+1
                                area_zone[area_id][zone_pos]["entrance"][entrance_pos][4] =\
                                    area_zone[dest_area_id][exit_key[0]]["entrance"][exit_key[1]][2]

                                nonent_list[dest_area_id].remove(exit_key)
                                entrance_assign_list.append(ent_key)
                                exit_found = True
                            # 3. Any Area (Last Resort)
                            if not exit_found:
                                for _area_id in range(0,3):
                                    if nonent_list[_area_id]:
                                        exit_key = choice(nonent_list[_area_id])
                                        print("3. Area ID", _area_id)
                                        print("3. ENT key",ent_key)
                                        print("3. EXIT key",exit_key)
                                        # Set value to exit_key
                                        area_zone[area_id][zone_pos]["entrance"][entrance_pos][3] = _area_id+1
                                        area_zone[area_id][zone_pos]["entrance"][entrance_pos][4] =\
                                            area_zone[_area_id][exit_key[0]]["entrance"][exit_key[1]][2]
                                        
                                        nonent_list[_area_id].remove(exit_key)
                                        entrance_assign_list.append(ent_key)
                                        exit_found = True
                                        break

                            if not exit_found:
                                # Handle no exit found (e.g., add a new exit, adjust entrance, raise error)
                                print(f"No suitable exit found for entrance: {ent_key}")
                                # Esort to a random entrance at the exit area
                                # TODO I wish there is a better way to handle this situation
                                dest_area_id = 0 if only_main else 1
                                area_zone[area_id][zone_pos]["entrance"][entrance_pos][3] = dest_area_id
                                area_zone[area_id][zone_pos]["entrance"][entrance_pos][4] =\
                                    choice(area_zone[dest_area_id][0]["entrance"])[2]
            ### OLD CODES
            """# While not all enterable processed and exit area nonenterable linked
            while processed_ent_count < sum(area_enterable_count)-1 or not processed_normal_exit_zone:
                # Starts randoming
                # Get the Dest Area
                cur_dest_area = randint(0,3)
                #print("Decided init dest area id",cur_dest_area)
                # Avoid area without enterable, and same area
                # We can safely assume every zone have at least 1 non-enterable entrance
                while cur_dest_area==cur_start_area or area_nonenterable_count[cur_dest_area]==0:
                    cur_dest_area = randint(0,3)
                print("Decided dest area id",cur_dest_area)
                # Get the dest zone
                cur_dest_zone = randint(0,len(entrance_list[cur_dest_area])-1)
                # Get the Dest Entrance POSITION in entrance_list
                # Preferrably Non-Enterable
                print("Dest zone",cur_dest_zone,entrance_list[cur_dest_area])
                cur_dest_ent_pos = choice(entrance_list[cur_dest_area][cur_dest_zone]["nonenterable"])
                # Assign them to the current processing enterable
                area_zone[cur_start_area][cur_start_zone]["entrance"][cur_start_ent_pos][3] = cur_dest_area+1
                area_zone[cur_start_area][cur_start_zone]["entrance"][cur_start_ent_pos][4] =\
                    area_zone[cur_dest_area][cur_dest_zone]["entrance"][cur_dest_ent_pos][2]
                # Add to enterable processed list
                processed_enterable_id[cur_start_area][cur_start_zone].append(cur_start_ent_pos)
                if cur_dest_area==normal_exit_area_id and cur_dest_zone==normal_exit_zone_id:
                    processed_normal_exit_zone = True
                prev_start_area = cur_start_area; prev_start_zone = cur_start_zone
                # Get a random enterable from the zone
                # If none, esort to other zone in area, then other area
                cur_start_area = cur_dest_area
                cur_start_zone = cur_dest_zone
                # Gets the random enterable
                if len(entrance_list[cur_start_area][cur_start_zone]["enterable"])!=0:
                    cur_start_ent_pos_i = randint(0,len(entrance_list[cur_start_area][cur_start_zone]["enterable"])-1)
                    cur_start_ent_pos = entrance_list[cur_start_area][cur_start_zone]["enterable"][cur_start_ent_pos_i]
                else:
                    cur_start_ent_pos = -1
                    cur_start_ent_pos_i = 0
                while (prev_start_area==cur_dest_area and prev_start_zone==cur_dest_zone)\
                    or cur_start_zone>len(entrance_list[cur_start_area])-1\
                    or cur_start_ent_pos_i>len(entrance_list[cur_start_area][cur_start_zone]["enterable"])-1\
                    or cur_start_ent_pos in processed_enterable_id[cur_start_area][cur_start_zone]\
                    or cur_start_ent_pos==-1:
                    print("area=",cur_start_area,"zone=",cur_start_zone)
                    print("var =",cur_start_ent_pos, processed_enterable_id[cur_start_area])
                    print("0.",(prev_start_area==cur_dest_area and prev_start_zone==cur_dest_zone))
                    print("1.",cur_start_zone>len(entrance_list[cur_start_area])-1)
                    try:
                        print("2.",cur_start_ent_pos_i>len(entrance_list[cur_start_area][cur_start_zone]["enterable"])-1)
                        print("3,4.",cur_start_ent_pos in processed_enterable_id[cur_start_area][cur_start_zone],cur_start_ent_pos==-1)
                    except IndexError:
                        pass

                    # Zone oob: area+1
                    if cur_start_zone>=len(entrance_list[cur_start_area]):
                        print("Adding area number", cur_start_area)
                        cur_start_area += 1
                        if cur_start_area>=4: cur_start_area = 0
                        cur_start_zone = 0
                        cur_start_ent_pos_i = 0
                    # Add zone no
                    elif (prev_start_area==cur_dest_area and prev_start_zone==cur_dest_zone)\
                        or cur_start_ent_pos_i>=len(entrance_list[cur_start_area][cur_start_zone]["enterable"]):
                        print("Adding zone number", cur_start_zone)
                        cur_start_zone+=1
                        cur_start_ent_pos_i = 0
                    else:
                        # Add entrance pos number
                        cur_start_ent_pos_i+=1
                        print("Adding ent pos i",cur_start_ent_pos_i)
                    # Ent processed - add ent no (NOT NECESARY as we have already added i above)
                    if cur_start_ent_pos in processed_enterable_id[cur_start_area][cur_start_zone]:
                        cur_start_ent_pos_i+=1
                        # Do not set cur_start_ent_pos yet as it may produce IndexError
                    print("Trying to set var")
                    # Now, try setting cur_dest_ent_pos
                    try:
                        cur_start_ent_pos = entrance_list[cur_start_area][cur_start_zone]["enterable"][cur_start_ent_pos_i]
                    except IndexError as e: # Something is wrong, continue looping
                        print("Something went wrong, continue loop:",traceback.format_exc())
                        cur_start_ent_pos = -1
                        input("")
            ### OLDER CODES BELOW

                
                # While:
                #   1. zone has no enterable, or
                #   2. enterable has been processed, or
                #   3. same area, same zone, or
                #   4. enterable_i is oob for list entrance_list[cur_start_area][cur_start_zone]["enterable"], or
                #   5. cur_start_ent_pos is None
                while len(entrance_list[cur_start_area][cur_start_zone]["enterable"])==0\
                    or cur_start_ent_pos in processed_enterable_id[cur_start_area][cur_start_zone]\
                    or (prev_start_area==cur_start_area and prev_start_zone==cur_start_zone)\
                    or cur_start_ent_pos_i>=len(entrance_list[cur_start_area][cur_start_zone]["enterable"])\
                    or cur_start_ent_pos==None:
                    # Order: other ent -> other zone -> other area
                    # TODO while loop unfinished
                    # is enterable processed? / i oob? / no enterable in zone?
                    if cur_start_ent_pos in processed_enterable_id[cur_start_area][cur_start_zone]\
                        or len(entrance_list[cur_start_area][cur_start_zone]["enterable"])==0\
                        or cur_start_ent_pos_i>=len(entrance_list[cur_start_area][cur_start_zone]["enterable"]): # This is here so that it will go to next zone
                        cur_start_ent_pos_i += 1
                        print("Next entrance pls")
                        # Is enterable oob? / no enterable in zone?
                        if cur_start_ent_pos==None\
                            or (cur_start_ent_pos_i>len(entrance_list[cur_start_area][cur_start_zone]["enterable"])-1):
                            cur_start_zone += 1 # Go to next zone
                            print("Next zone pls")
                            # If no more zone, go to next area
                            if cur_start_zone>len(entrance_list[cur_start_area])-1:
                                print("Next area pls")
                                cur_start_area+=1
                                cur_start_zone = 0
                                if cur_start_area>=4: # reset to area 1
                                    print("area 1 pls")
                                    cur_start_area = 0
                                if cur_start_area==cur_dest_area:
                                    print("what this should be impossible")
                                    exit()
                    else:
                        cur_start_ent_pos = entrance_list[cur_start_area][cur_start_zone]["enterable"][cur_start_ent_pos_i]

                # End of inner loop
                
                
                processed_ent_count+=1 # Processed an enterable
                print("Entering",processed_ent_count,"loop")
            # End of outer loop
        # End of "these codes"

        ### EVEN OLDER CODES BELOW \/ \/ \/

        for area_no in range(0,4):
            # If area does not contain enterable, skip pls
            if area_enterable_count[area_no]==0:
                continue
            print("Randomising Area",area_no)
            # Gets the entrance list of the level
            for area_zone_list_i in range(0,len(entrance_list[area_no])):
                # Gets the number of enterables and non-enterables 
                zone_ent_no = len(entrance_list[area_no][area_zone_list_i]["enterable"])
                zone_nonent_no = len(entrance_list[area_no][area_zone_list_i]["nonenterable"])
                print("LIST Com",len(entrance_list[area_no]),len(area_zone[area_no]))
                print("For",area_zone_list_i,": Enterable=",zone_ent_no,", nonEnt=",zone_nonent_no)
                for zone_enterable_i in entrance_list[area_no][area_zone_list_i]["enterable"]:
                    # zone_enterable_i = entrance_list[area_no][area_zone_list_i]["enterable"][i]
                    print("Randomising:",area_zone[area_no][area_zone_list_i]["entrance"][zone_enterable_i])
                    # Starts randoming
                    # Get the Dest Area
                    dest_area_id = randint(0,3)
                    #print("Decided init dest area id",dest_area_id)
                    # Avoid area without enterable, and same area
                    # We can safely assume every zone have at least 1 non-enterable entrance
                    while dest_area_id==area_no or area_nonenterable_count[dest_area_id]==0:
                        dest_area_id = randint(0,3)
                    print("Decided dest area id",dest_area_id)
                    # Get the dest zone
                    dest_zone_id = randint(0,len(entrance_list[dest_area_id])-1)
                    # Get the Dest Entrance ID
                    # Preferrably Non-Enterable
                    print("Dest zone",dest_zone_id,entrance_list[dest_area_id])
                    dest_ent_id_pos = choice(entrance_list[dest_area_id][dest_zone_id]["nonenterable"])
                    # Assign them to the current processing enterable
                    area_zone[area_no][area_zone_list_i]["entrance"][zone_enterable_i][3] = dest_area_id+1
                    area_zone[area_no][area_zone_list_i]["entrance"][zone_enterable_i][4] =\
                        area_zone[dest_area_id][dest_zone_id]["entrance"][dest_ent_id_pos][2]
                    # TODO After this, pick one enterable from dest area + zone id to be randomised,
                    # avoid going back to the prev. area to minimise circular loop"""

        ### THE CODE BELOW ARE THE OLDEST, TOO MESSY AND TOO COMPLICATED ###
        """# TODO Next step: link all zones tgt + gen deadends for extra exit / entrances
        # Get lists of enterable and non-enterable entrance
        area_ent = [] # Each area 1 new list
        # Structure: area_ent [Area No] [Exit=1 | Entrance=0] [Zone No] [0=AreaNo | 1=ZoneNo | 2=EntranceIDs]
        CONST_EXIT = 1; CONST_ENT = 0 # For viewing sake
        CONST_AREANO = 0; CONST_ZONENO = 1; CONST_ENTIDS = 2
        area_totExit = 0 # No. of exits
        for i in range(0,len(area_zone)):
            area_zone_ent = []
            area_zone_onlyEnt = []
            # Get list of zones in area_zone
            for j in range(0,len(area_zone[i])):
                ent_exits, ent_onlyEnt = checks.findExitEnt(area_zone[i][j]) # get entrancess in zone
                if len(ent_exits)!=0: # Only add if list is not empty
                    area_totExit += len(ent_exits) # TODO check len, it shouldn't only have 1
                    area_zone_ent.append((i,j,ent_exits)) # add to list
                if len(ent_onlyEnt)!=0: # Only add if list is not empty
                    area_zone_onlyEnt.append((i,j,ent_onlyEnt))
            # Shuffle list to achieve randomness since it will be processes as a *queue* below
            shuffle(area_zone_ent)
            shuffle(area_zone_onlyEnt)
            area_ent.append([area_zone_ent,area_zone_onlyEnt])
        # Randomise and pair entrances
        exit_idx = [0 for _ in range(0,len(area_zone))]
        print("Loop count:",area_totExit)
        # while not all enterables have a dest
        while area_totExit>0: # TODO area_totExit is 0???
            print("############ Looping:",area_totExit,"left ############")
            # Get a random area
            cur_process_area = randint(0,len(area_ent)-1)
            init_val = cur_process_area
            # while the area id hasnt loopback, has available enterable ent and no new zone needed
            while zoneAddedNo!=1 and (len(area_ent[cur_process_area][CONST_ENT])==0 or len(area_ent[cur_process_area][CONST_ENT][0][CONST_ENTIDS])==0):
                cur_process_area+=1 # Add if the chosen area does not have an enterable
                if cur_process_area>len(area_ent)-1: cur_process_area=0 # Resets if exceed limit
            # Generate new room if only 1 zone for extra enterable pipes
            if zoneAddedNo==1:
                # TODO Add zone
                # TODO This step needs to be done BEFORE we are in the random entrance process
                print("New zone needed, please interrupt")
                print("New zone needed, please interrupt")
                print("New zone needed, please interrupt")
                print("New zone needed, please interrupt")
                print("New zone needed, processing")
                added_area_no, added_tileset, added_type= addRandomZone([tileset_ for tileset_ in area_tileset if tileset_!=""],["full"])
                print("Extra:",added_area_no)
                print("Extra:",area_zone[added_area_no][-1]["zone"],)
                # exit()
                pass
            
            print("Entrance Area:",cur_process_area)
            # Get the exit area id
            print("Randomising range",0,len(area_ent)-1)
            cur_p_exit_area_no = randint(0,len(area_ent)-1)
            init_val = cur_p_exit_area_no
            print("[D] Exit area ID =", init_val)
            #while there is no ent in the current area (No zone that contain ent)
            while len(area_ent[cur_p_exit_area_no][CONST_EXIT])==0 or cur_p_exit_area_no==cur_process_area:
                print("exit",cur_p_exit_area_no,area_ent[cur_p_exit_area_no][CONST_EXIT])
                cur_p_exit_area_no+=1 # Add if the chosen area does not have an enterable
                if cur_p_exit_area_no>len(area_ent)-1: cur_p_exit_area_no=0
                if cur_p_exit_area_no==init_val:
                    # No exit?
                    print("WARNING: NO EXIT, Exiting")
                    exit()
                    pass
            print("Decided: final exit area id =",cur_p_exit_area_no)
            # Get the exit ent pos (randomise)
            cur_p_exit_zone_no = randint(0,len(area_ent[cur_p_exit_area_no][CONST_EXIT])-1)
            init_val = cur_p_exit_zone_no
            # Repeat until it is not empty
            # TODO If onlyExit list are all empty, get a new room (or pull of an existing enterable entrance)
            determinedExit = False
            while len(area_ent[cur_p_exit_area_no][CONST_EXIT][cur_p_exit_zone_no][CONST_ENTIDS])==0:
                cur_p_exit_zone_no+=1 # Add if the chosen zone does not have an entrance
                if cur_p_exit_zone_no>len(area_ent[cur_p_exit_area_no][CONST_EXIT])-1: cur_p_exit_zone_no=0
                if cur_p_exit_zone_no==init_val: # All list empty
                    determinedExit = True
                    dest_entData = getRandomEntrance(area_zone) # Gets random entrance (ignore used entrance)
                    break
            # Gets the random Entrance's ID
            if not determinedExit: # Random entrance was not set
                cur_process_exit_ent = randint(0,len(area_ent[cur_p_exit_area_no][CONST_EXIT][cur_p_exit_zone_no][CONST_ENTIDS])-1)
                cur_p_exit_area_zID = area_ent[cur_p_exit_area_no][CONST_EXIT][cur_p_exit_zone_no][CONST_ZONENO] # Unnecessary?
                dest_entData = area_zone[cur_p_exit_area_no][cur_p_exit_area_zID]["entrance"][area_ent[cur_p_exit_area_no][CONST_EXIT][cur_p_exit_zone_no][CONST_ENTIDS][cur_process_exit_ent]] # Gets the destination ent data
                # Waxed Lightly Weathered Cut Copper Stairs
            
            # Get their zone IDs as they are shuffled so they are not in order?
            cur_p_ent_area_zID = int(area_ent[cur_process_area][CONST_ENT][0][CONST_ZONENO]) # Unnecessary?
            # print("1",area_ent[cur_process_area][CONST_ENT][0])
            exit_entData = area_zone[cur_process_area][cur_p_ent_area_zID]["entrance"][int(area_ent[cur_process_area][CONST_ENT][0][CONST_ENTIDS][0])] # Gets the enterable entrance data
            
            #print("2",area_ent[cur_p_exit_area_no][CONST_EXIT][cur_p_exit_zone_no][CONST_ENTIDS],cur_process_exit_ent)
            
            #print("[D]", cur_process_area, exit_entData, "->", cur_p_exit_area_no,dest_entData)
            exit_entData[3] = cur_p_exit_area_no+1 # Set area
            print("Setting area id",cur_p_exit_area_no)
            exit_entData[4] = dest_entData[2] # Set ID
            area_zone[cur_process_area][cur_p_ent_area_zID]["entrance"][int(area_ent[cur_process_area][CONST_ENT][0][CONST_ENTIDS][0])] = exit_entData
            if not determinedExit: # Not an extra entrance
                del area_ent[cur_p_exit_area_no][CONST_EXIT][cur_p_exit_zone_no][CONST_ENTIDS][cur_process_exit_ent] # Remove from list
            del area_ent[cur_process_area][CONST_ENT][0][CONST_ENTIDS][0] # remove from list

            exit_idx[cur_process_area] += 1
            area_totExit-=1 # Countdown to 0"""
            

        print("Area len",area_len)
        D_writeToFile(area_zone,area_len)
        exit() ######## TEMP ########


    ################# OLD CODES ###################
    for areaNo in inJson[levelToImport].keys():
        for zoneNo in inJson[levelToImport][areaNo].keys():
            cur_zone = inJson[levelToImport][areaNo][zoneNo]
            areaRawSettings = []
            # Prepare for Sprite loading list
            loadSprList = nsmbw.NSMBWLoadSprite.addLoadSprites(cur_zone["sprites"])
            # Import settings one-by-one, in order from Section 0
            areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWtileset.toByteData(cur_zone["tileset"])))
            areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWAreaProp.toByteData(cur_zone["AreaSetting"])))
            areaRawSettings.append(nsmbw.generateSectionDef(cur_zone["ZoneBound"])) # TODO Convert this to list if needed
            areaRawSettings.append(nsmbw.generateSectionDef(cur_zone["AreaSetting2"]))
            areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWZoneBG.toByteData(cur_zone["topBackground"])))
            areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWZoneBG.toByteData(cur_zone["bottomBackground"])))
            areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWEntrances.toByteData(cur_zone["entrance"])))
            areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWsprite.toByteData(cur_zone["sprites"])))
            areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWLoadSprite.toByteData(loadSprList)))
            areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWZones.toByteData([cur_zone["zone"]])))
            areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWLocations.toByteData(cur_zone["location"])))
            areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWCamProfile.toByteData(cur_zone["cameraProfile"])))
            areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWPathProperties.toByteData(cur_zone["path"])))
            areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWPathNode.toByteData(cur_zone["pathNode"])))
            
            # Write it to byte array
            u8_files_list.append(u8_m.constructArchiveFile_m("course" + areaNo + ".bin",nsmbw.writeDef(areaRawSettings)))

            # Add tiles data
            for i in range(0,2): # Loop through each layer
                if "bgdatL"+str(i) in cur_zone.keys():
                    for tiles in cur_zone["bgdatL" + str(i)]:
                        tileData[i].append(tiles)
                    # Convert to byte data
                    u8_files_list.append(u8_m.constructArchiveFile_m("course" + areaNo + "_bgdatL" + str(i) + ".bin",nsmbw.NSMBWbgDat.toByteData(tileData[i])))
                    # TODO Output the file as a U8 archive
                    if isDebug:
                        with open("course" + areaNo + "_bgdatL" + str(i) + ".bin", 'wb') as f:
                            f.write(nsmbw.NSMBWbgDat.toByteData(tileData[i]))
                
    # Create "course" folder
    u8_files_dir = u8_m.constructArchiveFile_m("course",b"",True,len(u8_files_list)+2) # +2 for itself + root folder
    # Create u8_m dict for repacking
    u8_dict = u8_m.constructFromScratch(len(inJson[levelToImport].keys()),[u8_files_dir] + u8_files_list)

    returnARC = u8_m.repackToBytes(u8_dict)
    with open("test_json.arc", 'wb') as f:
        f.write(returnARC)

    pass

if __name__=="__main__":
    main()