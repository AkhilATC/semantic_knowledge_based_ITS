
function settingUp(){
    eel.init_session()(call_Back)
    start_panel = document.getElementById("start-panel")
    head_panel = document.getElementById("head-panel")
    head_panel.style.display = "flex"
    start_panel.style.display = "none"
}
function call_Back(output){
    console.log("---- >>> ",output)
    if(output.status){
        document.getElementById("display").innerHTML = output.data
        notification(output.message)
    }else{
        document.getElementById("display").innerHTML = ""
        notification(output.message)
    }

}
function parseInfo(nodeInfo){
    console.log("got data here---"+nodeInfo);
}

function notification(msg){
    MsgData = "💬 : "+msg
    document.getElementById("notifID").innerHTML = MsgData;
}