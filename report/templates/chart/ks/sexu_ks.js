fetch("/Api/sumario/grafiku/sexu/")
.then(response => response.json())
.then(data => {

    new Chart(document.getElementById('sexuChart'), {

        type: 'doughnut',

        data: {

            labels: data.label,

            datasets: [{
                data: data.obj
            }]
        },

        options: {
            responsive: true,
            maintainAspectRatio: false, 
            resizeDelay: 150,         
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }

    });

});