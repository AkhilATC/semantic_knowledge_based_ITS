
function settingUp(){
    eel.init_session()(call_Back)
    start_panel = document.getElementById("start-panel")
    head_panel = document.getElementById("head-panel")
    head_panel.style.display = "flex"
    start_panel.style.display = "none"
}
function call_Back(output){
    console.log("---- >>> ",output)
    document.getElementById("display").innerHTML = output
    notification("Please note down ...📝")
}

function notification(msg){
    conersation = "💬 : "+msg
    document.getElementById("notifID").innerHTML = conersation
}