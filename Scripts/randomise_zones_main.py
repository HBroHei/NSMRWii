import json
from shutil import move, copyfile, copytree, rmtree

from dolphinAutoTransfer import dolphinAutoTransfer
import u8_m
import nsmbw
import globalVars
from Util import tilePosToObjPos, convertToDict, objPosToTilePos, decodeTileset
from zone_random import checks,corrections, read_config

from random import randint, shuffle, choice, random
from copy import deepcopy
from collections import defaultdict
from pathlib import Path
from os import listdir, getcwd

inJson = {}

all_stage_zones = []
addedZone = {}

levelToImport = "01-01.arc"

zoneAddedNo = 0

entrance_list = [[],[],[],[]] # entrance_list[area_no][zone_no]["enterable"|"nonenterable"], no need to complicated things
area_enterable_count = [0,0,0,0]
area_nonenterable_count = [0,0,0,0]
area_zone = [[],[],[],[]]
area_zone_size = [[],[],[],[]]
area_tileset = [set(),set(),set(),set()]
area_len = 1

rando_priority_lst = []

tileData = [[],[],[]]
u8_files_list = []

STAGE_OUT_DIR = "./Stage_output/" if "Stage" in listdir(getcwd()) else "./Scripts/Stage_output/"
STAGE_DIR = "./Stage/" if "Stage" in listdir(getcwd()) else "./Scripts/Stage/"
OUTJSON_PATH = "./out.json" if "out.json" in listdir(getcwd()) else "./Scripts/out.json"
XML_PATH = "nsmb_randomizer.xml" if "nsmb_randomizer.xml" in listdir(getcwd()) else "./Scripts/nsmb_randomizer.xml"

#STAGE_DIR = "./Stage/" if "Stage" in listdir(getcwd()) else "./Scripts/Stage/"
CONFIG_PATH = "./config.json" if "config.json" in listdir(getcwd()) else "./Scripts/config.json"

isDebug = False

def D_check_conditions(main_zone):
    # if main_zone["orgLvl"]=="04-22.arc": input("1-1 found")
    # if "Pa0_jyotyuPa1_nohara" in area_tileset : input("Org tileset found")
    pass

class NoSuitableZoneError(Exception):
    def __init__(self, query):
        super().__init__(f"Cannot find a suitable zone with requirment {query}")

# Add data to the list of enterables / nonenterables
def addEntranceData(areaNo : int, zoneToFind:list):
    assert type(zoneToFind)==list or type(zoneToFind)==dict
    # Special zones that needs to be skipped:
    if zoneToFind==[]:
        allEnt = []
        allNonEnt = []
    else:
        allEnt, allNonEnt = checks.findExitEnt(zoneToFind)
    entrance_list[areaNo].append({
        "enterable" : allEnt,
        "nonenterable" : allNonEnt
    })
    print(f'ENTRANCE DATAS {areaNo}: {allEnt} {allNonEnt}')
    area_enterable_count[areaNo] += len(allEnt)
    area_nonenterable_count[areaNo] += len(allNonEnt)

def handle_zone_overlap(do_replace_tileset:bool, cur_area_tileset:set, area_zone: list, main_zone: dict, area_id: int):
    overlap_zone_no = checks.checkPosInZone(area_zone[area_id], main_zone["zone"][0:2], *main_zone["zone"][2:4])

    D_check_conditions(main_zone)

    if overlap_zone_no != -1:
        # print("Overlap with ZONE", overlap_zone_no, len(area_zone[area_id]))
        overlap_zone = area_zone[area_id][overlap_zone_no]["zone"]
        
        new_x = 512
        new_y = 512
        y_tot = overlap_zone[1] + overlap_zone[3] + 64 + main_zone["zone"][3]
        x_tot = overlap_zone[0] + overlap_zone[2] + 64 + main_zone["zone"][2]
        
        if x_tot > y_tot:  # Horizontal zone
            new_y = overlap_zone[1] + overlap_zone[3] + 480
        elif x_tot < y_tot:  # Vertical zone
            new_x = overlap_zone[0] + overlap_zone[2] + 480
        
        #print("Is X , Y", x_tot, y_tot)
        main_zone = corrections.alignToPos(main_zone, new_x, new_y, False)
        
    # Check and correct duplicated zones
    main_zone = corrections.corrDupID(area_id, main_zone)
    main_zone = corrections.corrSprEntZone(main_zone)
    #print("MAIN TILESET",main_tileset,type(main_tileset))
    # Check if more tilesets needed to be loaded
    cur_zone_tileset = set(ba.decode() for ba in main_zone["tileset"][1:])
    # Check if tileset name needs to be replaced
    if do_replace_tileset and len(area_zone[area_id])>0:#(cur_zone_tileset!=cur_area_tileset[area_id] and len(area_zone[area_id])!=0):
        cur_area_tileset[area_id] = cur_zone_tileset
        area_zone[area_id][0]["tileset"] = deepcopy(main_zone["tileset"])
    area_zone[area_id].append(main_zone)
    # Add entrances in zone to list of entrances
    addEntranceData(area_id, main_zone)
    print(f"Zone added to {area_id}")
    rando_priority_lst.insert(-1,area_id)

    return main_zone

