// =============================
// CSRF TOKEN
// =============================
function getCSRFToken() {

    return document.querySelector(
        'meta[name="csrf-token"]'
    ).getAttribute('content');
}


// =============================
// READ NOTIFICATION
// =============================
function readNotification(id, link) {

    $.ajax({

        url: `/Notifikasaun/notification/read/${id}/`,

        type: 'POST',

        headers: {
            'X-CSRFToken': getCSRFToken()
        },

        success: function(){

            loadNotifBadge();
            loadNotifList();

            if(link){
                window.location.href = link;
            }
        }
    });

    return false;
}


// =============================
// LOAD LIST
// =============================
function loadNotifList() {

    $.ajax({

        url: '/Notifikasaun/notification/list/',

        type: 'GET',

        success: function(data){

            let html = '';

            if(data.length === 0){

                html = `
                    <a class="dropdown-item text-center text-muted">
                        La iha notifikasaun
                    </a>
                `;

            } else {

                data.forEach(function(item){

                    html += `
                    <a class="dropdown-item"
                       href="#"
                       onclick="return readNotification(${item.id}, '${item.link || ''}')">

                        <div class="d-flex justify-content-between">
                            <span>${item.title}</span>
                            <span class="badge badge-primary">NEW</span>
                        </div>

                        <small class="text-muted">
                            ${item.message}
                        </small>
                    </a>
                    `;
                });
            }

            $('#notifList').html(html);
        }
    });
}


// =============================
// AUTO LOAD
// =============================
loadNotifList();

setInterval(loadNotifList, 5000);