var eList = []
var lvList = ["Texture","02-24.arc"]
var e_rand_sel = document.getElementById("e_rand_sel");
var t_rand_sel = document.getElementById("t_rand_sel");

var prevTab = "global";

loadChangelog();
document.getElementById("seed").value = Math.floor(Math.random()*(2147483647+2147483647))-2147483647

/*
document.getElementById("e_rand_sel").onchange = function(evt) {
    document.getElementById("r_description").innerHTML = e_presets_desc[e_rand_sel.options[e_rand_sel.options.selectedIndex].value]
}

document.getElementById("t_rand_sel").onchange = function(evt) {
    document.getElementById("t_r_description").innerHTML = t_presets_desc[t_rand_sel.options[t_rand_sel.options.selectedIndex].value]
}*/

function checkValid(ele, min, max){
    // This is just a clamp function lol
    ele.value = Math.min(Math.max(ele.value,min),max)
}

function loadChangelog(){
    fetch("../LATEST").then(a => a.text().then(txt => {
        document.getElementById("changelog_box").innerHTML = txt
    }))
}

function openWin(ele){
    document.getElementById("win_"+prevTab).style.display = "none";
    document.getElementById("win_"+ele.innerHTML.toLowerCase()).style.backgroundColor = "#edfdff";
    document.getElementById("tab_"+prevTab).classList.toggle("tab_chosen");
    //document.getElementById("win_world").style.display = "none";
    //document.getElementById("win_level").style.display = "none";
    //document.getElementById("win_general").style.display = "none";
    //document.getElementById("win_general").style.display = "none";
    console.log("win_"+ele.innerHTML.toLowerCase());
    document.getElementById("win_"+ele.innerHTML.toLowerCase()).style.display = "block";
    document.getElementById("win_"+ele.innerHTML.toLowerCase()).style.backgroundColor = "#c9f8ff";
    document.getElementById("tab_"+ele.innerHTML.toLowerCase()).classList.toggle("tab_chosen");
    prevTab = ele.innerHTML.toLowerCase();


}

function enableV2(){
    document.getElementById("exp_windRand").disabled = !document.getElementById("exp_v2enable").checked;
    document.getElementById("exp_panelRand").disabled = !document.getElementById("exp_v2enable").checked;
    document.getElementById("exp_darkRand").disabled = !document.getElementById("exp_v2enable").checked;
    document.getElementById("exp_rockRand").disabled = !document.getElementById("exp_v2enable").checked;
    document.getElementById("exp_lvlRand").disabled = !document.getElementById("exp_v2enable").checked;
}

