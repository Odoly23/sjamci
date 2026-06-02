fetch("/Api/sumario/kapital/")
  .then(r => r.json())
  .then(data => {
    new Chart(document.getElementById('kapitalChart'), {
      type: 'pie',
      data: {
        labels: data.label,
        datasets: [{
          data: data.obj,
          backgroundColor: ['#3498db', '#2ecc71', '#f39c12', '#e74c3c'],
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { position: 'bottom' } }
      }
    });
  });
