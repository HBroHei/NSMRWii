var eList = []
var lvList = ["Texture","02-24.arc"]
function addEnemy(){
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
    //document.getElementById("enemySel").remove(enemyPreList.indexOf(document.getElementById("eId").value))
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
}

function toJson(){
    return {
        "Skip": lvList,
        "Enemies": eList
    }
}

function genJson(){
    //console.log(JSON.stringify(toJson()))
    document.getElementById("jsonCode").innerHTML = JSON.stringify(toJson())
    var downBlob = new Blob([JSON.stringify(toJson())])
    //document.getElementById("fileGen").innerHTML = '<button>Generate</button>'
    document.getElementById("downFrame").src = window.URL.createObjectURL(downBlob)

    let _a = document.createElement('a');
    _a.download = 'config.json';
    _a.href = window.URL.createObjectURL(downBlob);
    _a.click();
}