# Adds a zone to the level
def addRandomZone(types: list):
    global zoneAddedNo, area_len, area_zone, area_tileset
    print("Determine extra")
    # Check if all area has been assigned
    a_tile_list = [("TILE", a_tile) for a_tile in area_tileset if a_tile]
    if len(a_tile_list)<4:
        query_param = types
    else:
        # All zones FULL! Please plop the zone into an existing tileset
        query_param = ["AND", ["OR"] + a_tile_list, types]
    generated_zone, gen_zone_tileset, gen_zone_type = genZone(query_param)


    if generated_zone is None:
        print("Cannot find suitable zone")
        return None, False
    
    print("[D] Extra zone =", generated_zone["orgLvl"], generated_zone["zone"])
    D_count_levelzone(generated_zone["orgLvl"])
    generated_zone["sprites"], _dum, __dum = nsmbw.NSMBWsprite.processSprites(generated_zone["sprites"], [])
    
    for lay_i in range(3):
        if f"bgdatL{lay_i}" in generated_zone:
            generated_zone[f"bgdatL{lay_i}"] = nsmbw.NSMBWbgDat.processTiles(generated_zone[f"bgdatL{lay_i}"])
    
    generated_zone["zone"] = nsmbw.NSMBWZones.processZones(generated_zone["zone"])
    generated_zone["tileset"] = nsmbw.NSMBWtileset.processTileset(generated_zone["tileset"])
    zoneAddedNo += 1

    
    for idx in range(4):  # Loop through the areas (0 to 3)
        # If area tileset is subset or not assigned
        if (not area_tileset[idx]) or (gen_zone_tileset.issubset(area_tileset[idx])) or (area_tileset[idx].issubset(gen_zone_tileset)):
            # Check if overrride needed
            # TODO This is already being done in handle_zone_overlap so ???
            if area_tileset[idx].issubset(gen_zone_tileset): area_tileset[idx] = gen_zone_tileset
            # Use handle_zone_overlap to manage overlap
            generated_zone = handle_zone_overlap(area_tileset[idx].issubset(gen_zone_tileset), area_tileset, area_zone, generated_zone, idx)
            
            return idx, area_tileset[idx] in gen_zone_tileset
    
    # Failsafe?
    return -1, False
    
# Unbiased zone chooser
def genZone(query:list):
    all_chosen_zones =  checks.filter_zone(all_stage_zones, query) # List of all suitable types
    if all_chosen_zones:
        chosen_zone = choice(all_chosen_zones)
        return chosen_zone, set(ba.decode() for ba in chosen_zone["tileset"][1:]), chosen_zone["type"]
    raise NoSuitableZoneError(query)

def getRandomEntrance(area_zone:list):
    area = choice(area_zone)
    while len(area)==0:
        area = choice(area_zone)
    zone = choice(area)
    while len(zone["entrance"])==0:
        zone = choice(area)
    return choice(zone["entrance"])

def checkDictListEmpty(d:dict):
    for i_lst in d.values():
        if len(i_lst)!=0: return False
    return True

def writeToFile(lvlName:str, lvlData:list, areaNo = 1):
    no_of_areas = 0
    u8_files_list = []
    # List always starts with 0, so +1 needed
    for area_i in range(1,areaNo+1):
        area_arr_i = area_i-1 # To be used in lists
        areaData = lvlData[area_arr_i]
        # If list len==0, skip
        if len(areaData)==0: continue

        areaRawSettings = []
        tileData = [[],[],[]]
        loadSprList = []

        # A bunch of config
        zone_bound = b""
        top_bg = []
        bot_bg = []
        ent_lst = []
        spr_lst = []
        zone_lst = []
        loc_lst = []
        cam_lst = []
        path_node_lst = []
        path_lst = []

        for zoneNo in range(0,len(areaData)):
            print("[D] outputting area",area_i,"zone",zoneNo)
            cur_zone = areaData[zoneNo]
            loadSprList += nsmbw.NSMBWLoadSprite.addLoadSprites(cur_zone["sprites"])
            ## finished adding config
            # Add properties
            zone_bound += cur_zone["ZoneBound"]
            top_bg += cur_zone["topBackground"]
            bot_bg += cur_zone["bottomBackground"]
            ent_lst += cur_zone["entrance"]
            spr_lst += cur_zone["sprites"]
            zone_lst.append(cur_zone["zone"])
            loc_lst += cur_zone["location"]
            if cur_zone["cameraProfile"]!=[]:
                cam_lst.append(cur_zone["cameraProfile"])
            # path_node_lst += cur_zone["pathNode"]
            # path_lst += cur_zone["path"]
            # TODO Add them to file
            
            # Add tiles data
            for i in range(0,3): # Loop through each layer
                if "bgdatL"+str(i) in cur_zone.keys():
                    for tiles in cur_zone["bgdatL" + str(i)]:
                        tileData[i].append(tiles)
                    # Convert to byte data
                    u8_files_list.append(u8_m.constructArchiveFile_m("course" + str(area_i) + "_bgdatL" + str(i) + ".bin",nsmbw.NSMBWbgDat.toByteData(tileData[i])))
                    # with open("course" + str(area_i) + "_bgdatL" + str(i) + ".bin", 'wb') as f:
                    #     f.write(nsmbw.NSMBWbgDat.toByteData(tileData[i]))
        # Add config
        # Prepare for Sprite loading list
        # TODO do this for all zones
        loadSprList = tuple(set(loadSprList))
        # Import settings one-by-one, in order from Section 0
        #print(f"AREA TILESET DEBUG @ {area_i}: {area_tileset}")
        areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWtileset.toByteData(areaData[0]["tileset"])))
        areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWAreaProp.toByteData(areaData[0]["AreaSetting"])))
        areaRawSettings.append(nsmbw.generateSectionDef(zone_bound)) # TODO Convert this to list if needed
        areaRawSettings.append(nsmbw.generateSectionDef(areaData[0]["AreaSetting2"]))
        areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWZoneBG.toByteData(top_bg)))
        areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWZoneBG.toByteData(bot_bg)))
        areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWEntrances.toByteData(ent_lst)))
        areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWsprite.toByteData(spr_lst)))
        areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWLoadSprite.toByteData(loadSprList)))
        areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWZones.toByteData(zone_lst)))
        areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWLocations.toByteData(loc_lst)))
        areaRawSettings.append(nsmbw.generateSectionDef(nsmbw.NSMBWCamProfile.toByteData(cam_lst)))
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

    returnARC = u8_m.repackToBytes(u8_dict)
    Path(STAGE_OUT_DIR).mkdir(exist_ok=True)
    with open(STAGE_OUT_DIR + lvlName, 'wb') as f:
        f.write(returnARC)
    print("============= Processed",lvlName,"=================")

