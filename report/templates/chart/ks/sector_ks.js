fetch("/Api/sumario/grafiku/sector/")
.then(response => response.json())
.then(data => {

    new Chart(document.getElementById('sectorChart'), {

        type: 'bar',

        data: {

            labels: data.label,

            datasets: [{
                label: 'Sector',
                data: data.obj
            }]
        },

        options: {

            indexAxis: 'y',

            responsive: true,

            maintainAspectRatio: false

        }

    });

});