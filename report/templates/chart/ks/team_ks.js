fetch("/Api/sumario/grafiku/team/")
.then(response => response.json())
.then(data => {

    new Chart(document.getElementById('teamChart'), {

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