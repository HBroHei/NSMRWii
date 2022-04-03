function getSkipOption(name,ele){
    if(ele.options[ele.options.selectedIndex].value=="s_same"){
        lvList_same.push(lvlJson[name])
    }
    else if(ele.options[ele.options.selectedIndex].value=="s_skip"){
        lvList_skip.push(...lvlJson[name])
    }
    else if(ele.options[ele.options.selectedIndex].value=="s_skip"){
        lvList_skip.push("03-04.arc")
    }
}