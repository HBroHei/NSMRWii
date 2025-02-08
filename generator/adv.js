var groupProp = {
    "sprites":{},
    "lvlGrp":{},
    "tileGrp":{}
};
var curProp = ""


document.getElementById("sel_gp").onkeypress = (e) => {
    if(e.key=="enter"){
        e.preventDefault();
        document.getElementById("btn_tbgp").click();
    }
}
document.getElementById("btn_gpedit").onclick = (e) => {
    groupProp[curProp] = JSON.parse(document.getElementById("inp_tbgp").value);
    groupManager(curProp);
    document.getElementById("div_preview").textContent = JSON.stringify(groupProp);
}

function groupManager(selProp){
    // Show edit div
    document.getElementById("div_editAttr").style.display = "block";
    document.getElementById("div_addAttr").style.display = "none";
    // Clear select
    document.getElementById("sel_gp").innerHTML = "";
    curProp = selProp;
    // Add to select
    for(const [gp_key, gp_val] of Object.entries(groupProp[selProp])){
        let opt_gp = document.createElement("option");
        opt_gp.value = gp_val;
        opt_gp.textContent = gp_key;
        
        document.getElementById("sel_gp").appendChild(opt_gp);
    }
}