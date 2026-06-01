fetch("/Api/sumario/api/dnim/total-valor-per-tinan/")
    .then(response => response.json())
    .then(data => {
        if (data.labels && data.labels.length > 0) {
            new Chart(document.getElementById('valorTinanChart'), {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Valor ($)',
                        data: data.data,
                        borderColor: '#17a2b8',
                        backgroundColor: 'rgba(23, 162, 184, 0.1)',
                        tension: 0.1,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    scales: {
                        y: { beginAtZero: true, title: { display: true, text: 'Valor ($)' } },
                        x: { title: { display: true, text: 'Tinan' } }
                    },
                    plugins: {
                        tooltip: { callbacks: { label: function(context) { return '$' + context.raw.toLocaleString(); } } }
                    }
                }
            });
        } else {
            document.getElementById('valorTinanChart').parentElement.innerHTML = '<div class="alert alert-warning text-center">La iha dadus ba grafik ne\'e</div>';
        }
    })
    .catch(error => {
        console.error('Error loading valor per tinan chart:', error);
    });