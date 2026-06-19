
var user_location = [-8.42565,125.32489084];
    var map = L.map('map').setView(user_location, 8);

    L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 18,
        id: 'mapbox/streets-v11',
        tileSize: 512,
        zoomOffset: -1,
        accessToken: 'pk.eyJ1IjoibG9iYXRvcGVyZWlyYSIsImEiOiJja2duaW8zOWcyMXFkMnp0ZWFjcm54M2xmIn0.C_ag6jiaMLzA8mz2hPc6xQ'
    }).addTo(map);

    
    var marker = L.marker([{{membru.membruLocation.latitude}},{{membru.membruLocation.lngitude}}]).addTo(map)
                .bindPopup('<b>{{membru.first_name}} </b><br/>{{membru.addressvillage}}, {{membru.addressadministrativepost}}, {{membru.addressmunicipality}}')
                .openPopup();
    



    
        
