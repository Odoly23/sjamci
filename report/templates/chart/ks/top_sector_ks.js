fetch("/Api/sumario/grafiku/top-sector/")
.then(response => response.json())
.then(data => {

    new Chart(document.getElementById('topSectorChart'), {

        type: 'bar',

        data: {

            labels: data.label,

            datasets: [{
                label: 'Top Sector',
                data: data.obj
            }]
        },

        options: {

            responsive: true,

            maintainAspectRatio: false

        }

    });

});