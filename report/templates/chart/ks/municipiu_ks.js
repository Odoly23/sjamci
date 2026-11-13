fetch("/Api/sumario/grafiku/ks/municipiu/")
.then(response => response.json())
.then(data => {

    new Chart(document.getElementById('municipiuChart'), {

        type: 'bar',

        data: {

            labels: data.label,

            datasets: [{
                label: 'Benefisiariu',
                data: data.obj
            }]
        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            scales: {
                y: {
                    beginAtZero: true
                }
            }

        }

    });

});