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

inJson = {}

groupTilesetJson = {}
addedZone = {}

levelToImport = "01-01.arc"

zoneAddedNo = 0

tileData = [[],[],[]]
u8_files_list = []

isDebug = False

def writeArea():
    pass

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
    if len(groupTilesetJson[cur_tileset][types[0]])==0:
        zone_ent_type = types[1]
    elif len(groupTilesetJson[cur_tileset][types[1]])==0:
        zone_ent_type = types[0]
    else:
        # zone_ent_type = "entrance" ### DEBUG
        zone_ent_type = choice(types) # Entrance only / Entranbce + exit
    #zone_ent_type = "full" ### DEBUG

    # Add the entrance zone
    ret_zone = getRandomZone(cur_tileset, zone_ent_type)
    #area_zone[0].append(ret_zone)

    # Adjust coordinates relative to the new level
    ret_zone = corrections.alignToPos(ret_zone,*tilePosToObjPos((32,32)))
    ret_zone = corrections.corrSprZone(ret_zone)
    ret_zone["type"] = "entrance" if zone_ent_type=="entrance" else "main"

def D_writeToFile(lvlData:list, areaNo = 1):
    no_of_areas = 0
    # List always starts with 0, so +1 needed
    for area_i in range(1,areaNo+1):
        area_arr_i = area_i-1 # To be used in lists
        areaData = lvlData[area_arr_i]
        print("len",len(areaData))
        areaRawSettings = []
        tileData = [[],[],[]]
        for zoneNo in range(0,len(areaData)):
            print("[D] outputting area",area_i,"zone",zoneNo)
            cur_zone = areaData[zoneNo]
            if areaRawSettings==[]: # Area First-timer, add configs
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
    # Create "course" folder
    u8_files_dir = u8_m.constructArchiveFile_m("course",b"",True,len(u8_files_list)+2) # +2 for itself + root folder
    # Create u8_m dict for repacking
    u8_dict = u8_m.constructFromScratch(no_of_areas,[u8_files_dir] + u8_files_list)
    #print(u8_dict)

    returnARC = u8_m.repackToBytes(u8_dict)
    with open("test_json.arc", 'wb') as f:
        f.write(returnARC)