# Code below are basically a copy of editArcFile()
def vanilla_processLvl(istr, old_stg_path):
    newName = istr
    globalVars.tileData = [[],[],[]]

    #Read the U8 archive content
    u8list = u8_m.openFile(old_stg_path + newName)
    u8FileList = u8list["File Name List"]
    areaNo = u8list["Number of area"]
    areaNo %= 4
    if areaNo==0:
        areaNo = 4
    
    #Loop through every area
    for i in range(1,areaNo+1):
        u8list = readAndRandomise(i,u8list)

    # "Encode" and Save the modified file
    u8n = u8_m.repackToBytes(u8list)
    Path(STAGE_OUT_DIR).mkdir(exist_ok=True)
    with open(STAGE_OUT_DIR + istr, 'wb') as f:
        f.write(u8n)
            

def readAndRandomise(i,_u8list):
    u8list = _u8list
    # Main area settings file
    lvlSetting = nsmbw.readDef(u8list["course"+ str(i) +".bin"]["Data"])

    # Read tiles
    for j in range(0,2): #Loop through every layers
        if ("course"+ str(i) +"_bgdatL" + str(j) + ".bin") in u8list: # if layer (j) exist
            #Get tiles info
            globalVars.tilesData[j] = nsmbw.NSMBWbgDat.phraseByteData(u8list["course"+ str(i) +"_bgdatL" + str(j) + ".bin"]["Data"])
            globalVars.tilesData[j] = nsmbw.NSMBWbgDat.processTiles(globalVars.tilesData[j])
            de_t = globalVars.tilesData[:] ## DEBUG VARIABLE TO STORE TILESDATA
            # "Encode" and Save the layer tile data
            u8list["course"+ str(i) +"_bgdatL" + str(j) + ".bin"]["Data"] = nsmbw.NSMBWbgDat.toByteData(globalVars.tilesData[j])
    
    # Sprite Handling (Section 7,8)
    # "Decode" to Python array
    spriteData = nsmbw.NSMBWsprite.phraseByteData(lvlSetting[7]["Data"])
    sprLoadData = nsmbw.NSMBWLoadSprite.phraseByteData(lvlSetting[8]["Data"])
    zoneData = nsmbw.NSMBWZones.phraseByteData(lvlSetting[9]["Data"])
    # Process the sprites, i.e. randomize it
    if len(spriteData)>0:
        spriteData,sprLoadData,lvlSetting[7]["Size"] = nsmbw.NSMBWsprite.processSprites(spriteData,sprLoadData)
    #print("ZONES",zoneData)
    zoneData = [nsmbw.NSMBWZones.processZones(z) for z in zoneData]
    lvlSetting[7]["Data"] = nsmbw.NSMBWsprite.toByteData(spriteData)
    lvlSetting[8]["Data"] = nsmbw.NSMBWLoadSprite.toByteData(sprLoadData)
    lvlSetting[9]["Data"] = nsmbw.NSMBWZones.toByteData(zoneData)
    u8list["course"+ str(i) +".bin"]["Data"] = nsmbw.writeDef(lvlSetting)

    return u8list

count_distri = {}
def D_count_levelzone(org_lvl):
    try:
        count_distri[org_lvl] += 1
    except KeyError:
        count_distri[org_lvl] = 1

