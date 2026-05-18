fetch("/Api/sumario/grafiku/status/")
.then(response => response.json())
.then(data => {

    new Chart(document.getElementById('statusChart'), {

        type: 'doughnut',

        data: {
            labels: data.label,

            datasets: [{
                data: data.obj
            }]
        },

        options: {
            responsive: true
        }

    });

});