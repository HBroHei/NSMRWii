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

function toJson(){
    lvList_skip = ["Texture","02-24.arc","01-40.arc","01-41.arc","01-42.arc"] //re-initalize
    var tileRan = [[]]
    
    try{
        var seeds = Number(document.getElementById("seed").value)
    }
    catch(e){
        var seeds = document.getElementById("seed").value
    }

    if(document.getElementById("S08-24").checked){
        lvList_skip.push("08-24.arc");
    }
    if(document.getElementById("TileRandomize").checked){ //Temporay, implement the system that enemy use.
        tileRan = [[39,40,41,44,45,46,47,48],[29,30,31,33,34,35,36,37]]
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
        "Reduce Lag": document.getElementById("LagReduce").checked,
        "Skip Level": lvList_skip,
        "Enemies": eList,
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