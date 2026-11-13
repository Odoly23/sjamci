fetch("/Api/sumario/grafiku/ks/status/")
.then(response => response.json())
.then(data => {

    new Chart(document.getElementById('statusChart'), {

        type: 'pie',

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