const valueLookup = {
    "SSE":{
        "s_all" : "Randomise with all other levels (May cause inaccessible levels)",
        "s_same": "Randomise with other secret exit levels. For example, 1-3 can become 2-6, but not 2-3. This greatly REDUCES the chance that some levels are forever inaccessible for a seed.",
        "s_skip": "Do not randomise levels that has secret exits. (i.e. 1-3 will stay as 1-3, 2-6 will stay as 2-6, etc) *Enemies and objects will still be randomised in that level*",
        "s_skip_3-4": "Randomise with other secret exit levels EXCEPT 3-4. This ENSURES all levels are accessible for a seed."
    },
    "CastleTower":{
        "s_all" : "Randomise with all other levels",
        "s_same": "Randomise within their group. i.e. Castle level will be randomised with other  For example, 1-3 can become 2-6, but not 2-3. This greatly REDUCES the chance that some levels are forever inaccessible for a seed.",
        "s_skip": "Do not randomise levels that has secret exits. (i.e. 1-3 will stay as 1-3, 2-6 will stay as 2-6, etc) *Enemies and objects will still be randomised in that level*",
        "s_skip_3-4": "Randomise with other secret exit levels EXCEPT 3-4. This ENSURES all levels are accessible for a seed."
    },
    "SCannon":{
        "s_all": "Randomise with all other NORMAL levels. *May cause a world to end early without granting access to the rest of the world*",
        "s_same":"Randomise with other cannon levels. Due to how the game works, this will only be an asthetic change, and will not randomise the destination of the cannon.",
        "s_skip":"Do not randomise cannon levels."
    },
    "SToadHse":{
        "s_all": "Randomise with all other NORMAL levels. This can make some Toad House permanently available even though the save file is not yet completed.",
        "s_same": "Randomise with other Toad House.  All Toad House would still be Toad House, but may have different minigame.",
        "s_skip": "Do not randomise Toad House levels."
    },
    "enemy_presets":{
        "r_type": "Randomise the enemies in groups of their species. (e.g. Normal Goomba -> Paragoomba)",
        "r_world": "Randomise the enemies in groups of each worlds.",
        "r_all_b": "Randomise ALL enemies to be different, except those that are immovable (like munchers). *Sometimes cause lag / crash*",
        "r_all": "Randomise ALL enemies. This also includes immovable enemies like muncher. *OFTEN cause lag / crash, ESPECIALLY in base game 9-7*"
    },
    "block_blockRando":{
        "block_none": "No blocks will be randomised",
        "block_same": "Blocks will be randomised, but would still visually looks the same. (? blocks would remain as ? blocks, brick blocks woukd still be brick blocks, etc.)",
        "block_all": "All blocks will be randomised. *May cause inaccessible area*"
    }
};


function changeOpt(ele){
    const selectedOption = ele.options[ele.selectedIndex];
    document.getElementById(ele.id + "_explain").textContent = valueLookup[ele.id][selectedOption.value];
}