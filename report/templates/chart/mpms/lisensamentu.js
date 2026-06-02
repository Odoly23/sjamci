fetch("/Api/sumario/lisensamentu/")
  .then(r => r.json())
  .then(data => {
    new Chart(document.getElementById('lisensamentuChart'), {
      type: 'doughnut',
      data: {
        labels: data.label,
        datasets: [{
          data: data.obj,
          backgroundColor: ['#2ecc71', '#e74c3c', '#f39c12'],
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { position: 'bottom' } }
      }
    });
  });

