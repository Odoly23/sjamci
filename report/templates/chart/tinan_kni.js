fetch("/Api/sumario/grafiku/tinan/")
.then(response => response.json())
.then(data => {

    new Chart(document.getElementById('tinanChart'), {
        type: 'line',
        data: {
            labels: data.label,
            datasets: [{
                label: 'Apoiu',
                data: data.obj,
                fill: true,
                backgroundColor: 'rgba(40, 167, 69, 0.2)', 
                borderColor: 'rgba(40, 167, 69, 1)',       
                borderWidth: 2,
                tension: 0.2 
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
