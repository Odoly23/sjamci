function loadNotifBadge() {

    $.ajax({
        url: '/Notifikasaun/notification/badge/distribution/request/',
        type: 'GET',

        success: function(data){

            $('#notifbadge').text(data.total);

            if($('#notifpedidufoun').length){
                $('#notifpedidufoun').text(data.pedidu);
            }
        }
    });
}

loadNotifBadge();

setInterval(loadNotifBadge, 5000);