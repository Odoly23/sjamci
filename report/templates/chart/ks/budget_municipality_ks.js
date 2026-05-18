fetch("/Api/sumario/grafiku/budget-municipiu/")
.then(response => response.json())
.then(data => {

    new Chart(document.getElementById('budgetMunicipalityChart'), {

        type: 'bar',

        data: {

            labels: data.label,

            datasets: [{
                label: 'Budget',
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