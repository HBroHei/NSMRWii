import json
from shutil import move

from dolphinAutoTransfer import dolphinAutoTransfer
import u8_m
import nsmbw
import globalVars
from Util import tilePosToObjPos, convertToDict, objPosToTilePos
from zone_random import checks,corrections, read_config

from random import randint, shuffle, choice, random
from copy import deepcopy
import traceback
from collections import defaultdict

inJson = {}

groupTilesetJson = {
    "normal" : defaultdict(list) , # No Entrance / Exit
    "entrance" : defaultdict(list), # Have  Level entrance only
    "full" : defaultdict(list), # Have both Level entrance and exit
    "exit" : defaultdict(list), # Have Level exit only
    "boss" : defaultdict(list), # Have Boss in zone
    "after_boss" : defaultdict(list), # Castle / Airship Boss cutscene
    "bonus" : defaultdict(list), # Only 1 entrance / same ent and exit
    "count" : 0
}
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

def check_conditions(main_zone):
    # if main_zone["orgLvl"]=="04-22.arc": input("1-1 found")
    # if "Pa0_jyotyuPa1_nohara" in area_tileset : input("Org tileset found")
    pass

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
    area_enterable_count[areaNo] += len(allEnt)
    area_nonenterable_count[areaNo] += len(allNonEnt)

def handle_zone_overlap(main_tileset, area_tileset, area_zone: list, main_zone: dict, zone_index: int):
    overlap_zone_no = checks.checkPosInZone(area_zone[zone_index], main_zone["zone"][0:2], *main_zone["zone"][2:4])

    check_conditions(main_zone)

    if overlap_zone_no != -1:
        print("Overlap with ZONE", overlap_zone_no, len(area_zone[zone_index]))
        overlap_zone = area_zone[zone_index][overlap_zone_no]["zone"]
        
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
    main_zone = corrections.corrDupID(zone_index, main_zone)
    main_zone = corrections.corrSprZone(main_zone)
    
    area_zone[zone_index].append(main_zone)
    # Add entrances in zone to list of entrances
    addEntranceData(zone_index, main_zone)
    
    return main_zone

# Adds a zone to the level
def addRandomZone(types: list):
    global zoneAddedNo, area_len, area_zone, area_tileset
    print("Determine extra")
    
    generated_zone, gen_zone_tileset, gen_zone_type = genZone(types)
    if generated_zone is None:
        print("Cannot find suitable zone")
        return None, None, None
    
    print("[D] Extra zone =", generated_zone["orgLvl"], generated_zone["zone"])
    D_count_levelzone(generated_zone["orgLvl"])
    generated_zone["sprites"], _dum, __dum = nsmbw.NSMBWsprite.processSprites(generated_zone["sprites"], [], "")
    
    for lay_i in range(3):
        if f"bgdatL{lay_i}" in generated_zone:
            generated_zone[f"bgdatL{lay_i}"] = nsmbw.NSMBWbgDat.processTiles(generated_zone[f"bgdatL{lay_i}"])
    
    generated_zone["zone"] = nsmbw.NSMBWZones.processZones(generated_zone["zone"])
    zoneAddedNo += 1
    gen_zone_prop = generated_zone["zone"]
    
    for idx in range(4):  # Loop through the areas (0 to 3)
        # If area tileset is subset or not assigned
        if area_tileset[idx] == "" or gen_zone_tileset in area_tileset[idx] or area_tileset[idx] in gen_zone_tileset:
            if area_tileset[idx] in gen_zone_tileset: area_tileset[idx] = gen_zone_tileset
            print("Tileset same?", gen_zone_tileset, area_tileset[idx])
            
            # Use handle_zone_overlap to manage overlap
            #print("MAIN",)
            try:
                generated_zone = handle_zone_overlap(area_tileset[idx], area_tileset, area_zone, generated_zone, idx)
            except IndexError: # New Area
                area_len += 1
            # Check for duplication and add zone
            # try:
            #     generated_zone = corrections.corrDupID(idx, generated_zone)
            #     generated_zone = corrections.corrSprZone(generated_zone)
            # except IndexError:
            #     area_len += 1
            
            area_zone[idx].append(generated_zone)
            area_tileset[idx] = gen_zone_tileset
            
            return idx, gen_zone_tileset, gen_zone_type
    
    return -1, "", None
    

