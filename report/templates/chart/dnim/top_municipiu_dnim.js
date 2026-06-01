fetch("/Api/sumario/api/dnim/top-municipiu/")
    .then(response => response.json())
    .then(data => {
        if (data.labels && data.labels.length > 0) {
            new Chart(document.getElementById('topMunicipiuChart'), {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Jumlah Grupu',
                        data: data.data,
                        backgroundColor: '#ffc107'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    scales: {
                        y: { beginAtZero: true, title: { display: true, text: 'Jumlah Grupu' } },
                        x: { title: { display: true, text: 'Municipiu' } }
                    },
                    plugins: {
                        tooltip: { callbacks: { label: function(context) { return context.raw + ' grupu'; } } }
                    }
                }
            });
        } else {
            document.getElementById('topMunicipiuChart').parentElement.innerHTML = '<div class="alert alert-warning text-center">La iha dadus ba grafik ne\'e</div>';
        }
    })
    .catch(error => {
        console.error('Error loading top municipiu chart:', error);
    });