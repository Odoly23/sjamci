fetch("/Api/sumario/materia/")
  .then(r => r.json())
  .then(data => {
    new Chart(document.getElementById('materiaChart'), {
      type: 'doughnut',
      data: {
        labels: data.label,
        datasets: [{
          data: data.obj,
          backgroundColor: ['#27ae60', '#e67e22', '#8e44ad'],
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { position: 'bottom' } }
      }
    });
  });