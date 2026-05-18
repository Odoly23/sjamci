fetch("/Api/sumario/grafiku/employee/")
.then(response => response.json())
.then(data => {

    new Chart(document.getElementById('employeeChart'), {

        type: 'bar',

        data: {

            labels: data.label,

            datasets: [{
                label: 'Employee',
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