function toJson(){
    lvList_skip = ["Texture","01-40.arc","01-41.arc","01-42.arc"] //re-initalize
    lvList_same = []

    //Set seed
    try{
        var seeds = Number(document.getElementById("seed").value)
    }
    catch(e){
        var seeds = document.getElementById("seed").value
    }

    /* LEGACY CODES
    if(document.getElementById("S08-24").checked){
        lvList_skip.push("08-24.arc");
    }*/
    // Get skipping special levels
    for(const lvl_skip_item of ["map_01-01","map_02-24","map_03-04","map_03-05","map_06-24","map_08-03","map_08-24"]){
        if(document.getElementById(lvl_skip_item).checked){
            const skipLvlName = lvl_skip_item.replace("map_","") + ".arc";
            lvList_skip.push(skipLvlName)
            // Check if item is in lvlJson_n and remove them if exist
            for(const items of Object.keys(lvlJson_n)){
                const lvlPosInArr = lvlJson_n[items].indexOf(skipLvlName);
                if(lvlPosInArr!=-1){
                    console.log("Removed " + skipLvlName)
                    lvlJson_n[items].splice(lvlPosInArr,1);
                }
            }
        }
    }

    //Set skipping list for levels
    //document.querySelector('input[name="rate"]:checked')
    // getSkipOption("Secret",document.getElementById("SSE"))
    // getSkipOption("Cannon",document.getElementById("SCannon"))
    // getSkipOption("Toad",document.getElementById("SToadHse"))
    getGroupOption("secret");
    getGroupOption("castle");
    getGroupOption("tower");
    getGroupOption("airship");
    getGroupOption("ambush");
    getGroupOption("cannon");
    getGroupOption("toads");

    console.log(lvList_same)

    var enemyVarients = {
        "60":["0000 0000 0000","0000 0000 0001"], // Spike top rando direction
        "63":[  // Spike ball
            "0000 0000 0000","0000 0000 0001","0000 0000 0002","0000 0000 0003",
            "0000 0000 0010","0000 0000 0011","0000 0000 0012","0000 0000 0013",
            "0000 0000 1000","0000 0000 1001","0000 0000 1002","0000 0000 1003",
            "0000 0000 1010","0000 0000 1011","0000 0000 1012","0000 0000 1013"
        ],
        "98":[  // BIG Spike ball
            "0000 0000 0000","0000 0000 0001","0000 0000 0002","0000 0000 0003",
            "0000 0000 0010","0000 0000 0011","0000 0000 0012","0000 0000 0013",
            "0000 0000 1000","0000 0000 1001","0000 0000 1002","0000 0000 1003",
            "0000 0000 1010","0000 0000 1011","0000 0000 1012","0000 0000 1013"
        ],
        "338":[]
    }

    //Set tile raandomization
    let includeTilesList = []
    const qBlock = [38,39,40,41,43,44,45,46,47,48]
    let bBolck = [26,27,28,29,30,31,33,34,35,36,37]
    const hBlock = [17,18,19,20,22,23,24,25]
    const sBlock = [49,50,53,54]

    const_s_qBlock = [
        "0000 0000 0000", // Nothing
        "0000 0000 0001", 
        "0000 0000 0002", 
        "0000 0000 0003", 
        "0000 0000 0004", 
        "0000 0000 0005", 
        "0000 0000 0006", 
        "0000 0000 0007", 
        "0000 0000 0008",
        "0000 0000 0009",
        "0000 0000 000A",
        "0000 0000 000B",
        "0000 0000 000C",
        "0000 0000 000D",
        "0000 0000 000E",
        "0000 0000 000F"  
    ]

    if(document.getElementById("block_blockRando").options[document.getElementById("block_blockRando").options.selectedIndex].value=="block_same"){
        if(document.getElementById("block_qBlock").checked){
            includeTilesList.push(qBlock);

        }
        if(document.getElementById("block_bBlock").checked){
            if(document.getElementById("block_exbBlock").checked){ // Exclude breakable bricks
                bBolck.shift();
            }
            includeTilesList.push(bBolck);
        }
        if(document.getElementById("block_hBlock").checked){
            includeTilesList.push(hBlock);
        }
        if(document.getElementById("block_sBlock").checked){
            includeTilesList.push(sBlock);
        }
    }
    else if(document.getElementById("block_blockRando").options[document.getElementById("block_blockRando").options.selectedIndex].value=="block_all"){
        if(document.getElementById("block_qBlock").checked){
            includeTilesList.join(qBlock);
        }
        if(document.getElementById("block_bBlock").checked){
            includeTilesList.join(bBolck);
        }
        if(document.getElementById("block_hBlock").checked){
            includeTilesList.join(hBlock);
        }
        if(document.getElementById("block_sBlock").checked){
            includeTilesList.join(sBlock);
        }
    }

    //Set Toad House randomisation
    // 1-Up blast
    if(document.getElementById("level_1upBlast_cb").checked){
        enemyVarients["412"] = [
            /*
                From the third section:
                1st byte: n-up, where byte value = n+1
                2nd byte: -----
                3rd byte: No handle boolean
                4th byte: right/up and left/down toggle
            */
            "0000 0000 0010", // 1up, right/up
            "0000 0000 0011", // 1up, left/down
            "0000 0000 1010", // 2up, right/up
            "0000 0000 1011", // 2up, left/down
            "0000 0000 2010", // 3up, right/up
            "0000 0000 2011", // 3up, left/down
            "0000 0000 3010", // 4up, right/up
            "0000 0000 3011" // 4up, left/down
        ]
    }

    // Star House
    if(document.getElementById("level_starHse_cb").checked){
        enemyVarients["203"] = [
            "0000 0000 0000", // Nothing
            "0000 0000 0002", // Mushroom
            "0000 0000 0003", // Fire Flower
            "0000 0000 0004", // Propeller
            "0000 0000 0005", // Penguin Suit
            "0000 0000 0006", // Mini shroom
            "0000 0000 0007", // Star
            "0000 0000 0008", // Ice Flower
            "0000 0000 000F"  // Random
        ]
    }

    // Koopa
    if(document.getElementById("ev_k_red").checked){
        enemyVarients["57"] = [
            "0000 0000 0000", // Green
            "0000 0000 0001"  // Red
        ]
    }

    // Fire Piranha Plant (Pipe)
    if(document.getElementById("ev_piranha_fireball_1").checked){
        if(enemyVarients["71"]===undefined){
            enemyVarients["71"] = []
        }
        enemyVarients["71"].push("0000 0000 0000")
    }
    if(document.getElementById("ev_piranha_fireball_2").checked){
        if(enemyVarients["71"]===undefined){
            enemyVarients["71"] = []
        }
        enemyVarients["71"].push("0000 0000 0001")
    }
    if(document.getElementById("ev_piranha_fireball_3").checked){
        if(enemyVarients["71"]===undefined){
            enemyVarients["71"] = []
        }
        enemyVarients["71"].push("0000 0000 0002")
    }
    if(document.getElementById("ev_piranha_fireball_6").checked){
        if(enemyVarients["71"]===undefined){
            enemyVarients["71"] = []
        }
        enemyVarients["71"].push("0000 0000 0003")
    }

    // Buillet Bill Launcher
    // Rise / Fall Varient
    highNib1 = Number(document.getElementById("ev_buillet_min_1").value).toString(16);
    highNib2 = Number(document.getElementById("ev_buillet_min_2").value).toString(16);
    lowNib1 = Number(document.getElementById("ev_buillet_max_1").value).toString(16);
    lowNib2 = Number(document.getElementById("ev_buillet_max_2").value).toString(16);
    // Filter out non-related data
    for(const rawDat of e_rflauncher_data){
        if(rawDat[12]>=highNib1 && rawDat[12]<=highNib2 && rawDat[13]>=lowNib1 && rawDat[13]<=lowNib2){
            enemyVarients["338"].push(rawDat)
        }
    }
    // Wind Speed
    if(document.getElementById("ev_wind_visual").checked){
        if(enemyVarients["90"]===undefined){
            enemyVarients["90"] = []
        }
        enemyVarients["90"].push("0000 4500 0000")
    }
    if(document.getElementById("ev_wind_low").checked){
        if(enemyVarients["90"]===undefined){
            enemyVarients["90"] = []
        }
        enemyVarients["90"].push("0000 4500 0001")
    }
    if(document.getElementById("ev_wind_medium").checked){
        if(enemyVarients["90"]===undefined){
            enemyVarients["90"] = []
        }
        enemyVarients["90"].push("0000 4500 0002")
    }
    if(document.getElementById("ev_wind_high").checked){
        if(enemyVarients["90"]===undefined){
            enemyVarients["90"] = []
        }
        enemyVarients["90"].push("0000 4500 0003")
    }

    /*
    // Reserved?
    if(document.getElementById("").checked){
        // Reserved for future use?
    }
    */

    const e_rand_sel = document.getElementById(("enemy_presets"))
    let eList = e_presets_data[e_rand_sel.options[e_rand_sel.options.selectedIndex].value];
    //let tileRan = t_presets_data[t_rand_sel.options[t_rand_sel.options.selectedIndex].value];
    let tileRan = includeTilesList;

    // V2 checks
    if(document.getElementById("exp_v2enable").checked){
        let skipRandoList = ["03-05.arc"] // Skip but randomise list
        if(document.getElementById("exp_lvlRand").checked){
            skipRandoList = [
                "01-01.arc",
                "01-02.arc",
                "01-03.arc",
                "01-04.arc",
                "01-05.arc",
                "01-06.arc",
                "01-20.arc",
                "01-22.arc",
                "01-24.arc",
                "01-26.arc",
                "01-27.arc",
                "01-28.arc",
                "01-29.arc",
                "01-33.arc",
                "01-34.arc",
                "01-35.arc",
                "02-01.arc",
                "02-02.arc",
                "02-03.arc",
                "02-04.arc",
                "02-05.arc",
                "02-06.arc",
                "02-20.arc",
                "02-22.arc",
                "02-26.arc",
                "02-27.arc",
                "02-28.arc",
                "02-33.arc",
                "02-34.arc",
                "02-35.arc",
                "03-01.arc",
                "03-02.arc",
                "03-03.arc",
                "03-04.arc",
                "03-05.arc",
                "03-20.arc",
                "03-21.arc",
                "03-22.arc",
                "03-24.arc",
                "03-26.arc",
                "03-27.arc",
                "03-28.arc",
                "03-29.arc",
                "03-33.arc",
                "03-34.arc",
                "03-35.arc",
                "04-01.arc",
                "04-02.arc",
                "04-03.arc",
                "04-04.arc",
                "04-05.arc",
                "04-20.arc",
                "04-21.arc",
                "04-22.arc",
                "04-24.arc",
                "04-26.arc",
                "04-27.arc",
                "04-28.arc",
                "04-29.arc",
                "04-33.arc",
                "04-34.arc",
                "04-35.arc",
                "04-38.arc",
                "05-01.arc",
                "05-02.arc",
                "05-03.arc",
                "05-04.arc",
                "05-05.arc",
                "05-20.arc",
                "05-21.arc",
                "05-22.arc",
                "05-24.arc",
                "05-26.arc",
                "05-27.arc",
                "05-28.arc",
                "05-29.arc",
                "05-33.arc",
                "05-34.arc",
                "05-35.arc",
                "06-01.arc",
                "06-02.arc",
                "06-03.arc",
                "06-04.arc",
                "06-05.arc",
                "06-06.arc",
                "06-22.arc",
                "06-24.arc",
                "06-26.arc",
                "06-27.arc",
                "06-28.arc",
                "06-33.arc",
                "06-34.arc",
                "06-35.arc",
                "06-38.arc",
                "07-01.arc",
                "07-02.arc",
                "07-03.arc",
                "07-04.arc",
                "07-05.arc",
                "07-06.arc",
                "07-21.arc",
                "07-22.arc",
                "07-24.arc",
                "07-26.arc",
                "07-27.arc",
                "07-28.arc",
                "07-29.arc",
                "07-33.arc",
                "07-34.arc",
                "07-35.arc",
                "08-01.arc",
                "08-02.arc",
                "08-03.arc",
                "08-04.arc",
                "08-05.arc",
                "08-06.arc",
                "08-07.arc",
                "08-22.arc",
                "08-26.arc",
                "08-27.arc",
                "08-28.arc",
                "08-33.arc",
                "08-34.arc",
                "08-35.arc",
                "08-38.arc",
                "09-01.arc",
                "09-02.arc",
                "09-03.arc",
                "09-04.arc",
                "09-05.arc",
                "09-06.arc",
                "09-07.arc",
                "09-08.arc",
                "09-26.arc",
                "09-27.arc",
                "09-28.arc",
                "08-24.arc",
                "01-36.arc",
                "01-40.arc",
                "01-41.arc",
                "01-42.arc",
                "02-24.arc",
                "02-36.arc",
                "03-36.arc",
                "04-36.arc",
                "05-36.arc",
                "06-36.arc"
            ]
        }

        return {
            "Seed": seeds,
            "Reduce Lag": document.getElementById("LagReduce").checked,
            "Skip Level": lvList_skip,
            "Enemies": eList,
            "Enemy Variation": enemyVarients,
            "Secret Exit List": ["01-03.arc","02-04.arc","02-06.arc","03-04.arc","03-05.arc","03-21.arc","04-21.arc","04-22.arc","05-21.arc","06-05.arc","06-06.arc","07-21.arc","07-22.arc","08-02.arc"],
            "Skip But Randomise" : skipRandoList,
            "Tile Group": tileRan,
            "Wind Chance": Number(document.getElementById("exp_windRand").value),
            "Dark Chance": Number(document.getElementById("exp_darkRand").value),
            "Rock Chance": Number(document.getElementById("exp_rockRand").value),
            "Power-up Panel Shuffle": document.getElementById("exp_panelRand").value,
            "Patches" : {
                "09-05 Pipe" : true
            },
        }
    }
    else{
        return {
            "Seed": seeds,
            "Reduce Lag": document.getElementById("LagReduce").checked,
            "Entrance Randomisation": document.getElementById("exp_entRand").checked,
            "Skip Level": lvList_skip,
            "Enemies": eList,
            "Enemy Variation": enemyVarients,
            "Level Group": lvList_same,
            "Tile Group": tileRan
        }
    }
    
    
}

function genJson(){
    //console.log(JSON.stringify(toJson()))
    //document.getElementById("jsonCode").innerHTML = JSON.stringify(toJson())
    const outJSonText = document.getElementById("gen_beauty").checked ? [JSON.stringify(toJson(),null,4)] : [JSON.stringify(toJson())]
    var downBlob = new Blob(outJSonText)
    //document.getElementById("fileGen").innerHTML = '<button>Generate</button>'
    document.getElementById("downFrame").src = window.URL.createObjectURL(downBlob)

    let _a = document.createElement('a');
    _a.download = 'config.json';
    _a.href = window.URL.createObjectURL(downBlob);
    _a.click();
}