def main(out_json_path = OUTJSON_PATH, config_f = CONFIG_PATH, stage_f = STAGE_DIR, autocopy_config = {}):
    global inJson, zoneAddedNo, area_zone, area_tileset, entrance_list, area_enterable_count, area_nonenterable_count, rando_priority_lst

    read_config.read(config_f=config_f, stage_f=stage_f)

    # Delete previous run
    try:
        rmtree(STAGE_OUT_DIR)
    except FileNotFoundError:
        pass

    if isinstance(out_json_path, str):
        with open(out_json_path, 'r') as f:
            json_orginal = json.load(f)
    else:
        json_orginal = out_json_path
    inJson = convertToDict(json_orginal)

    lst_tileset = set()
    
    ####   ZONES GROUPING   ####

    for key_lvl in inJson:
        for key_area in inJson[key_lvl]:
            for key_zone in inJson[key_lvl][key_area]:
                cur_zone = (inJson[key_lvl][key_area][key_zone])
                cur_zone["orgLvl"] = key_lvl
                cur_tileset_str = ",".join([ba.decode() for ba in cur_zone["tileset"][1:]]) # All tilesets exclude 1st one, added "," to identify unique tileset name
                cur_zone["type"] = [set(ba.decode() for ba in cur_zone["tileset"][1:])]

                # Calculate number of zones for each tilesets
                lst_tileset.add(cur_tileset_str)
                cutscene_spr = checks.checkisCutsceneZone(cur_zone)
                # Check if zone is a cutscene zone
                if cutscene_spr!=-1:
                    if cutscene_spr[0]==408 or checks.checkBossSprite(cur_zone)[0]==-1:
                        cur_zone["type"].append("after_boss")
                        all_stage_zones.append(cur_zone)
                        continue # Skip the zone

                # Check zone has exit / entrances
                ambush_flag, _dum = checks.checkAmbushSprite(cur_zone)
                cannon_flag = checks.checkCannonSprite(cur_zone)
                exit_flag,_dum = checks.checkExitSprite(cur_zone)
                ent_flag = checks.checkEntSpawn(cur_zone) # Check if entrance is the area entrance
                boss_flag,_dum = checks.checkBossSprite(cur_zone)
                oneent_flag = checks.checkOnlyOneEnt(cur_zone)
                zone_len_x = cur_zone["zone"][2]
                zone_len_y = cur_zone["zone"][3]
                # Add the zone to its category
                lvl_type = ""
                if boss_flag!=-1:
                    lvl_type = "exit"
                elif ambush_flag!=-1:
                    lvl_type = "ambush"
                elif exit_flag!=-1 and zone_len_x<=2000 and zone_len_y<=1000:
                    lvl_type = "exit"
                elif exit_flag!=-1 and ent_flag!=-1:
                    lvl_type = "full"
                elif oneent_flag:
                    lvl_type = "bonus"
                elif zone_len_x>2000 or zone_len_y>1000:
                    lvl_type = "normal"
                elif cannon_flag:
                    lvl_type = "cannon"
                else:
                    lvl_type = "entrance"
                cur_zone["type"].append(lvl_type)

                # NOTE Add other types here
                # Add group tags
                cur_zone["type"] += globalVars.groupTag["Full"].get(key_lvl, [])
                cur_zone["type"] += globalVars.groupTag["World"].get(key_lvl[0:2], [])
                cur_zone["type"] += globalVars.groupTag["Stage"].get(key_lvl[3:5], [])

                # Add to the list of all zones
                all_stage_zones.append(cur_zone)

    # These will always be area 1, with exit zone as zone 0 in the level
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
    # tilesetList = list(groupTilesetJson.keys())
    zoneAddedNo = 0
    stg_lst = read_config.listdir(stage_f)
    stg_i = 0
    while stg_i<len(stg_lst):
        stg_name = stg_lst[stg_i]
        rando_priority_lst = []
        print("============== Processing",stg_name,"=====================")
        if stg_name=="Texture" or stg_name in globalVars.skipLvl :
            #log += str("Processing [S]"+ "Stage_temp" + "/" + stg_name +"to" + "Stage_output/" + stg_name + "\n")
            copyfile(stage_f + stg_name,STAGE_OUT_DIR + stg_name) if stg_name!="Texture" else copytree(stage_f + stg_name,STAGE_OUT_DIR + stg_name)
            stg_i += 1
            continue # Skip that folder
        elif stg_name in globalVars.skip_but_rando:
            # Randomise that level
            vanilla_processLvl(stg_name, stage_f)
            stg_i += 1
            continue # Skip zone rando nonsense

        entrance_list = [[],[],[],[]] # entrance_list[area_no][zone_no]["enterable"|"nonenterable"], no need to complicated things
        area_enterable_count = [0,0,0,0]
        area_nonenterable_count = [0,0,0,0] 
        area_zone = [[],[],[],[]]
        area_zone_size = [[],[],[],[]]
        area_tileset = [set(),set(),set(),set()]

        area_len = 1
        only_main = False
        have_secret = stg_name in read_config.secret_exit

        # Get the type the stage should be (Generate the query)
        stage_query = []
        zone_limit = 10 # Temp number
        if globalVars.groupTag["Full"].get(stg_name, []):
            stage_query.append(["OR"] + globalVars.groupTag["Full"][stg_name])
        if globalVars.groupTag["World"].get(stg_name, []):
            stage_query.append(["OR"] + globalVars.groupTag["World"][stg_name])
        if globalVars.groupTag["Stage"].get(stg_name, []):
            stage_query.append(["OR"] + globalVars.groupTag["Stage"][stg_name])
        if stage_query:
            # Check zone limit
            for t in [t2 for tl in stage_query for t2 in tl]:
                if t in globalVars.groupTag["Zone Number Limit"]:
                    zone_limit = globalVars.groupTag["Zone Number Limit"][t]
                    stage_query = t
                    break
            else:
                stage_query.insert(0, "OR")

        # Generate the entrance zone
        generated_ent_zone, gen_ent_zone_tileset, gen_ent_zone_type = genZone(checks.simplify_query(("OR", "full", "entrance", "ambush"), stage_query, zone_limit==1))
        if have_secret and "full" in gen_ent_zone_type: # If have secret and type full, check whether spawn zone has 2 or more enterables
            while len(checks.findExitEnt(generated_ent_zone)[0])<1:
                generated_ent_zone, gen_ent_zone_tileset, gen_ent_zone_type = genZone(checks.simplify_query(("OR", "full", "entrance", "ambush"), stage_query, zone_limit==1))

        spawn_zone = deepcopy(generated_ent_zone)
        # Sprites randomisation
        spawn_zone["sprites"],_dum,__dum = nsmbw.NSMBWsprite.processSprites(spawn_zone["sprites"],[])
        for lay_i in range(0,3):
            if "bgdatL"+str(lay_i) in spawn_zone:
                spawn_zone["bgdatL"+str(lay_i)] = nsmbw.NSMBWbgDat.processTiles(spawn_zone["bgdatL"+str(lay_i)])
        
        # Zone-related randomisaton (Music, dark)
        spawn_zone["zone"] = nsmbw.NSMBWZones.processZones(spawn_zone["zone"])

        # Tileset 0 rando
        spawn_zone["tileset"] = nsmbw.NSMBWtileset.processTileset(spawn_zone["tileset"])
        
        # Record entrances data
        addEntranceData(0,spawn_zone)

        # Correcting incorrect positions and IDs
        spawn_zone = corrections.alignToPos(spawn_zone,*tilePosToObjPos((32,32)))
        spawn_zone = corrections.corrDupID(0, spawn_zone)
        spawn_zone = corrections.corrSprEntZone(spawn_zone)

        # Add to list
        area_zone[0].append(spawn_zone)
        area_tileset[0] = gen_ent_zone_tileset
        zoneAddedNo += 1 # Number of zones added
        print("[D] Ent zone from", area_zone[0][-1]["orgLvl"] ,"data =",area_zone[0][-1]["zone"], decodeTileset(spawn_zone))
        D_count_levelzone(area_zone[0][-1]["orgLvl"])

        D_check_conditions(spawn_zone)

        if "entrance" in gen_ent_zone_type:
            # TODO LARGELY duplicated from above (TWICE!). Clean up pls
            # Also please make use of addRandomZone, it is capable of this stuff
            print("Determine exit")
            # Need an exit zone, and a "main" zone
            generated_exit_zone, gen_exit_zone_tileset, gen_exit_zone_type = genZone(checks.simplify_query(("OR","full","exit","ambush","cannon"), stage_query))
        
            exit_zone = deepcopy(generated_exit_zone)
            print("[D] Exit zone from", exit_zone["orgLvl"] , "data =",exit_zone["zone"], gen_exit_zone_tileset)
            D_count_levelzone(exit_zone["orgLvl"])
            # Change Flagpole type to normal
            exit_spr,exit_spr_pos = checks.checkAllExitSprite(exit_zone)
            if exit_spr[0]==113:
                exit_zone["sprites"][exit_spr_pos][3] = b"\x00\x00\x00\x00\x00\x00"
                print("Changed Flagpole")
            # Sprites randomisation
            exit_zone["sprites"],_dum,__dum =\
                nsmbw.NSMBWsprite.processSprites(exit_zone["sprites"],[])
            for lay_i in range(0,3):
                if "bgdatL"+str(lay_i) in exit_zone:
                    exit_zone["bgdatL"+str(lay_i)] = nsmbw.NSMBWbgDat.processTiles(exit_zone["bgdatL"+str(lay_i)])
            exit_tileset = deepcopy(gen_exit_zone_tileset)
            exit_zone["zone"] = nsmbw.NSMBWZones.processZones(exit_zone["zone"])
            exit_zone["tileset"] = nsmbw.NSMBWtileset.processTileset(exit_zone["tileset"])
            D_check_conditions(exit_zone)
            # Check for overlap with zones
            if (not area_tileset[0]) or exit_tileset.issubset(area_tileset[0]) or area_tileset[0].issubset(exit_tileset):
                # Check if area_tileset[0] is a subset of exit_tileset
                # TODO again, this is already being done in the following function so even more ?????
                if area_tileset[0].issubset(exit_tileset): area_tileset[0] = exit_tileset
                exit_zone = handle_zone_overlap(area_tileset[0].issubset(exit_tileset), area_tileset, area_zone, exit_zone, 0)
                added_zone_area_no = 0
            else:
                exit_zone = corrections.alignToPos(exit_zone,*tilePosToObjPos((32,32)))
                exit_zone = corrections.corrDupID(1, exit_zone) # Still needed to add IDs in this zone
                exit_zone = corrections.corrSprEntZone(exit_zone)
                area_zone[1].append(exit_zone)
                area_tileset[1] = exit_tileset
                addEntranceData(1,exit_zone)
                area_len+=1
                added_zone_area_no = 1
                rando_priority_lst.append(1)

            if exit_spr[0] in (406,407):
                # Gets the linked cutscene zone
                # cutscene_zone = deepcopy(groupTilesetJson["after_boss"][gen_exit_zone_tileset][0])
                print(f"After boss: {gen_exit_zone_tileset}")
                cutscene_zone, _dummy, __dummy = genZone(checks.simplify_query(["AND", "after_boss", ("TILE", gen_exit_zone_tileset)], stage_query))
                cutscene_zone["cutscene"] = ""
                overlap_zone_no = checks.checkPosInZone(area_zone[added_zone_area_no], cutscene_zone["zone"][1:3], *cutscene_zone["zone"][3:5])
                if overlap_zone_no!=-1:
                    overlap_zone = area_zone[added_zone_area_no][overlap_zone_no]["zone"]
                    new_x = 512
                    new_y = 512
                    y_tot = overlap_zone[1]+overlap_zone[3]+64+cutscene_zone["zone"][3]
                    x_tot = overlap_zone[0]+overlap_zone[2]+64+cutscene_zone["zone"][2]
                    if x_tot > y_tot: # Horizontal zone
                        new_y = overlap_zone[1]+overlap_zone[3]+480
                    if x_tot < y_tot: # Vertical zone
                        new_x = overlap_zone[0]+overlap_zone[2]+480
                    cutscene_zone = corrections.alignToPos(cutscene_zone,new_x,new_y,False)
                # Surely this boss-dedicated scene would not have any other duplicates IDs
                cutscene_zone = corrections.corrSprEntZone(cutscene_zone)
                area_zone[added_zone_area_no].append(cutscene_zone)
                addEntranceData(added_zone_area_no,[])
                print("Added cutscene zone from",cutscene_zone["orgLvl"],cutscene_zone["zone"], "at", len(area_zone[added_zone_area_no])); # input()

            zoneAddedNo += 1

            # Check if zone limit exceeded
            # TODO temp. code, will be removed with merging code with addRandomZone
            if zone_limit>2:
                # Generate the main area
                print("Determine main")

                # # Gets the random zone
                # main_zone = deepcopy(getRandomZone(main_tileset,"normal"))
                generated_main_zone, gen_main_zone_tileset, gen_main_zone_type = genZone(checks.simplify_query("normal", stage_query))
            
                main_zone = deepcopy(generated_main_zone)
                main_tileset = gen_main_zone_tileset

                if have_secret:
                    # If have secret, check whether main_zone has 2 or more enterables
                    # Or have 1 enterable and 1 exit, that works too
                    zone_type = ""
                    while len(checks.findExitEnt(main_zone)[0])<2 or (len(checks.findExitEnt(main_zone)[0])<1 and zone_type=="exit"):
                        main_zone, main_tileset, gen_main_zone_type = genZone(checks.simplify_query(("OR", "normal","exit","ambush","cannon"), stage_query))

                # Sprites randomisation
                main_zone["sprites"],_dum,__dum =\
                    nsmbw.NSMBWsprite.processSprites(main_zone["sprites"],[])
                for lay_i in range(0,3):
                    if "bgdatL"+str(lay_i) in main_zone:
                        main_zone["bgdatL"+str(lay_i)] = nsmbw.NSMBWbgDat.processTiles(main_zone["bgdatL"+str(lay_i)])
                print("[D] Main zone from", main_zone["orgLvl"] , "data =",main_zone["zone"], main_tileset)
                main_zone["zone"] = nsmbw.NSMBWZones.processZones(main_zone["zone"])
                main_zone["tileset"] = nsmbw.NSMBWtileset.processTileset(main_zone["tileset"])
                D_check_conditions(main_zone)
                D_count_levelzone(main_zone["orgLvl"])
                # Check for overlap with zones
                if (not area_tileset[0]) or area_tileset[0].issubset(main_tileset) or main_tileset.issubset(area_tileset[0]):
                    # check subset tileset
                    # TODO AGAIN????????????
                    if area_tileset[0].issubset(main_tileset): area_tileset[0] = main_tileset
                    main_zone = handle_zone_overlap(area_tileset[0].issubset(main_tileset), area_tileset, area_zone, main_zone, 0)
                elif (not area_tileset[1]) or area_tileset[1].issubset(main_tileset) or main_tileset.issubset(area_tileset[1]):
                    if area_tileset[1].issubset(main_tileset): area_tileset[1] = main_tileset # TODO yes, it is this again
                    main_zone = handle_zone_overlap(area_tileset[0].issubset(main_tileset), area_tileset, area_zone, main_zone, 1)
                else:  # Esort to Area 3 I guess
                    main_zone = corrections.alignToPos(main_zone, *tilePosToObjPos((32, 32)))
                    main_zone = corrections.corrDupID(2, main_zone)
                    main_zone = corrections.corrSprEntZone(main_zone)
                    area_zone[2].append(main_zone)
                    area_tileset[2] = main_tileset
                    # Add entrances in zone to list of entrances
                    addEntranceData(2, main_zone)
                    area_len += 1
                    rando_priority_lst.insert(-1,2)

            zoneAddedNo += 1
        else:
            main_zone = spawn_zone # Only for programmer's viewing sake, shouldn't do anything lol
            only_main = True # This, however, is to mark which entrance will be prioritised to be randomised

        #### END OF ADDING THE NECESSARY ZONES ####

        ### Check if new zones is needed to be added - for:
        # - Entrances > exit number
        # - have secret exit
        # I believe there is a better wauy to do this, but this will do for now
        secret_generated = False
        ent_pipes_cand = []
        # print("NONENT:",area_nonenterable_count)
        # print("   ENT:",area_enterable_count)
        start_over = False
        secret_generated = not have_secret
        for area_no in range(0,4):
            # GEts a list of non-enterables excluding the current one
            lst_nonent_wo_myself = deepcopy(area_nonenterable_count)
            del lst_nonent_wo_myself[area_no]
            # if the sum of non-enterables < enterable, new zone needed
            if sum(lst_nonent_wo_myself)<area_enterable_count[area_no] or\
                not secret_generated: # Also: if secret exit needed
                print("NEW ZONE NEEDED, PLEASE ADD CODE HERE")
                print("Length of area_zone:",len(area_zone[0]),len(area_zone[1]),len(area_zone[2]),len(area_zone[3]))
                # If there is an secret exit in this level, set type to "exit", and "full" otherwise
                (added_area_no, is_new_tileset) = addRandomZone(checks.simplify_query("exit" if have_secret else ["OR","entrance","bonus"], stage_query))
                if added_area_no==None:
                    # Lets start over
                    # TODO Is this necessary anymore?
                    start_over = True
                    break
                if have_secret:
                    # Check if exit type is goal pole]
                    #print(f"{added_area_no}  {area_zone[added_area_no]}")
                    exit_spr,exit_spr_pos = checks.checkExitSprite(area_zone[added_area_no][-1])
                    if exit_spr[0]==113:
                        area_zone[added_area_no][-1]["sprites"][exit_spr_pos][3] = b"\x00\x00\x10\x00\x00\x00"
                        print("Changed Flagpole")
                    else:
                        # Make a new flag pole
                        zone_ent_x,zone_ent_y = area_zone[added_area_no][-1]["entrance"][0][0:2]
                        new_pole = [
                            113,
                            zone_ent_x+40,
                            zone_ent_y,
                            b"\x00\x00\x10\x00\x00\x00",
                            exit_spr[4],
                            exit_spr[5]
                        ]
                        area_zone[added_area_no][-1]["sprites"].append(new_pole)
                        # Set entrance type to normal
                        area_zone[added_area_no][-1]["entrance"][0][5] = 20
                        area_zone[added_area_no][-1]["entrance"][0][1] += 32 # Lower Y value
                        # prevent softlock in tiles
                        for til in area_zone[added_area_no][-1]["bgdatL1"]:
                            if checks.checkPosInSpecificPos([zone_ent_x,zone_ent_y-160,96,160],tilePosToObjPos(til[1:3]),*tilePosToObjPos(til[3:])):
                                print("Removing tile")
                                area_zone[added_area_no][-1]["bgdatL1"].remove(til)
                        # Add tiles to prevent falling
                        area_zone[added_area_no][-1]["bgdatL1"].append([53, zone_ent_x, zone_ent_y+2, 25,1])

                        print("ADDED New Flagpole")
                    # Randomise sprite
                    area_zone[added_area_no][-1]["sprites"],_dum,__dum =\
                        nsmbw.NSMBWsprite.processSprites(area_zone[added_area_no][-1]["sprites"],[])
                    area_zone[added_area_no][-1]["zone"] = nsmbw.NSMBWZones.processZones(area_zone[added_area_no][-1]["zone"])
                    for lay_i in range(0,3):
                        if "bgdatL"+str(lay_i) in area_zone[added_area_no][-1]:
                            area_zone[added_area_no][-1]["bgdatL"+str(lay_i)] = nsmbw.NSMBWbgDat.processTiles(area_zone[added_area_no][-1]["bgdatL"+str(lay_i)])
                print("Extra to Area:",added_area_no)
                secret_exit_area_id = added_area_no
                secret_exit_zone_id = len(area_zone[added_area_no])
                print("NEW Length of area_zone:",len(area_zone[0]),len(area_zone[1]),len(area_zone[2]),len(area_zone[3]))
                # input() 

                secret_generated = True
        if start_over:
            print("Cannot find suitable area, starting over")
            start_over = False
            continue
        
        #############################################
        ### END OF GENERATING ZONE FOR THIS LEVEL ###
        #############################################

        #############################################
        ######## START RANDOMISING ENTRANCES ########
        #############################################
        print("*** START OF Entrance Randomisation ***")
        print("Nonenterable list",area_nonenterable_count)
        print("   enterable list",area_enterable_count)
        print(f"PRIORITY LIST: {rando_priority_lst}")
        #### CALCULATE THE NECESSARRY ENTRANCES / EXITS, AND ADDITIONAL ZONES ####
        # Well first, if there are no enterables, we can skip all "these codes"
        if sum(area_enterable_count)!=0:
            # First is Area 1 (0), which is always the spawn of the level
            processed_enterable_id = [
                [[] for _ in range(len(entrance_list[0]))],
                [[] for _ in range(len(entrance_list[1]))],
                [[] for _ in range(len(entrance_list[2]))],
                [[] for _ in range(len(entrance_list[3]))]
            ] # Storing randomised entrance ids

            entrance_assign_list = []

            # Add nonents to the nonent list
            nonent_list = [[],[],[],[]]
            for area_id in range(0,4):
                processing_area = area_zone[area_id]
                for zone_pos in range(0,len(processing_area)):
                    if "cutscene" in processing_area[zone_pos]: continue # Skip cutscene zones
                    zone_main_ent = tuple()
                    for exit_pos in entrance_list[area_id][zone_pos]["nonenterable"]:
                        # Check if nonent is the main entrance
                        if processing_area[zone_pos]["AreaSetting"][0][6]!=processing_area[zone_pos]["entrance"][exit_pos][2]:
                            print(f"Area Zone Main Entrance: {processing_area[zone_pos]["AreaSetting"][0][6]} {processing_area[zone_pos]["entrance"][exit_pos][2]}")
                            nonent_list[area_id].append((zone_pos, exit_pos))
                        else:
                            zone_main_ent = (zone_pos, exit_pos)
                    # Shuffle the nonent list
                    shuffle(nonent_list[area_id])
                    # Add zone main entrance to the top of the list
                    if zone_main_ent:
                        print("zone_main_ent", processing_area[zone_main_ent[0]]["entrance"][zone_main_ent[1]])
                        nonent_list[area_id].append(zone_main_ent)
                    
                if not nonent_list[area_id]: # Failsafe to assign enterables for nonenterable in case there are no nonenterable
                    for zone_pos in range(0,len(processing_area)):
                        nonent_list[area_id] += [(zone_pos, exit_pos) for exit_pos in entrance_list[area_id][zone_pos]["enterable"]]
            nonent_list_backup = deepcopy(nonent_list) # Backup list in case the list got emptied

            # Assign entrances
            for area_id in (0,2,1,3):
                for zone_pos in range(0,len(area_zone[area_id])):
                    if "cutscene" in area_zone[area_id][zone_pos]: continue # Skip cutscene zones
                    for entrance_pos in entrance_list[area_id][zone_pos]["enterable"]:
                        # Find suitable exit
                        exit_found = False
                        # Check assigned
                        ent_key = str(area_id) + "_" + str(zone_pos) + "_" + str(entrance_pos)
                        if ent_key in entrance_assign_list: continue

                        # Get the dest area id
                        # Check if there are priority
                        if len(rando_priority_lst)==0:
                            # No priority - choose randomly
                            area_lists_choice = (0,1,2,3)
                            dest_area_id = choice(area_lists_choice)
                            round_count = 0
                            while dest_area_id==area_id or len(nonent_list[dest_area_id])==0:
                                dest_area_id += 1
                                if dest_area_id>3: dest_area_id = 0
                                round_count+=1
                                if round_count == 4: break
                        else:
                            # Have priority
                            dest_area_id = rando_priority_lst.pop(0)
                            print("Priority: Area set to",dest_area_id)
                            print(f"Area has {nonent_list[dest_area_id]} entrances")
                        
                        # Check area have nonent
                        if len(nonent_list[dest_area_id])!=0:
                            # Exist - choose a nonent
                            exit_key = nonent_list[dest_area_id].pop()
                            exit_found = True

                        """# Check if it is priority. If true, choose ANY (enterable in this case) entrance in the area
                        elif len(rando_priority_lst)!=0:
                            exit_key=[]
                            available_zones = tuple(zpos for zpos in range(len(area_zone[dest_area_id])) if area_zone[dest_area_id][zpos]["entrance"])
                            for zpos in available_zones:
                                for epos in range(len(area_zone[dest_area_id][zpos]["entrance"])):
                                    exit_key.append((zpos, epos))
                            print("2. EXIT KEY",exit_key)
                            exit_found = True"""

                        # 3. Any Area (Last Resort)
                        if not exit_found:
                            available_choose_area = [a for a in range(0,4) if len(nonent_list[a])!=0]
                            dest_area_id = choice(available_choose_area if len(available_choose_area)!=0 else (0,))
                            print("RESORTING.", nonent_list[dest_area_id])
                            print("3. Area ID", dest_area_id)
                            exit_key = nonent_list[dest_area_id].pop()

                        # Set value to exit_key
                        area_zone[area_id][zone_pos]["entrance"][entrance_pos][3] = dest_area_id+1
                        area_zone[area_id][zone_pos]["entrance"][entrance_pos][4] =\
                            area_zone[dest_area_id][exit_key[0]]["entrance"][exit_key[1]][2]
                        #             Area ID   Zone Pos                  Ent Pos

                        # Check if it is set to Area entrance

                        # Remove available exit from list if there are still other exits available
                        # nonent_list[dest_area_id].remove(exit_key)
                        if len(nonent_list[dest_area_id])==0: nonent_list[dest_area_id] = deepcopy(nonent_list_backup[dest_area_id])
                        entrance_assign_list.append(ent_key)
                try:
                    # Set default level entrance
                    area_zone[area_id][0]["AreaSetting"][0][6] = area_zone[area_id][0]["entrance"][0][2]
                    # Set timer to a reasonable amount (700 for now)
                    area_zone[area_id][0]["AreaSetting"][0][3] = 500
                    # Set ambush flag off
                    area_zone[area_id][0]["AreaSetting"][0][7] = False
                except IndexError:
                    pass

        stg_i += 1
        # Why keeping track of area_len when I can just do this?
        area_len = len([area_add for area_add in area_zone if len(area_add)!=0])
        # Well, I wasted my time I guess
        print("Area len",area_len)
        writeToFile(stg_name,area_zone,area_len)
        # Reset correction variables
        corrections.reset_vars()
        print("=========",str(stg_i) + "/" + str(len(stg_lst)),"processed. =========")
        globalVars.cp1 = True
        if stg_name=="01-01.arc":input("PRESS ENTER TO CONTINUE...")
        #exit() ######## TEMP ########

    
    print(json.dumps(dict(sorted(count_distri.items(), key=lambda item: item[1]))))
    #print("*****All levels have been generated. Please move the stages into the respective folder*****")
    dolphinAutoTransfer.readAutoCopyConfig(autocopy_config)

    # Starting Transfer to dolphin
    if dolphinAutoTransfer.verify_autotransfer_status(): 
        print("Auto Copying : Beginning transfer setting verification")
        if dolphinAutoTransfer.verify_transfer_settings():
            print("Auto Copying : Transfer settings are valid, beginning transfer...")
            if dolphinAutoTransfer.start_transfer(STAGE_OUT_DIR, XML_PATH):
                print("Auto Copying : Randomized Files and related Riivolution XML has been correctly transfered to the riivolution folder")
            else:
                print("Auto Copying : An error occurred during files transfer")
        else:
            print("Auto Copying : Transfer settings are invalid, aborting transfer")
    else:
        print("Auto Copying : Auto Copying is disabled, don't forget to follow instructions for copy files from \"Stage_output\"")
    exit()

if __name__=="__main__":
    main()
