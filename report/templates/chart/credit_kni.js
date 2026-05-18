fetch("/Api/sumario/grafiku/credit/")
.then(response => response.json())
.then(data => {

    new Chart(document.getElementById('creditChart'), {

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