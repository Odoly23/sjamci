document.addEventListener("DOMContentLoaded", function () {

    // =====================================
    // MAP
    // =====================================

    var map = L.map('map', {
        center: [-8.5569, 125.5603],
        zoom: 8
    });

    // =====================================
    // GOOGLE MAP
    // =====================================

    var googleMaps = L.tileLayer(
        'http://{s}.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}',
        {
            maxZoom: 20,
            subdomains: ['mt0', 'mt1', 'mt2', 'mt3']
        }
    );

    googleMaps.addTo(map);

    // =====================================
    // YELLOW ICON
    // =====================================

    var yellowIcon = new L.Icon({

        iconUrl:
            'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-gold.png',

        shadowUrl:
            'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',

        iconSize: [25, 41],

        iconAnchor: [12, 41],

        popupAnchor: [1, -34],

        shadowSize: [41, 41]

    });

    // =====================================
    // CLUSTER
    // =====================================

    var markers = L.markerClusterGroup({

        showCoverageOnHover: false,

        spiderfyOnMaxZoom: true,

        zoomToBoundsOnClick: true,

        iconCreateFunction: function(cluster) {

            return L.divIcon({

                html: `
                    <div style="
                        background:rgba(40,167,69,0.5);
                        border:2px solid #28a745;
                        width:45px;
                        height:45px;
                        border-radius:50%;
                        display:flex;
                        justify-content:center;
                        align-items:center;
                        color:white;
                        font-weight:bold;
                        font-size:16px;
                    ">
                        ${cluster.getChildCount()}
                    </div>
                `,

                className: 'custom-cluster',

                iconSize: [45, 45]

            });

        }

    });

    // =====================================
    // FETCH DATA
    // =====================================

    fetch("/Suave-Home/Sasa/grafiku/gis/")

    .then(response => response.json())

    .then(data => {

        if (!data.obj) return;

        data.obj.forEach(item => {

            if (!item.latitude || !item.longitude) return;

            // =====================================
            // MARKER
            // =====================================

            var marker = L.marker(
                [
                    parseFloat(item.latitude),
                    parseFloat(item.longitude)
                ],
                {
                    icon: yellowIcon
                }
            );

            // =====================================
            // POPUP
            // =====================================

            marker.bindPopup(`

                <div style="min-width:220px">

                    <h6 style="font-weight:bold">
                        ${item.name}
                    </h6>

                    <table class="table table-sm mb-0">

                        <tr>
                            <th>Naran</th>
                            <td>${item.owner}</td>
                        </tr>

                        <tr>
                            <th>Sector</th>
                            <td>${item.sector}</td>
                        </tr>

                        <tr>
                            <th>Municipality</th>
                            <td>${item.municipality}</td>
                        </tr>

                        <tr>
                            <th>Village</th>
                            <td>${item.village}</td>
                        </tr>

                    </table>

                </div>

            `);

            markers.addLayer(marker);

        });

        map.addLayer(markers);

        // =====================================
        // FIT BOUNDS
        // =====================================

        if (markers.getLayers().length > 0) {

            map.fitBounds(
                markers.getBounds(),
                {
                    padding: [20, 20]
                }
            );

        }

    })

    .catch(error => {

        console.error(error);

    });

});