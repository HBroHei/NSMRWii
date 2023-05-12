var eList = []
var lvList = ["Texture","02-24.arc"]
var e_rand_sel = document.getElementById("e_rand_sel");
var t_rand_sel = document.getElementById("t_rand_sel");

var prevTab = "global";

document.getElementById("seed").value = Math.floor(Math.random()*(2147483647+2147483647))-2147483647

/*
document.getElementById("e_rand_sel").onchange = function(evt) {
    document.getElementById("r_description").innerHTML = e_presets_desc[e_rand_sel.options[e_rand_sel.options.selectedIndex].value]
}

document.getElementById("t_rand_sel").onchange = function(evt) {
    document.getElementById("t_r_description").innerHTML = t_presets_desc[t_rand_sel.options[t_rand_sel.options.selectedIndex].value]
}*/

document.getElementById("SSE").onchange = function(evt) {
    document.getElementById("S3-4").disabled = document.getElementById("SSE").checked
    document.getElementById("S3-4").checked = false;
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

function toJson(){
    lvList_skip = ["Texture","02-24.arc","01-40.arc","01-41.arc","01-42.arc"] //re-initalize
    
    //Set seed
    try{
        var seeds = Number(document.getElementById("seed").value)
    }
    catch(e){
        var seeds = document.getElementById("seed").value
    }

    if(document.getElementById("S08-24").checked){
        lvList_skip.push("08-24.arc");
    }
    //Set skipping list for levels
    getSkipOption("Secret",document.getElementById("SSE"))
    getSkipOption("Cannon",document.getElementById("SCannon"))
    getSkipOption("Toad",document.getElementById("SToadHse"))

    //Set tile raandomization
    let includeTilesList = []
    const qBlock = [38,39,40,41,42,43,44,45,46,47,48]
    const bBolck = [26,27,28,29,30,31,32,33,34,35,36,37]
    const hBlock = [17,18,19,20,21,22,23,24,25]
    const sBlock = [49,50,51,53,54]
    if(document.getElementById("block_blockRando").options[document.getElementById("block_blockRando").options.selectedIndex].value=="block_same"){
        if(document.getElementById("block_qBlock").checked){
            includeTilesList.push(qBlock);
        }
        if(document.getElementById("block_bBlock").checked){
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


    /*
    if(document.getElementById("SSE").checked){
        lvList.push("01-03.arc");
        lvList.push("02-04.arc");
        lvList.push("02-06.arc");
        lvList.push("03-04.arc");
        lvList.push("03-05.arc");
        lvList.push("03-21.arc");
        lvList.push("04-21.arc");
        lvList.push("04-22.arc");
        lvList.push("05-21.arc");
        lvList.push("06-05.arc");
        lvList.push("06-06.arc");
        lvList.push("07-21.arc");
        lvList.push("07-22.arc");
        lvList.push("08-02.arc");
    }*/
    const e_rand_sel = document.getElementById(("enemy_presets"))
    let eList = e_presets_data[e_rand_sel.options[e_rand_sel.options.selectedIndex].value];
    //let tileRan = t_presets_data[t_rand_sel.options[t_rand_sel.options.selectedIndex].value];
    let tileRan = includeTilesList;
    return {
        "Seed": seeds,
        "Reduce Lag": document.getElementById("LagReduce").checked,
        "Skip Level": lvList_skip,
        "Enemies": eList,
        "Enemy Variation": [],
        "Level Group": lvList_same,
        "Tile Group": tileRan
    }
}

function genJson(){
    //console.log(JSON.stringify(toJson()))
    //document.getElementById("jsonCode").innerHTML = JSON.stringify(toJson())
    var downBlob = new Blob([JSON.stringify(toJson())])
    //document.getElementById("fileGen").innerHTML = '<button>Generate</button>'
    document.getElementById("downFrame").src = window.URL.createObjectURL(downBlob)

    let _a = document.createElement('a');
    _a.download = 'config.json';
    _a.href = window.URL.createObjectURL(downBlob);
    _a.click();
}