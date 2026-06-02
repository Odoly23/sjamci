fetch("/Api/sumario/munisipiu/")
  .then(r => r.json())
  .then(data => {
    new Chart(document.getElementById('munChart'), {
      type: 'bar',
      data: {
        labels: data.label,
        datasets: [{
          label: 'Total Empresa',
          data: data.obj,
          backgroundColor: '#3498db',
          borderRadius: 4,
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, ticks: { stepSize: 1 } }
        }
      }
    });
  });


