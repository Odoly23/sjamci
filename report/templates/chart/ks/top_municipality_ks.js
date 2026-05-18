fetch("/Api/sumario/grafiku/top-municipality/")
.then(response => response.json())
.then(data => {

    new Chart(document.getElementById('topMunicipalityChart'), {

        type: 'bar',

        data: {

            labels: data.label,

            datasets: [{
                label: 'Top Municipality',
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