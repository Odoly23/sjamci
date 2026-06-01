fetch("/Api/sumario/api/dnim/top-10-grupu/")
    .then(response => response.json())
    .then(data => {
        if (data.labels && data.labels.length > 0) {
            new Chart(document.getElementById('topGrupuChart'), {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Valor ($)',
                        data: data.data,
                        backgroundColor: '#dc3545'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    indexAxis: 'y',
                    scales: {
                        x: { title: { display: true, text: 'Valor ($)' } },
                        y: { title: { display: true, text: 'Grupu' } }
                    },
                    plugins: {
                        tooltip: { callbacks: { label: function(context) { return '$' + context.raw.toLocaleString(); } } }
                    }
                }
            });
        } else {
            document.getElementById('topGrupuChart').parentElement.innerHTML = '<div class="alert alert-warning text-center">La iha dadus ba grafik ne\'e</div>';
        }
    })
    .catch(error => {
        console.error('Error loading top grupu chart:', error);
    });