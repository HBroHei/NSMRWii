### THIS IS A TEST SCRIPT TO TEST THE OUTPUTTED JSON CAN BE ASSEMBLED INTO A PROPER LEVEL.
### IT SHOULD BE USED FOR TESTING ONLY

import json

import u8_m
import nsmbw
import globalVars
from Util import tilePosToObjPos, convertToDict, objPosToTilePos
from zone_random import checks,corrections, read_config

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

# Add data to the list of enterables / nonenterables
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
        overlap_zone_no = checks.checkPosInZone(area_zone[3], *generated_zone[0:4])
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
        area_zone[3].append(generated_zone)

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

    # Prevent:
    # - area without an entrance
    # - no suitable place to place the zone
    while checkDictListEmpty(groupTilesetJson[cur_tileset],types) or\
        (cur_tileset not in area_tileset and "" not in area_tileset):
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

def writeToFile(lvlName:str, lvlData:list, areaNo = 1):
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
    with open("./Stage_output/" + lvlName, 'wb') as f:
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
    for stg_name in read_config.listdir("./Stage_temp/"):
        print("Processing",stg_name)
        if stg_name=="Texture":
            continue # Skip that folder

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
        ### Check if new zones is needed to be added - for:
        # - Entrances > exit number
        # - have secret exit
        # I believe there is a better wauy to do this, but this will do for now
        have_secret = stg_name in read_config.secret_exit
        secret_generated = False
        ent_pipes_cand = []
        for area_no in range(0,4):
            # GEts a list of non-enterables excluding the current one
            lst_nonent_wo_myself = deepcopy(area_nonenterable_count)
            del lst_nonent_wo_myself[area_no]
            print("Checking new zone:",lst_nonent_wo_myself,area_enterable_count[area_no])
            # if the sum of non-enterables < enterable, new zone needed
            if sum(lst_nonent_wo_myself)<area_enterable_count[area_no]:
                print("NEW ZONE NEEDED, PLEASE ADD CODE HERE")
                # If there is an secret exit in this level, set type to "exit", "full" otherwise
                added_area_no, added_tileset, added_type= addRandomZone([tileset_ for tileset_ in area_tileset if tileset_!=""],["exit"] if have_secret else ["full"])
                print("Extra:",added_area_no)
                print("Extra:",area_zone[added_area_no][-1]["zone"])
                addEntranceData(area_no,area_zone[added_area_no][-1])

                secret_generated = True
            # Checks for static pipes that is candidate for new enterable
            for zone_check in area_zone[area_no]:
                for tile in zone_check["bgdatL1"]:
                    if tile[0] in [65,73,79]:
                        ent_pipes_cand.append((area_no,tile))
                # I believe this is the right opportunity to do tile randomisation
                # Layer 1 matters the most
                zone_check["bgdatL1"] = nsmbw.NSMBWbgDat.processTiles(zone_check["bgdatL1"])
        # Check if have secret exit
        if have_secret and not secret_generated:
            # Option 1: have pipe candidate(s), only 1 new zone needed
            if len(ent_pipes_cand)!=0:
                print("1 ZONE NEEDED FOR SECRET, PLEASE ADD CODE HERE")
                ent_pipe = choice(ent_pipes_cand)
                # TODO add entrance
                added_area_no, added_tileset, added_type= addRandomZone([tileset_ for tileset_ in area_tileset if tileset_!=""],["exit"] if have_secret else ["full"])
                print("Extra:",added_area_no)
                print("Extra:",area_zone[added_area_no][-1]["zone"])
                addEntranceData(area_no,area_zone[added_area_no][-1])
            # Option 2: Generate 2 exita zones (Last resort)
            else:
                print("2 ZONES NEEDED FOR SECRET, PLEASE ADD CODE HERE")
                added_area_no, added_tileset, added_type= addRandomZone([tileset_ for tileset_ in area_tileset if tileset_!=""],["exit"] if have_secret else ["full"])
                print("Extra 1:",added_area_no)
                print("Extra 1:",area_zone[added_area_no][-1]["zone"])
                addEntranceData(area_no,area_zone[added_area_no][-1])
                added_area_no, added_tileset, added_type= addRandomZone([tileset_ for tileset_ in area_tileset if tileset_!=""],["exit"] if have_secret else ["full"])
                print("Extra 2:",added_area_no)
                print("Extra 2:",area_zone[added_area_no][-1]["zone"])
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
            

        print("Area len",area_len)
        writeToFile(stg_name,area_zone,area_len)
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