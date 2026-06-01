fetch("/Api/sumario/api/dnim/grupu-status-per-municipiu/")
    .then(response => response.json())
    .then(data => {
        if (data.labels && data.labels.length > 0) {
            new Chart(document.getElementById('grupuStatusChart'), {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [
                        {
                            label: 'Ativo',
                            data: data.ativo,
                            backgroundColor: '#28a745'
                        },
                        {
                            label: 'Parado',
                            data: data.parado,
                            backgroundColor: '#dc3545'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    scales: {
                        x: { stacked: true },
                        y: { stacked: true, beginAtZero: true, title: { display: true, text: 'Jumlah Grupu' } }
                    },
                    plugins: {
                        legend: { position: 'top' },
                        tooltip: { callbacks: { label: function(context) { return context.dataset.label + ': ' + context.raw; } } }
                    }
                }
            });
        } else {
            document.getElementById('grupuStatusChart').parentElement.innerHTML = '<div class="alert alert-warning text-center">La iha dadus ba grafik ne\'e</div>';
        }
    })
    .catch(error => {
        console.error('Error loading grupu status chart:', error);
    });