# NOTE This will NOT remove the zone from the list
def getRandomZone(tilesetName:str, zone_type:str) -> dict:
    print("SELECT",tilesetName,zone_type)
    ret_zone = choice(groupTilesetJson[zone_type][tilesetName])
    return ret_zone

# Unbiased zone chooser
def genZone(types_list:list):
    all_zones = []
    # First, get all zones that are a type in types_list
    for cur_zone_type in types_list:
        for tileset_lst in groupTilesetJson[cur_zone_type].values():
            all_zones.extend(tileset_lst)
    #all_zones = [z for z in [tileset_lst for tileset_lst in [cur_type_zone_lst for cur_type_zone_lst in groupTilesetJson[types_list].values()]]]
    # Then choose a zone from it
    ret_zone = choice(all_zones)
    ret_tileset = "".join([ba.decode() for ba in ret_zone["tileset"]])
    return ret_zone, ret_tileset, ret_zone["type"]

def getRandomTileset(types_list:list):
    type_used = choice(types_list)
    return_tileset = []
    # print("USE",groupTilesetJson[type_used])
    while return_tileset==[]:
        return_tileset = choice(tuple(groupTilesetJson[type_used].keys()))
    print("Using",type_used,return_tileset)
    # Seperating return statement since I never know I would be seperating them in the future
    return return_tileset, type_used

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

# Generates a random zone from existing pool
# NOTE OLD / DEPRECATED
def genZone_O(types:list):
    # Get which types of zone to use
    type_used = ""
    cur_tileset = ""
    rep_counts = 0
    # Prevent:
    # - area without an entrance
    # - All area used, and generated tileset not in area tilesets
    # - no suitable place to place the zone
    while type_used == "" or (checkDictListEmpty(groupTilesetJson[type_used]) or\
        cur_tileset=="" or\
        (cur_tileset not in area_tileset and "" not in area_tileset)) and\
        rep_counts <= 100: # Failsafe, a hacky one

        cur_tileset, type_used = getRandomTileset(types)
        rep_counts+=1
    
    if rep_counts>100:
        return None,None,None
    
    zone_ent_type = type_used
    #zone_ent_type = "full" ### DEBUG

    assert type(cur_tileset)==str, "Type mismatch: " + type(cur_tileset) + " " + type(zone_ent_type)
    # Add the entrance zone
    ret_zone = deepcopy(getRandomZone(cur_tileset, zone_ent_type))
    assert ret_zone != None
    #area_zone[0].append(ret_zone)

    # Adjust coordinates relative to the new level
    ret_zone = corrections.alignToPos(ret_zone,*tilePosToObjPos((32,32)))
    assert ret_zone!=None
    ret_zone = corrections.corrSprZone(ret_zone)

    # Add info
    #ret_zone["tileset"] = cur_tileset
    ret_zone["type"] = zone_ent_type

    # Return: zone, tileset, type
    return ret_zone, cur_tileset, ret_zone["type"]

def writeToFile(lvlName:str, lvlData:list, areaNo = 1):
    no_of_areas = 0
    u8_files_list = []
    # List always starts with 0, so +1 needed
    for area_i in range(1,areaNo+1):
        area_arr_i = area_i-1 # To be used in lists
        areaData = lvlData[area_arr_i]
        print("len",len(areaData))
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
            if areaRawSettings==[]: # Area First-timer, add configs
                print("[D] Adding configs")
                
                pass
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
            for i in range(0,2): # Loop through each layer
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

    returnARC = u8_m.repackToBytes(u8_dict)
    from pathlib import Path
    Path("./Stage_output/").mkdir(exist_ok=True)
    with open("./Stage_output/" + lvlName, 'wb') as f:
        f.write(returnARC)
    print("============= Processed",lvlName,"=================")

