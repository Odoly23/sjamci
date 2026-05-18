fetch("/Api/sumario/grafiku/revenue-sector/")
.then(response => response.json())
.then(data => {

    new Chart(document.getElementById('revenueSectorChart'), {

        type: 'line',

        data: {

            labels: data.label,

            datasets: [{
                label: 'Revenue',
                data: data.obj,
                tension: 0.4
            }]
        },

        options: {

            responsive: true,

            maintainAspectRatio: false

        }

    });

});