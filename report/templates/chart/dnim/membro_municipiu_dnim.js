fetch("/Api/sumario/api/dnim/jumlah-membro-per-municipiu/")
    .then(response => response.json())
    .then(data => {
        if (data.labels && data.labels.length > 0) {
            new Chart(document.getElementById('membroMunicipiuChart'), {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [
                        {
                            label: 'Mane',
                            data: data.mane,
                            backgroundColor: '#007bff'
                        },
                        {
                            label: 'Feto',
                            data: data.feto,
                            backgroundColor: '#fd7e14'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    scales: {
                        y: { beginAtZero: true, title: { display: true, text: 'Jumlah Membro' } },
                        x: { title: { display: true, text: 'Municipiu' } }
                    },
                    plugins: {
                        tooltip: { callbacks: { label: function(context) { return context.dataset.label + ': ' + context.raw; } } }
                    }
                }
            });
        } else {
            document.getElementById('membroMunicipiuChart').parentElement.innerHTML = '<div class="alert alert-warning text-center">La iha dadus ba grafik ne\'e</div>';
        }
    })
    .catch(error => {
        console.error('Error loading membro per municipiu chart:', error);
    });