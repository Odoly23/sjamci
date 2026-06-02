fetch("/Api/sumario/jeneru/")
  .then(r => r.json())
  .then(data => {
    new Chart(document.getElementById('jeneruChart'), {
      type: 'doughnut',
      data: {
        labels: data.label,
        datasets: [{
          data: data.obj,
          backgroundColor: ['#3498db', '#e74c3c'],
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'bottom' },
          title: { display: false }
        }
      }
    });
  });