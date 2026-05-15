fetch("/Api/sumario/grafiku/sexu/")
.then(response => response.json())
.then(data => {

    const ctx = document.getElementById('sexuChart');

    new Chart(ctx, {
        type: 'doughnut',

        data: {
            labels: data.label,

            datasets: [{
                label: 'Total',
                data: data.obj,
                borderWidth: 1
            }]
        },

        options: {
            responsive: true,

            plugins: {
                legend: {
                    position: 'bottom'
                },

                title: {
                    display: true,
                    text: 'Benefisiariu Tuir Sexu'
                }
            }
        }
    });

});
