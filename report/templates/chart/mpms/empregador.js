fetch("/Api/sumario/empregador/")
  .then(r => r.json())
  .then(data => {
    new Chart(document.getElementById('empregadorChart'), {
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
        plugins: { legend: { position: 'bottom' } }
      }
    });
  });