# Code below are basically a copy of editArcFile()
def vanilla_processLvl(istr):
    newName = istr
    globalVars.tileData = [[],[],[]]

    #Read the U8 archive content
    u8list = u8_m.openFile("Stage_temp/"+newName)
    u8FileList = u8list["File Name List"]
    areaNo = u8list["Number of area"]
    areaNo %= 4
    if areaNo==0:
        areaNo = 4
    
    #Loop through every area
    for i in range(1,areaNo+1):
        u8list = readAndrandomise(i,istr,u8list)

    # "Encode" and Save the modified file
    u8n = u8_m.repackToBytes(u8list)
    from pathlib import Path
    Path("./Stage_output/").mkdir(exist_ok=True)
    with open("./Stage_output/" + istr, 'wb') as f:
        f.write(u8n)
            

def readAndrandomise(i,istr,_u8list):
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
        spriteData,sprLoadData,lvlSetting[7]["Size"] = nsmbw.NSMBWsprite.processSprites(spriteData,sprLoadData,istr)
    print("ZONES",zoneData)
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

def main():
    global inJson, zoneAddedNo, area_zone, area_tileset, entrance_list, area_enterable_count, area_nonenterable_count
    
    

    with open('out.json', 'r') as f:
        json_orginal = json.load(f)
    inJson = convertToDict(json_orginal)

    lst_tileset = set()
    # Group similar tilesets
    for key_lvl in inJson:
        for key_area in inJson[key_lvl]:
            for key_zone in inJson[key_lvl][key_area]:
                cur_zone = deepcopy(inJson[key_lvl][key_area][key_zone])
                cur_zone["orgLvl"] = key_lvl
                cur_tileset_str = "".join([ba.decode() for ba in cur_zone["tileset"]]) # All tilesets
                
                # Add key to dict if dict does not have the key
                # if cur_tileset_str not in groupTilesetJson.keys():
                #     lst_tileset.append(cur_tileset_str)
                #     groupTilesetJson[cur_tileset_str] = {
                #         "normal" : [] , # No Entrance / Exit
                #         "entrance" : [], # Have  Level entrance only
                #         "full" : [], # Have both Level entrance and exit
                #         "exit" : [], # Have Level exit only
                #         "boss" : [], # Have Boss in zone
                #         "after_boss" : [], # Castle / Airship Boss cutscene
                #         "bonus" : [], # Only 1 entrance / same ent and exit
                #         "count" : 0
                #     }
                # Calculate number of zones for each tilesets
                #groupTilesetJson[cur_tileset_str]["count"] += len(inJson[key_lvl][key_area].keys())
                lst_tileset.add(cur_tileset_str)
                cutscene_spr = checks.checkisCutsceneZone(cur_zone)
                if cutscene_spr!=-1:
                    if cutscene_spr[0]==408 or checks.checkBossSprite(cur_zone)[0]==-1:
                        cur_zone["type"] = "after_boss"
                        groupTilesetJson["after_boss"][cur_tileset_str].append(cur_zone) # Add to the cutscene list
                        continue # Skip the zone

                # Check zone has exit / entrances
                exit_flag,_dum = checks.checkExitSprite(cur_zone)
                ent_flag = checks.checkEntSpawn(cur_zone)
                boss_flag,_dum = checks.checkBossSprite(cur_zone)
                oneent_flag = checks.checkOnlyOneEnt(cur_zone)
                # Add the zone to its category
                if boss_flag==-1:
                    if exit_flag!=-1 and ent_flag!=-1:
                        cur_zone["type"] = "full"
                        groupTilesetJson["full"][cur_tileset_str].append(cur_zone)
                    elif exit_flag!=-1:
                        cur_zone["type"] = "exit"
                        groupTilesetJson["exit"][cur_tileset_str].append(cur_zone)
                    elif oneent_flag:
                        cur_zone["type"] = "bonus"
                        groupTilesetJson["bonus"][cur_tileset_str].append(cur_zone)
                    elif ent_flag!=-1:
                        cur_zone["type"] = "entrance"
                        groupTilesetJson["entrance"][cur_tileset_str].append(cur_zone)
                    else:
                        cur_zone["type"] = "normal"
                        groupTilesetJson["normal"][cur_tileset_str].append(cur_zone)
                else:
                    cur_zone["type"] = "exit"
                    groupTilesetJson["exit"][cur_tileset_str].append(cur_zone)

    ##### NOTE DEBUG #####
    ## RE-COMMENT WHEN NOT IN USED FOR PROGRAM TO FUNCTION ##
    # with open("./dist.json","w") as df:
    #     df.write(json.dumps(groupTilesetJson))
    # out_dejson = {}
    # with open("./testdejson.csv","w") as df:
    #     first_line = ""
    #     for t in lst_tileset:
    #         # df.write(t + ",")
    #         for k, v in groupTilesetJson.items():
    #             if k!="count":
    #                 # out_dejson[t][k] = len(v[t])
    #                 df.write(t + "," + k + "," + str(len(v[t])) + "\n")
    #     df.write(json.dumps(out_dejson, indent=4))
    # input("OUT END")
    

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
    normal_exit_area_id = -1
    secret_exit_area_id = -1
    stg_lst = read_config.listdir("./Stage_temp/")
    stg_i = 0
    while stg_i<len(stg_lst):
        stg_name = stg_lst[stg_i]
        print("============== Processing",stg_name,"=====================")
        if stg_name=="Texture" or stg_name in globalVars.skipLvl :
            #log += str("Processing [S]"+ "Stage_temp" + "/" + stg_name +"to" + "Stage_output/" + stg_name + "\n")
            move("Stage_temp" + "/" + stg_name,"Stage_output" + "/" + stg_name)
            stg_i += 1
            continue # Skip that folder
        elif stg_name in globalVars.skip_but_rando:
            # Randomise that level
            vanilla_processLvl(stg_name)
            stg_i += 1
            continue # Skip zone rando nonsense

        entrance_list = [[],[],[],[]] # entrance_list[area_no][zone_no]["enterable"|"nonenterable"], no need to complicated things
        area_enterable_count = [0,0,0,0]
        area_nonenterable_count = [0,0,0,0] 
        area_zone = [[],[],[],[]]
        area_zone_size = [[],[],[],[]]
        area_tileset = ["","","",""]
        area_len = 1
        only_main = False
        have_secret = stg_name in read_config.secret_exit

        # Generate the entrance zone
        generated_ent_zone, gen_ent_zone_tileset, gen_ent_zone_type = genZone(["full","entrance"])
        #genZone(tilesetList,["full","entrance"])
        if have_secret and gen_ent_zone_type=="full": # If have secret and type full, check whether spawn zone has 2 or more enterables
            while len(checks.findExitEnt(generated_ent_zone)[0])<1:
                generated_ent_zone, gen_ent_zone_tileset, gen_ent_zone_type = genZone(["full","entrance"])
        
        spawn_zone = deepcopy(generated_ent_zone)
        # Sprites randomisation
        spawn_zone["sprites"],_dum,__dum =\
            nsmbw.NSMBWsprite.processSprites(spawn_zone["sprites"],[],stg_name)
        for lay_i in range(0,3):
            if "bgdatL"+str(lay_i) in spawn_zone:
                spawn_zone["bgdatL"+str(lay_i)] = nsmbw.NSMBWbgDat.processTiles(spawn_zone["bgdatL"+str(lay_i)])
        spawn_zone["zone"] = nsmbw.NSMBWZones.processZones(spawn_zone["zone"])
        addEntranceData(0,spawn_zone)
        spawn_zone = corrections.alignToPos(spawn_zone,*tilePosToObjPos((32,32)))
        spawn_zone = corrections.corrDupID(0, spawn_zone)
        spawn_zone = corrections.corrSprZone(spawn_zone)
        area_zone[0].append(spawn_zone)
        area_tileset[0] = gen_ent_zone_tileset
        zoneAddedNo += 1 # Number of zones added
        print("[D] Ent zone from", area_zone[0][-1]["orgLvl"] ,"data =",area_zone[0][-1]["zone"])
        D_count_levelzone(area_zone[0][-1]["orgLvl"])

        check_conditions(spawn_zone)        

        if gen_ent_zone_type=="entrance":
            print("Determine exit")
            # Need an exit zone, and a "main" zone
            generated_exit_zone, gen_exit_zone_tileset, gen_exit_zone_type = genZone(["full","exit"])
        
            exit_zone = deepcopy(generated_exit_zone)
            print("[D] Exit zone from", exit_zone["orgLvl"] , "data =",exit_zone["zone"])
            D_count_levelzone(exit_zone["orgLvl"])
            # Change Flagpole type to normal
            exit_spr,exit_spr_pos = checks.checkExitSprite(exit_zone)
            if exit_spr[0]==113:
                exit_zone["sprites"][exit_spr_pos][3] = b"\x00\x00\x00\x00\x00\x00"
                print("Changed Flagpole")
            # Sprites randomisation
            exit_zone["sprites"],_dum,__dum =\
                nsmbw.NSMBWsprite.processSprites(exit_zone["sprites"],[],stg_name)
            for lay_i in range(0,3):
                if "bgdatL"+str(lay_i) in exit_zone:
                    exit_zone["bgdatL"+str(lay_i)] = nsmbw.NSMBWbgDat.processTiles(exit_zone["bgdatL"+str(lay_i)])
            exit_tileset = deepcopy(gen_exit_zone_tileset)
            exit_zone["zone"] = nsmbw.NSMBWZones.processZones(exit_zone["zone"])
            check_conditions(exit_zone)
            # Check for overlap with zones
            if area_tileset[0]=="" or exit_tileset in area_tileset[0] or area_tileset[0] in exit_tileset:
                # Check if area_tileset[0] is a subset of exit_tileset
                if area_tileset[0] in exit_tileset: area_tileset[0] = exit_tileset
                exit_zone = handle_zone_overlap(exit_tileset, area_tileset, area_zone, exit_zone, 0)
            else:
                exit_zone = corrections.alignToPos(exit_zone,*tilePosToObjPos((32,32)))
                exit_zone = corrections.corrSprZone(exit_zone)
                area_zone[1].append(exit_zone)
                area_tileset[1] = exit_tileset
                addEntranceData(1,exit_zone)
                normal_exit_zone_id = len(area_zone[1])-1
                normal_exit_area_id = 1
                area_len+=1
                added_zone_area_no = 1

            cutscene_zone_pos = (-1,-1)
            if exit_spr[0] in (406,407):
                # Gets the linked cutscene zone
                cutscene_zone = deepcopy(groupTilesetJson["after_boss"][gen_exit_zone_tileset][0])
                cutscene_zone["cutscene"] = ""
                #cutscene_zone_pos = (added_area_no,len(area_zone[added_zone_area_no]))
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
                # Check and correct duplicated zones
                # cutscene_zone = corrections.corrDupID(added_zone_area_no,cutscene_zone)
                # Surely this boss-dedicated scene would not have any other duplicates IDs
                cutscene_zone = corrections.corrSprZone(cutscene_zone)
                area_zone[added_zone_area_no].append(cutscene_zone)
                addEntranceData(added_zone_area_no,[])
                print("Added cutscene zone from",cutscene_zone["orgLvl"],cutscene_zone["zone"], "at", len(area_zone[added_zone_area_no])); # input()

            zoneAddedNo += 1

            # Generate the main area
            print("Determine main")
            # main_tileset = getRandomTileset(tilesetList)
            # # Prevent area without exit
            # while len(groupTilesetJson["normal"][main_tileset])==0:
            #     main_tileset = getRandomTileset(tilesetList)
            # ### DEBUGGING
            # # zone_ent_type = "full"
            # # exit_tileset = "Pa0_jyotyuPa2_sora"

            # # Gets the random zone
            # main_zone = deepcopy(getRandomZone(main_tileset,"normal"))
            generated_main_zone, gen_main_zone_tileset, gen_main_zone_type = genZone(["normal"])
        
            main_zone = deepcopy(generated_main_zone)
            main_tileset = gen_main_zone_tileset

            if have_secret:
                # If have secret, check whether main_zone has 2 or more enterables
                # Or have 1 enterable and 1 exit, that works too
                zone_type = ""
                while len(checks.findExitEnt(main_zone)[0])<2 or (len(checks.findExitEnt(main_zone)[0])<1 and zone_type=="exit"):
                    main_tileset, zone_type = getRandomTileset(["normal","exit"])
                    # Prevent area without exit
                    # while len(groupTilesetJson[main_tileset]["normal"])==0 and len(groupTilesetJson[main_tileset]["exit"])==0:
                    #     main_tileset = getRandomTileset(tilesetList)
                    #     # if "Pa0_jyotyuPa1_noharaPa2_doukutu" in main_tileset:
                    #     #     print(len(groupTilesetJson[main_tileset]["normal"]), len(groupTilesetJson[main_tileset]["exit"]))
                    #     #     input()
                    # if len(groupTilesetJson["normal"][main_tileset])!=0:
                    #     zone_type = "normal"
                    # else:
                    #     zone_type = "exit"
                    # if "Pa0_jyotyuPa1_noharaPa2_doukutu" in main_tileset: input(main_tileset, zone_type)
                    main_zone = deepcopy(getRandomZone(main_tileset,zone_type))
                    
                if "Pa0_jyotyuPa1_noharaPa2_doukutu" in main_tileset: input(main_tileset)
            # Sprites randomisation
            main_zone["sprites"],_dum,__dum =\
                nsmbw.NSMBWsprite.processSprites(main_zone["sprites"],[],stg_name)
            for lay_i in range(0,3):
                if "bgdatL"+str(lay_i) in main_zone:
                    main_zone["bgdatL"+str(lay_i)] = nsmbw.NSMBWbgDat.processTiles(main_zone["bgdatL"+str(lay_i)])
            print("[D] Main zone from", main_zone["orgLvl"] , "data =",main_zone["zone"])
            main_zone["zone"] = nsmbw.NSMBWZones.processZones(main_zone["zone"])
            check_conditions(main_zone)
            D_count_levelzone(main_zone["orgLvl"])
            # Check for overlap with zones
            if area_tileset[0]=="" or area_tileset[0] in main_tileset or main_tileset in area_tileset[0]:
                # check subset tileset
                if area_tileset[0] in main_tileset: area_tileset[0] = main_tileset
                main_zone = handle_zone_overlap(main_tileset, area_tileset, area_zone, main_zone, 0)
            elif area_tileset[1]=="" or area_tileset[1] in main_tileset or main_tileset in area_tileset[1]:
                if area_tileset[1] in main_tileset: area_tileset[1] = main_tileset
                main_zone = handle_zone_overlap(main_tileset, area_tileset, area_zone, main_zone, 1)
            else:  # Esort to Area 3 I guess
                main_zone = corrections.alignToPos(main_zone, *tilePosToObjPos((32, 32)))
                main_zone = corrections.corrSprZone(main_zone)
                area_zone[2].append(main_zone)
                area_tileset[2] = main_tileset
                # Add entrances in zone to list of entrances
                addEntranceData(2, main_zone)
                area_len += 1

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
        print("NONENT:",area_nonenterable_count)
        print("   ENT:",area_enterable_count)
        start_over = False
        secret_generated = not have_secret
        for area_no in range(0,4):
            # GEts a list of non-enterables excluding the current one
            lst_nonent_wo_myself = deepcopy(area_nonenterable_count)
            del lst_nonent_wo_myself[area_no]
            print(area_no,": Checking new zone:",lst_nonent_wo_myself,area_enterable_count[area_no])
            # if the sum of non-enterables < enterable, new zone needed
            if sum(lst_nonent_wo_myself)<area_enterable_count[area_no] or\
                not secret_generated: # Also: if secret exit needed
                print("NEW ZONE NEEDED, PLEASE ADD CODE HERE")
                print("Length of area_zone:",len(area_zone[0]),len(area_zone[1]),len(area_zone[2]),len(area_zone[3]))
                #input()
                # If there is an secret exit in this level, set type to "exit", and "full" otherwise
                added_area_no, added_tileset, added_type= addRandomZone(["exit"] if have_secret else ["normal","bonus"])
                if added_area_no==None:
                    # Lets start over
                    start_over = True
                    break
                if have_secret:
                    # Check if exit type is goal pole
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
                        # area_zone[added_area_no][-1]["sprites"][exit_spr_pos] = new_pole
                        area_zone[added_area_no][-1]["sprites"].append(new_pole)
                        # Set entrance type to normal
                        area_zone[added_area_no][-1]["entrance"][0][5] = 20
                        area_zone[added_area_no][-1]["entrance"][0][1] += 32 # Lower Y value
                        # prevent softlock in tiles
                        for til in area_zone[added_area_no][-1]["bgdatL1"]:
                            # if stg_name=="08-02.arc":
                            #     print("Area of pole",[zone_ent_x,zone_ent_y-160,96,160],"TILE:",til)
                            #     input()
                            if checks.checkPosInSpecificPos([zone_ent_x,zone_ent_y-160,96,160],tilePosToObjPos(til[1:3]),*tilePosToObjPos(til[3:])):
                                print("Removing tile")
                                area_zone[added_area_no][-1]["bgdatL1"].remove(til)

                        print("ADDED New Flagpole")
                    # Randomise sprite
                    area_zone[added_area_no][-1]["sprites"],_dum,__dum =\
                        nsmbw.NSMBWsprite.processSprites(area_zone[added_area_no][-1]["sprites"],[],stg_name)
                    area_zone[added_area_no][-1]["zone"] = nsmbw.NSMBWZones.processZones(area_zone[added_area_no][-1]["zone"])
                    for lay_i in range(0,3):
                        if "bgdatL"+str(lay_i) in area_zone[added_area_no][-1]:
                            area_zone[added_area_no][-1]["bgdatL"+str(lay_i)] = nsmbw.NSMBWbgDat.processTiles(area_zone[added_area_no][-1]["bgdatL"+str(lay_i)])
                print("Extra to Area:",added_area_no)
                print("Extra from", area_zone[added_area_no][-1]["orgLvl"] , "data =",area_zone[added_area_no][-1]["zone"])
                addEntranceData(added_area_no,area_zone[added_area_no][-1])
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

        print("Nonenterable list",area_nonenterable_count)
        print("   enterable list",area_enterable_count)
        #### CALCULATE THE NECESSARRY ENTRANCES / EXITS, AND ADDITIONAL ZONES ####
        # Well first, if there are no enterables, we can skip all "these codes"
        if sum(area_enterable_count)!=0:
            # First is Area 1 (0), which is always the spawn of the level
            cur_start_area = 0
            cur_start_zone = 0
            #cur_start_ent_pos = entrance_list[cur_start_area][cur_start_zone]["enterable"][-1]
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
            elif have_secret:
                rando_priority_lst = [2,1,secret_exit_area_id,1]
            else:
                rando_priority_lst = [2,1,1]

            # Add nonents to the nonent list
            nonent_list = [[],[],[],[]]
            for area_id in range(0,4):
                for zone_pos in range(0,len(area_zone[area_id])):
                    if "cutscene" in area_zone[area_id][zone_pos]: continue # Skip cutscene zones
                    print("Dest Area",area_id,"Len",len(area_zone[area_id]),"Zone pos =",zone_pos)
                    nonent_list[area_id] = [(zone_pos, exit_pos) for exit_pos in entrance_list[area_id][zone_pos]["nonenterable"]]
                    if len(nonent_list[area_id])==0: # FAilsafe to assign enterables for nonenterable in case there are no nonenterable
                        nonent_list[area_id] = [(zone_pos, exit_pos) for exit_pos in entrance_list[area_id][zone_pos]["enterable"]]

            # Assign entrances
            for area_id in (0,2,1,3):
                try:
                    # Set default level entrance
                    area_zone[area_id][0]["AreaSetting"][0][6] = area_zone[area_id][0]["entrance"][0][2]
                    # Set timer to a reasonable amount
                    area_zone[area_id][0]["AreaSetting"][0][3] = 500
                    # Set ambush flag off
                    area_zone[area_id][0]["AreaSetting"][0][7] = False
                except IndexError:
                    pass
                for zone_pos in range(0,len(area_zone[area_id])):
                    if "cutscene" in area_zone[area_id][zone_pos]: continue # Skip cutscene zones
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
                            area_lists_choice = (0,1,2,3)
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
                            for _area_id in range(0,4):
                                if len(nonent_list[_area_id])!=0:
                                    exit_key = choice(nonent_list[_area_id])
                                    print("3. Area ID", _area_id)
                                    print("3. ENT key",ent_key)
                                    print("3. EXIT key",exit_key)
                                    print("3. AREA LEN", len(area_zone[_area_id]))
                                    # Set value to exit_key
                                    area_zone[area_id][zone_pos]["entrance"][entrance_pos][3] = _area_id+1
                                    area_zone[area_id][zone_pos]["entrance"][entrance_pos][4] =\
                                        area_zone[_area_id][exit_key[0]]["entrance"][exit_key[1]][2]
                                    #             Area ID   Zone Pos                  Ent Pos
                                    
                                    nonent_list[_area_id].remove(exit_key)
                                    entrance_assign_list.append(ent_key)
                                    exit_found = True
                                    break

                            if not exit_found:
                                # Handle no exit found (e.g., add a new exit, adjust entrance, raise error)
                                print(f"No suitable exit found for entrance: {ent_key}")
                                # Esort to a random entrance at the exit area
                                # TODO I wish there is a better way to handle this situation
                                dest_area_id = 0
                                area_zone[area_id][zone_pos]["entrance"][entrance_pos][3] = dest_area_id+1
                                area_zone[area_id][zone_pos]["entrance"][entrance_pos][4] =\
                                    choice(area_zone[dest_area_id][0]["entrance"])[2]
            
        stg_i += 1
        # Why keeping track of area_len when I can just do this?
        area_len = len([area_add for area_add in area_zone if len(area_add)!=0])
        # Well, I wasted my time I guess
        print("Area len",area_len)
        writeToFile(stg_name,area_zone,area_len)
        print("=========",str(stg_i) + "/" + str(len(stg_lst)),"processed. =========")
        corrections.used_ids = [{},{},{},{}] # Reset duplicate ID list
        globalVars.cp1 = True
        if stg_name=="01-05.arc":input("PRESS ENTER TO CONTINUE...")
        #exit() ######## TEMP ########

    
    print(json.dumps(dict(sorted(count_distri.items(), key=lambda item: item[1]))))
    #print("*****All levels have been generated. Please move the stages into the respective folder*****")
    dolphinAutoTransfer.readAutoCopyConfig()

    # Starting Transfer to dolphin
    if dolphinAutoTransfer.verify_autotransfer_status(): 
        print("Auto Copying : Beginning transfer setting verification")
        if dolphinAutoTransfer.verify_transfer_settings():
            print("Auto Copying : Transfer settings are valid, beginning transfer...")
            if dolphinAutoTransfer.start_transfer("./Stage_output"):
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