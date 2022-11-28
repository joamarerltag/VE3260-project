
function update(){
    let diktid = document.getElementById("diktid").value;
    let dikt = document.getElementById("dikt").value;
    let xml = `<dikt_entry><dikt>${dikt}</dikt></dikt_entry>`

    let updateReq = new XMLHttpRequest();
    updateReq.open("PUT", `http://138.68.92.43:8180/dikt/${diktid}`, true);
    updateReq.setRequestHeader("Content-Type", "application/xml");
    updateReq.withCredentials = true;
    updateReq.send(xml);

    updateReq.onload = function(){
        if(updateReq.status == 200){
	    let feedback = updateReq.responseXML.getElementsByTagName("tilbakemelding")[0].textContent;
	    console.log("Update operation:", feedback);
	    if(feedback.includes("SUCCESS")){
                document.body.innerHTML = "<h1>Diktet har nå blitt endret</h1>"
	    }
            else{
                document.body.innerHTML = "<h1>En feil oppsto under endring av dikt</h1>"
            }
	    document.body.innerHTML += "<a href=index.html>Tilbake til hovedsiden</a>"
        }
    }
}
