function login(){
    let epost = document.getElementById("epost").value;
    let passord = document.getElementById("passord").value;
    let loginXML = document.createElement("innlogging");
    loginXML.innerHTML = `<bruker><epostadresse>${epost}</epostadresse><passord>${passord}</passord></bruker>`;
    let loginReq = new XMLHttpRequest();
    loginReq.open("POST", "http://138.68.92.43:8180/login", true);
    loginReq.setRequestHeader("Content-Type", "application/xml");
    loginReq.withCredentials = true;
    loginReq.send(loginXML.innerHTML);
    loginReq.onload = function(){
	if(loginReq.status == 200){
	    let feedback = loginReq.responseXML.getElementsByTagName("tilbakemelding")[0].textContent;
            if(feedback.includes("SUCCESS")){
                document.body.innerHTML = "<h1>Du har nå blitt logget inn</h1>"
            }
            else{
                document.body.innerHTML = "<h1>En feil oppsto under innlogging</h1>"
            }
            document.body.innerHTML += "<a href=index.html>Tilbake til hovedsiden</a>"
	}
    }
}
