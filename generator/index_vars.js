const e_presets_desc = {
    "r_all" : "All the enemies, including non-movable obsticles, will be randomized.<br> MAY CAUSE LAG OR CRASHES!",
    "r_all_b" : "All the standalone enemies will be randomized.<br> MAY CAUSE LAG OR CRASHES!",
    "r_world" : "Randomize enemies in groups with their respective World.",
    "r_type" : "Randomize enemies in groups with their respective species."
};

const e_presets_data = {
    "r_all_b" : [[20,21,200,199,170,57,58,24,25,80,94,95,308,272,120,73,74,75,76,264,342,130,240,230,303,195,238,369,146,177,54,370,104,105,158,414,100,46,118,119,101,47,48,63,98,394,413,131,61,323,102,134,262,271,232,269,352,476],[115,334,335,395,196,180,151,233,425,193,194,111,112,197]],
    "r_all" : [[115,334,335,395,196,180,151,233,425,193,194,111,112,197,60,26,20,21,200,199,170,57,58,24,25,80,94,95,308,272,120,73,74,75,76,264,342,92,93,338,136,326,130,240,230,303,195,238,369,146,177,54,370,104,105,158,414,100,46,118,119,101,47,48,63,98,109,62,394,413,131,61,323,102,134,262,271,232,269,352,476,114,304,298,299,300,115,334,335,395,196,180,151,233,425,193,194,111,112,197]],
    "r_world" : [
        [20,21,57,58,95,308,73,75,118],
        [24,25,54,80,94,105,158,414,63,98],
        [272,369,118,119,101],
        [120,195,370],
        [200,199,170,264,342,130,240,230,100,131,61,323,102,134,262,271],
        [74,76,146,60,26,303],
        [238,177,269],
        [104,46,101,47,48,134,232,352,476],
        [115,334,335,395,196,180,151,233,425,193,194,111,112,197]
    ],
    "r_type" : [
        [20,21,200,199,170],
        [57,58,118,119],
        [24,25,60,26,54,370],
        [80,94,95,308,272,120],
        [73,74,75,76,264,342],
        [92,93,338,136,114,304,298,299,300],
        [130,240,230],
        [303,352,269,101,232],
        [146,177,104,47,48,63,98],
        [105,158,414,100,134],
        [131,61,323,102,262,271]
    ]
}

const t_presets_desc = {
    "t_r_all" : "All the blocks (Brick Blocks, ? Blocks and Hidden Blocks) will be randomized (Except Vine blocks). Hidden blocks may turn visible.",
    "t_r_ex_sec" : "All the blocks (Brick Blocks, ? Blocks and Hidden Blocks) will be randomized (Except Vine blocks), but hidden blocks will remain hidden.",
    "t_r_pup" : "Only blocks with power-ups will be randomized.",
    "t_r_pup_m" : "Blocks with power-ups will be randomized both in block type and power-up.",
    "t_r_none" : "Blocks wil not be randomized"
};

/*
const t_presets_data = {
    "t_r_all": [[17,18,19,20,22,23,24,25,26,27,28,29,30,31,33,34,35,36,37,38,39,40,41,43,44,45,46,47,48]],
    "t_r_ex_sec" : [[17,18,19,20,22,23,24,25],[26,27,28,29,30,31,33,34,35,36,37,38,39,40,41,43,44,45,46,47,48]],
    "t_r_pup" : [[39,40,41,44,45,46,47,48],[29,30,31,33,34,35,36,37]],
    "t_r_pup_m" : [[39,40,41,44,45,46,47,48,29,30,31,33,34,35,36,37]],
    "t_r_none" : [[]]
}*/
const t_presets_data = {
    
}


// Level options - Skip / Group level
const lvlJson = {
    "Secret":["01-03.arc","02-04.arc","02-06.arc","03-04.arc","03-05.arc","03-21.arc","04-21.arc","04-22.arc","05-21.arc","06-05.arc","06-06.arc","07-21.arc","07-22.arc","08-02.arc"],
    "Cannon":["01-36.arc","02-36.arc","03-36.arc","04-36.arc","05-36.arc","06-36.arc",],
    "Toad":["01-26.arc","01-27.arc","01-28.arc","01-29.arc","02-26.arc","02-27.arc","02-28.arc","03-26.arc","03-27.arc","03-28.arc","03-29.arc","04-26.arc","04-27.arc","04-28.arc","04-29.arc","05-26.arc","05-27.arc","05-28.arc","05-29.arc","06-26.arc","06-27.arc","06-28.arc","07-26.arc","07-27.arc","07-28.arc","07-29.arc","08-26.arc","08-27.arc","08-28.arc","09-26.arc","09-27.arc","09-28.arc"]
}

var lvList_skip = ["Texture","02-24.arc","01-40.arc","01-41.arc","01-42.arc"]
var lvList_same = []