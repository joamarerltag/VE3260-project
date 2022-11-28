function loadDikt(){
    let dikts = diktReq.responseXML.getElementsByTagName("dikt_entry");
    if(dikts != null){
        for(let i = 0; i < dikts.length; i++){
            let diktEntry = dikts[i];
            let diktid = diktEntry.getElementsByTagName("diktID")[0].textContent;
	    let epost = diktEntry.getElementsByTagName("epostadresse")[0].textContent;
            let dikt = diktEntry.getElementsByTagName("dikt")[0].textContent;
            document.body.innerHTML += `<p>DiktID: ${diktid}</p><p>Skrevet av: ${epost}</p><p>${dikt}</p><br>`;
        }
    }
    else{
        if(feedback.includes("SUCCESS")){
            document.body.innerHTML = "<h1>Diktet har nå blitt lagt til</h1>"
        }
        else{
            document.body.innerHTML = "<h1>En feil oppsto under opprettelse av dikt</h1>"
        }
        document.body.innerHTML += "<a href=index.html>Tilbake til hovedsiden</a>"
    }
}

let diktReq = new XMLHttpRequest();
diktReq.open("GET", "http://138.68.92.43:8180/dikt/", true);
diktReq.setRequestHeader("Content-Type", "application/xml");
diktReq.send();

window.onload = function (){
    if(diktReq.readyState == 4){
        loadDikt();
    }
}
diktReq.onload = function (){
    if(document.readyState == "complete"){
        loadDikt();
    }
}
