fetch("/Api/sumario/grafiku/growth/")
.then(response => response.json())
.then(data => {

    new Chart(document.getElementById('growthChart'), {

        type: 'line',

        data: {

            labels: data.label,

            datasets: [{
                label: 'Growth %',
                data: data.obj,
                tension: 0.5
            }]
        },

        options: {

            responsive: true,

            maintainAspectRatio: false

        }

    });

});