var eList = []
var lvList = ["Texture","02-24.arc"]
var e_rand_sel = document.getElementById("e_rand_sel");

document.getElementById("seed").value = Math.floor(Math.random()*(2147483647+2147483647))-2147483647

document.getElementById("e_rand_sel").onchange = function(evt) {
    document.getElementById("r_description").innerHTML = e_presets_desc[e_rand_sel.options[e_rand_sel.options.selectedIndex].value]
}

document.getElementById("SSE").onchange = function(evt) {
    document.getElementById("S3-4").disabled = document.getElementById("SSE").checked
    document.getElementById("S3-4").checked = false;
}


/*
function addEnemy(){
    //Add enemy from the selected items
    if(document.getElementById(document.getElementById("eId").value).disabled){
        alert("'" + document.getElementById("eId").value + "' already exist in the list.")
        return
    }
    eList.push(document.getElementById("eId").value)
    var eOpt = document.createElement("option")
    eOpt.text = (enemyPreList.indexOf(document.getElementById("eId").value)!=-1) ? 
        document.getElementById("enemySel").options[enemyPreList.indexOf(document.getElementById("eId").value)].text : document.getElementById("eId").value
    eOpt.value = document.getElementById("eId").value
    document.getElementById("reList").add(eOpt)
    document.getElementById(document.getElementById("eId").value).disabled = true
    document.getElementById("eId").value = document.getElementById("enemySel").options[document.getElementById("enemySel").selectedIndex].value
}
function rmEnemy(){
    eList.splice(eList.indexOf(document.getElementById("reList").options[document.getElementById("reList").selectedIndex].text))
    if(enemyPreList.indexOf(document.getElementById("reList").options[document.getElementById("reList").selectedIndex].value)!=-1){
        var eOpt = document.createElement("option")
        eOpt.text = document.getElementById("reList").options[document.getElementById("reList").selectedIndex].text
        eOpt.value =document.getElementById("eId").value
        document.getElementById("enemySel").add(eOpt)
    }
    document.getElementById(document.getElementById("reList").options[document.getElementById("reList").selectedIndex].value).disabled = false
    document.getElementById("reList").remove(document.getElementById("reList").selectedIndex)
    document.getElementById("eId").value = document.getElementById("enemySel").options[document.getElementById("enemySel").selectedIndex].value

}

function addLevel(){
    if(document.getElementById(document.getElementById("lvlId").value).disabled){
        alert("'" + document.getElementById("lvlId").value + "' already exist in the list.")
        return
    }
    lvList.push(document.getElementById("lvlId").value)
    var lOpt = document.createElement("option")
    lOpt.text = (lvlPreList.indexOf(document.getElementById("lvlId").value)!=-1) ? 
        document.getElementById("lvlSel").options[lvlPreList.indexOf(document.getElementById("lvlId").value)].text : document.getElementById("lvlId").value
    lOpt.value = document.getElementById("lvlId").value
    document.getElementById("rlvList").add(lOpt)
    //document.getElementById("lvlSel").remove(lvlPreList.indexOf(document.getElementById("lvlId").value))
    document.getElementById(document.getElementById("lvlId").value).disabled = true
    document.getElementById("lvlId").value = document.getElementById("lvlSel").options[document.getElementById("lvlSel").selectedIndex].value

}
function rmLevel(){
    lvList.splice(lvList.indexOf(document.getElementById("rlvList").options[document.getElementById("rlvList").selectedIndex].text))
    if(lvlPreList.indexOf(document.getElementById("rlvList").options[document.getElementById("rlvList").selectedIndex].value)!=-1){
        var eOpt = document.createElement("option")
        eOpt.text = document.getElementById("rlvList").options[document.getElementById("rlvList").selectedIndex].text
        eOpt.value =document.getElementById("lvlId").value
        document.getElementById("lvlSel").add(eOpt)
    }
    document.getElementById(document.getElementById("rlvList").options[document.getElementById("rlvList").selectedIndex].value).disabled = false
    document.getElementById("rlvList").remove(document.getElementById("rlvList").selectedIndex)
    document.getElementById("lvlId").value = document.getElementById("lvlSel").options[document.getElementById("lvlSel").selectedIndex].value
}

document.getElementById("lvlSel").onchange = function(){
    document.getElementById("lvlId").value = document.getElementById("lvlSel").options[document.getElementById("lvlSel").selectedIndex].value
}
document.getElementById("enemySel").onchange = function(){
    document.getElementById("eId").value = document.getElementById("enemySel").options[document.getElementById("enemySel").selectedIndex].value
}*/

function toJson(){
    lvList_skip = ["Texture","02-24.arc","01-40.arc","01-41.arc","01-42.arc"] //re-initalize
    
    try{
        var seeds = Number(document.getElementById("seed").value)
    }
    catch(e){
        var seeds = document.getElementById("seed").value
    }

    if(document.getElementById("S08-24").checked){
        lvList_skip.push("08-24.arc");
    }
    getSkipOption("Secret",document.getElementById("SSE"))
    getSkipOption("Cannon",document.getElementById("SCannon"))
    getSkipOption("Toad",document.getElementById("SToadHse"))
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
    let eList = e_presets_data[e_rand_sel.options[e_rand_sel.options.selectedIndex].value];
    return {
        "Seed": seeds,
        "Skip Level": lvList_skip,
        "Enemies": eList,
        "Level Group": lvList_same
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