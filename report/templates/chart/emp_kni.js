fetch("/Api/sumario/grafiku/trabalhador/")
.then(response => response.json())
.then(data => {

    new Chart(document.getElementById('employeeChart'), {

        type: 'bar',

        data: {
            labels: data.label,

            datasets: [{
                label: 'Total',
                data: data.obj
            }]
        },

        options: {
            responsive: true
        }

    });

});
