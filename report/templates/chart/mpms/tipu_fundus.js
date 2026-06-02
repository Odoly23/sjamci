fetch("/Api/sumario/tipu-fundus/")
  .then(r => r.json())
  .then(data => {
    new Chart(document.getElementById('tipuFundusChart'), {
      type: 'bar',
      data: {
        labels: data.labels,
        datasets: data.datasets.map(ds => ({
          ...ds,
          borderRadius: 3,
        }))
      },
      options: {
        responsive: true,
        scales: {
          x: { stacked: true },
          y: { stacked: true, beginAtZero: true }
        },
        plugins: {
          legend: { position: 'bottom' }
        }
      }
    });
  });