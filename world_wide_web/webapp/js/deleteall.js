function delall(){
    let deleteReq = new XMLHttpRequest();
    deleteReq.open("DELETE", "http://138.68.92.43:8180/dikt/", true);
    deleteReq.setRequestHeader("Content-Type", "application/xml");
    deleteReq.withCredentials = true;
    deleteReq.send();

    deleteReq.onload = function() {
        if(deleteReq.status == 200){
	    let deleteResp = deleteReq.responseXML;
	    let feedback = deleteResp.getElementsByTagName("tilbakemelding")[0].textContent;
	    if(feedback.includes("SUCCESS")){
                document.body.innerHTML = "<h1>Alle dine dikt har nå blitt slettet</h1>"
            }
            else{
                document.body.innerHTML = "<h1>En feil oppsto under sletting av alle dine dikt</h1>"
            }
            document.body.innerHTML += "<a href=index.html>Tilbake til hovedsiden</a>"
        }
    }
}
