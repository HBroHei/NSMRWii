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

function getGroupOption(name){
    const selectedVal = document.querySelector('input[name="skip_' + name + '"]:checked').value
    if(selectedVal=="skip"){
        lvList_skip.push(...lvlJson_n[name]) // append(lvl) for lvl in lvlJson_n[name]
    }
    else if(selectedVal=="same"){
        lvList_same.push(lvlJson_n[name]) // append array to array
    }
}