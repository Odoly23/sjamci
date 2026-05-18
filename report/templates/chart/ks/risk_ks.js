fetch("/Api/sumario/grafiku/risk/")
.then(response => response.json())
.then(data => {

    new Chart(document.getElementById('riskChart'), {

        type: 'doughnut',

        data: {

            labels: data.label,

            datasets: [{
                data: data.obj
            }]
        },

        options: {

            responsive: true,

            maintainAspectRatio: false

        }

    });

});