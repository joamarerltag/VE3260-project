function get(){
    let diktid = document.getElementById("diktid").value;
    let diktReq = new XMLHttpRequest();
    diktReq.open("GET", `http://138.68.92.43:8180/dikt/${diktid}`, true);
    diktReq.setRequestHeader("Content-Type", "application/xml");
    diktReq.send();
    diktReq.onload = function(){
        if(diktReq.status == 200){
            let diktXML = diktReq.responseXML;
            let rootTag = diktXML.documentElement.tagName;
            if(rootTag == "dikt_entry"){
                let epost = diktXML.getElementsByTagName("epostadresse")[0].textContent;
                let dikt = diktXML.getElementsByTagName("dikt")[0].textContent;
                document.body.innerHTML = `<p>DiktID: ${diktid}</p><p>Skrevet av: ${epost}</p><p>${dikt}</p>`;
            }else{
                document.body.innerHTML = `<h1>En feil oppsto under henting av dikt`
            }
            document.body.innerHTML += "<a href=index.html>Tilbake til hovedsiden</a>"
        }
    }
}
