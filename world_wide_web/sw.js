addEventListener('install', function (event) {
    let diktids = [];
    fetch("http://138.68.92.43:8180/dikt/")
	.then(response => response.text())
        .then(data => {
            diktids = data.match(/<diktID>(.*?)<\/diktID>/g).map(val => {
                return val.replace(/<\/?diktID>/g,'');
            });
            console.log(data);
            console.log(diktids);
            return diktids;
    }).then(diktids => {
    event.waitUntil(caches.open('core').then(function (cache) {
        cache.add(new Request('webapp/index.html'));
        cache.add(new Request('webapp/getall.html'));
        cache.add(new Request('webapp/get.html'));
        cache.add(new Request('files/css/interface.css'));
        cache.add(new Request('webapp/js/getall.js'));
        cache.add(new Request('webapp/js/get.js'));
        cache.add(new Request('webapp/js/index.js'));
        cache.add(new Request('http://138.68.92.43:8180/dikt/'));
        console.log(diktids);
        for(let i = 0; i < diktids.length; i++){
            cache.add(new Request(`http://138.68.92.43:8180/dikt/${diktids[i]}`));
        }
	return;
    }))
    })
    .catch(console.error);
});

// listen for requests
addEventListener('fetch', function (event) {
    var request = event.request;

    if (event.request.cache === 'only-if-cached' && event.request.mode !== 'same-origin') return;

//    if (request.headers.get('Accept').includes('text/html') || request.headers.get('Accept').includes('text/css') || request.headers.get('Accept').includes('text/javascript')) {
        event.respondWith(
	    fetch(request).then(function (response) {
	        return response;
	    }).catch(function (error) {
	        return caches.match(request);
	    })
	);
//    }
});
