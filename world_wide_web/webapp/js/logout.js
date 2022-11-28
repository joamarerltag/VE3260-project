function checkResponse(){
    if(logoutReq.status == 200){
        let logoutResp = logoutReq.responseXML;
        let feedback = logoutResp.getElementsByTagName("tilbakemelding")[0].textContent;
        if(feedback.includes("SUCCESS")){
            document.body.innerHTML = "<h1>Du har nå blitt logget ut</h1>"
        }else{
            document.body.innerHTML = "<h1>En feil oppsto under utlogging</h1>"
        }
        document.body.innerHTML += "<a href=index.html>Tilbake til hovedsiden</a>"
    }
}

let logoutReq = new XMLHttpRequest();
logoutReq.open("DELETE", "http://138.68.92.43:8180/logout", true);
logoutReq.setRequestHeader("Content-Type", "application/xml");
logoutReq.withCredentials = true;
logoutReq.send();

window.onload = function() {
    if(logoutReq.readyState == 4){
        checkResponse();
    }
}

logoutReq.onload = function() {
    if(document.readyState == "complete"){
        checkResponse();
    }
}
