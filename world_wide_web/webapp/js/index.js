console.log("Script start");

if (navigator && navigator.serviceWorker) {
    navigator.serviceWorker.register('../../sw.js');
}

function addStateLinks(){
    if(!loggedIn && connection){
        let loginLink = document.createElement("a");
        loginLink.setAttribute("href", "login.html");
        loginLink.textContent = "Logg inn";
        document.body.insertBefore(loginLink, document.body.firstChild);
    }
    else if(!loggedIn && !connection){
        let header = document.createElement("h1");
        header.textContent = "Kunne ikke sjekke login-status. Kan hende du er i offline-modus."
        document.body.insertBefore(header, document.body.firstChild);
    }
    else{
        let logoutLink = document.createElement("a");
	logoutLink.setAttribute("href", "logout.html");
	logoutLink.textContent = "Logg ut";
        let addLink = document.createElement("a");
	addLink.setAttribute("href", "add.html");
	addLink.textContent = "Legg til nytt dikt";
        let updateLink = document.createElement("a");
	updateLink.setAttribute("href", "update.html");
	updateLink.textContent = "Endre et av dine dikt";
        let deleteLink = document.createElement("a");
	deleteLink.setAttribute("href", "delete.html");
	deleteLink.textContent = "Slett et av dine dikt";
        let deleteAllLink = document.createElement("a");
	deleteAllLink.setAttribute("href", "deleteall.html");
	deleteAllLink.textContent = "Slett alle dine dikt";

	document.body.insertBefore(deleteAllLink, document.body.firstChild);
	document.body.insertBefore(deleteLink, document.body.firstChild);
	document.body.insertBefore(updateLink, document.body.firstChild);
	document.body.insertBefore(addLink, document.body.firstChild);
	document.body.insertBefore(logoutLink, document.body.firstChild);
    }
}

let loggedIn = false;
let connection = true;
let cookies = document.cookie.split(";");
let sessionId = "";
for(let i = 0; i < cookies.length; i++){
    if(cookies[i].includes("sessionId")){
        sessionId = cookies[i].split("=")[1];
        break;
    }
}

let loginTest = new XMLHttpRequest();
loginTest.open("PUT", "http://138.68.92.43:8180/dikt/0", true);
loginTest.setRequestHeader("Content-Type", "application/xml");
loginTest.withCredentials = true;
loginTest.send();
loginTest.onloadend = function(){
    if(loginTest.status==200){
	let loginTestXML = loginTest.responseXML;
	let feedback = loginTestXML.getElementsByTagName("tilbakemelding")[0].textContent;
	if(feedback.includes("logget inn")){
            loggedIn = false;
	}
	else if(feedback.includes("innlogget")){
            loggedIn = true;
	}
        else{
            connection = false;
        }

    }else{
        connection = false;
    }
    if(document.readyState == "complete"){
	addStateLinks();
    }
}

window.onload = function(){
    console.log("Window loaded");
    if(loginTest.readyState == 4){
	addStateLinks();
    }
}

console.log("Script end");
