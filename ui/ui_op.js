
function settingUp(name){
    eel.init_session(name)(call_Back)
    start_panel = document.getElementById("start-panel")
    head_panel = document.getElementById("head-panel")
    head_panel.style.display = "block"
    start_panel.style.display = "none"
}
function call_Back(output){
    console.log("---- >>> ",output)
    document.getElementById("display").innerHTML = output
}