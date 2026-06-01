fetch("/Api/sumario/api/dnim/rasio-mane-feto/")
    .then(response => response.json())
    .then(data => {
        if (data.labels && data.labels.length > 0) {
            new Chart(document.getElementById('rasioManeFetoChart'), {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [
                        {
                            label: 'Mane (%)',
                            data: data.mane,
                            backgroundColor: '#007bff'
                        },
                        {
                            label: 'Feto (%)',
                            data: data.feto,
                            backgroundColor: '#fd7e14'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    scales: {
                        x: { stacked: true, title: { display: true, text: 'Municipiu' } },
                        y: { stacked: true, max: 100, beginAtZero: true, title: { display: true, text: 'Persentase (%)' } }
                    },
                    plugins: {
                        tooltip: { callbacks: { label: function(context) { return context.dataset.label + ': ' + context.raw + '%'; } } }
                    }
                }
            });
        } else {
            document.getElementById('rasioManeFetoChart').parentElement.innerHTML = '<div class="alert alert-warning text-center">La iha dadus ba grafik ne\'e</div>';
        }
    })
    .catch(error => {
        console.error('Error loading rasio mane feto chart:', error);
    });