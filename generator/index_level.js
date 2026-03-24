function getSkipOption(name,ele){
    if(ele.options[ele.options.selectedIndex].value=="s_same"){
        lvList_same.push(lvlJson[name])
    }
    else if(ele.options[ele.options.selectedIndex].value=="s_skip"){
        lvList_skip.push(...lvlJson[name])
    }
    else if(ele.options[ele.options.selectedIndex].value=="s_skip_3-4"){
        lvList_skip.push("03-04.arc")
    }
}

function getGroupOption(name, isV2){
    const selectedVal = document.querySelector(`input[name="skip_${name}"]:checked`).value;
    if(selectedVal=="skip"){
        lvList_skip.push(...lvlJson_n[name]); // append(lvl) for lvl in lvlJson_n[name]
    }
    else if(selectedVal=="same"){
        if(isV2){
            for(let lvlName of lvlJson_n[name]){
                if(!Object.hasOwn(lvlTypeList.Full, lvlName)){ lvlTypeList.Full[lvlName] = [name]; }
                else{ lvlTypeList.Full[lvlName].push(name); }
            }
        }
        else{
            lvList_same.push(lvlJson_n[name]); // append array to array
        }
    }
}