
function add(){
    let dikt = document.getElementById("dikt").value;
    let xml = `<dikt_entry><dikt>${dikt}</dikt></dikt_entry>`

    let addReq = new XMLHttpRequest();
    addReq.open("POST", "http://138.68.92.43:8180/dikt", true);
    addReq.setRequestHeader("Content-Type", "application/xml");
    addReq.withCredentials = true;
    addReq.send(xml);

    addReq.onload = function(){
        if(addReq.status == 200){
	    let feedback = addReq.responseXML.getElementsByTagName("tilbakemelding")[0].textContent;
	    console.log("Add operation:", feedback);
	    if(feedback.includes("SUCCESS")){
                document.body.innerHTML = "<h1>Diktet har nå blitt lagt til</h1>"
	    }
            else{
                document.body.innerHTML = "<h1>En feil oppsto under opprettelse av dikt</h1>"
            }
	    document.body.innerHTML += "<a href=index.html>Tilbake til hovedsiden</a>"
        }
    }
}
