fetch("/Api/sumario/grafiku/municipiu/")
.then(response => response.json())
.then(data => {

    new Chart(document.getElementById('municipiuChart'), {

        type: 'bar',

        data: {
            labels: data.label,

            datasets: [{
                label: 'Total',
                data: data.obj,
                borderWidth: 1
            }]
        },

        options: {
            indexAxis: 'y',
            responsive: true
        }

    });

});