def main():
    global inJson
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
    # copy dict template for addedZone
    addedZone = deepcopy(groupTilesetJson)
    while notFinished:
        area_zone = [[],[],[],[]]
        area_zone_size = [[],[],[],[]]
        area_tileset = ["","","",""]
        area_len = 1

        generated_zone, gen_zone_tileset, gen_zone_type = genZone(tilesetList,["full","entrance"])
        entrance_zone = deepcopy(generated_zone)
        ### OLD CODES \/\/
        
        area_zone[0].append(entrance_zone)
        zoneAddedNo += 1
        print("[D] Ent zone =",area_zone[0][-1]["zone"])
        # area_zone_size[0].append(area_zone[0][-1][4])

        if zone_ent_type=="entrance":
            print("Determine exit")
            # Need an exit zone, and a "main" zone
            exit_tileset = getRandomTileset(tilesetList)
            # Prevent area without exit
            while len(groupTilesetJson[exit_tileset]["exit"])==0 and len(groupTilesetJson[exit_tileset]["full"])==0 and len(groupTilesetJson[exit_tileset]["boss"])==0:
                exit_tileset = getRandomTileset(tilesetList)
            # Check for only 1 specific entrance zone type
            if len(groupTilesetJson[exit_tileset]["full"])==0:
                zone_ent_type = "exit"
            elif len(groupTilesetJson[exit_tileset]["exit"])==0:
                zone_ent_type = "full"
            else:
                zone_ent_type = "full" if randint(0,4)==0 else "exit" # Entrance only / Entranbce + exit

            ### DEBUGGING
            # zone_ent_type = "full"
            # exit_tileset = "Pa0_jyotyuPa2_sora"

            # Gets the random zone
            exit_zone = getRandomZone(exit_tileset,zone_ent_type)
            exit_zone["type"] = "exit"
            print("[D] Exit zone =",exit_zone["zone"])
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
            else:
                exit_zone = corrections.alignToPos(exit_zone,*tilePosToObjPos((32,32)))
                area_zone[1].append(exit_zone)
                area_tileset[1] = exit_tileset
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
                area_zone[0].append(main_zone)
            else: # Esort to Area 3 I guess
                main_zone = corrections.alignToPos(main_zone,*tilePosToObjPos((32,32)))
                main_zone = corrections.corrSprZone(main_zone)
                area_zone[2].append(main_zone)
                area_tileset[2] = main_tileset
                area_len+=1
                # All that is done, back out from the if statement.

            zoneAddedNo += 1
        else:
            main_zone = entrance_zone # Only for programmer's viewing sake

        # TODO Next step: link all zones tgt + gen deadends for extra exit / entrances
        # Get lists of enterable and non-enterable entrance
        area_ent = [] # Each area 1 new list
        # Structure: area_ent [Area No] [Exit=1 | Entrance=0] [Zone No] [0=AreaNo | 1=ZoneNo | 2=EntranceIDs]
        CONST_EXIT = 1; CONST_ENT = 0 # For viewing sake
        CONST_AREANO = 0; CONST_ZONENO = 1; CONST_ENTIDS = 2
        area_totExit = 0
        for i in range(0,len(area_zone)):
            area_zone_ent = []
            area_zone_onlyEnt = []
            # Get list of zones in area_zone
            for j in range(0,len(area_zone[i])):
                ent_exits, ent_onlyEnt = checks.findExitEnt(area_zone[i][j]) # get entrancess in zone
                if len(ent_exits)!=0: # Only add if list is not empty
                    area_totExit += len(ent_exits)
                    area_zone_ent.append((i,j,ent_exits)) # add to list
                if len(ent_onlyEnt)!=0: # Only add if list is not empty
                    area_zone_onlyEnt.append((i,j,ent_onlyEnt))
            # Shuffle list to achieve randomness since it will be processes as a queue below
            shuffle(area_zone_ent)
            shuffle(area_zone_onlyEnt)
            area_ent.append([area_zone_ent,area_zone_onlyEnt])
        # Randomise and pair entrances
        exit_idx = [0 for _ in range(0,len(area_zone))]
        # while not all enterables have a dest
        while area_totExit>0:
            # Get the entrance area
            cur_process_area = randint(0,len(area_ent)-1)
            init_val = cur_process_area
            while zoneAddedNo!=1 and (len(area_ent[cur_process_area][CONST_ENT])==0 or len(area_ent[cur_process_area][CONST_ENT][0][CONST_ENTIDS])==0):
                cur_process_area+=1 # Add if the chosen area does not have an enterable
                if cur_process_area>len(area_ent)-1: cur_process_area=0
            # Generate new room if only 1 zone
            if zoneAddedNo==1:
                # TODO Add zone
                print("New zone needed, please interrupt")
                exit()
                pass

            # Get the exit area
            cur_p_exit_area_no = randint(0,len(area_ent)-1)
            init_val = cur_p_exit_area_no
            while len(area_ent[cur_p_exit_area_no][CONST_EXIT])==0:
                print("exit",cur_p_exit_area_no,area_ent[cur_p_exit_area_no][CONST_EXIT])
                cur_p_exit_area_no+=1 # Add if the chosen area does not have an enterable
                if cur_p_exit_area_no>len(area_ent)-1: cur_p_exit_area_no=0
                if cur_p_exit_area_no==init_val:
                    # No exit?
                    pass
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
            
            print("2",area_ent[cur_p_exit_area_no][CONST_EXIT][cur_p_exit_zone_no][CONST_ENTIDS],cur_process_exit_ent)
            
            print("[D]", cur_process_area, exit_entData, "->", cur_p_exit_area_no,dest_entData)
            exit_entData[3] = cur_p_exit_area_no+1 # Set area
            exit_entData[4] = dest_entData[2] # Set ID
            area_zone[cur_process_area][cur_p_ent_area_zID]["entrance"][int(area_ent[cur_process_area][CONST_ENT][0][CONST_ENTIDS][0])] = exit_entData
            if not determinedExit: # Not an extra entrance
                del area_ent[cur_p_exit_area_no][CONST_EXIT][cur_p_exit_zone_no][CONST_ENTIDS][cur_process_exit_ent] # Remove from list
            del area_ent[cur_process_area][CONST_ENT][0][CONST_ENTIDS][0] # remove from list

            exit_idx[cur_process_area] += 1
            area_totExit-=1 # Countdown to 0
            

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