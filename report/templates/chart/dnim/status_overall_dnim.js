fetch("/Api/sumario/api/dnim/status-overall/")
    .then(response => response.json())
    .then(data => {
        if (data.labels && data.labels.length > 0) {
            new Chart(document.getElementById('statusOverallChart'), {
                type: 'pie',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.data,
                        backgroundColor: ['#28a745', '#dc3545', '#ffc107', '#6c757d']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: { position: 'right' },
                        tooltip: { callbacks: { label: function(context) { return context.label + ': ' + context.raw + ' grupu'; } } }
                    }
                }
            });
        } else {
            document.getElementById('statusOverallChart').parentElement.innerHTML = '<div class="alert alert-warning text-center">La iha dadus ba grafik ne\'e</div>';
        }
    })
    .catch(error => {
        console.error('Error loading status overall chart:', error);
    });