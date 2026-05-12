$(document).ready( function () {
    var table = $('#example').removeAttr('width').DataTable( {
        "scrollY": "50vh",
        "scrollX": true,
        "scrollCollapse": true,
        "paging": true,
        searchBuilder: true,
        buttons:[
            {
                extend: 'excelHtml5',
                autoFilter: true,
                sheetName: 'Exported data'
            },
        ],
        dom: 'Bfrtip',
        responsive: {
            details: {
                type: 'column'
            }
        },
        columnDefs: [
            {
                className: 'dtr-control',
                orderable: false,
                targets:   0
            },
        ],
        "deferRender": true
    });
} );