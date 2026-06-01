fetch("/Api/sumario/api/dnim/total-valor-per-municipiu/")
    .then(response => response.json())
    .then(data => {
        if (data.labels && data.labels.length > 0) {
            new Chart(document.getElementById('valorMunicipiuChart'), {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Valor ($)',
                        data: data.data,
                        backgroundColor: '#ffc107'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    scales: {
                        y: { beginAtZero: true, title: { display: true, text: 'Valor ($)' } },
                        x: { title: { display: true, text: 'Municipiu' } }
                    },
                    plugins: {
                        tooltip: { callbacks: { label: function(context) { return '$' + context.raw.toLocaleString(); } } }
                    }
                }
            });
        } else {
            document.getElementById('valorMunicipiuChart').parentElement.innerHTML = '<div class="alert alert-warning text-center">La iha dadus ba grafik ne\'e</div>';
        }
    })
    .catch(error => {
        console.error('Error loading valor per municipiu chart:', error);
    });