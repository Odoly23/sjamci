fetch("/Api/sumario/api/dnim/tipu-industria/")
    .then(response => response.json())
    .then(data => {
        if (data.labels && data.labels.length > 0) {
            new Chart(document.getElementById('tipuIndustriaChart'), {
                type: 'pie',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.data,
                        backgroundColor: ['#007bff', '#28a745', '#ffc107', '#dc3545', '#17a2b8', '#6c757d', '#fd7e14', '#20c997', '#e83e8c', '#6610f2']
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
            document.getElementById('tipuIndustriaChart').parentElement.innerHTML = '<div class="alert alert-warning text-center">La iha dadus ba grafik ne\'e</div>';
        }
    })
    .catch(error => {
        console.error('Error loading tipu industria chart:', error);
    });