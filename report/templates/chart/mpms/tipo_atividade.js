fetch("/Api/sumario/tipo-atividade/")
  .then(r => r.json())
  .then(data => {
    new Chart(document.getElementById('tipoAtividadeChart'), {
      type: 'bar',
      data: {
        labels: data.label,
        datasets: [{
          label: 'Total',
          data: data.obj,
          backgroundColor: '#9b59b6',
          borderRadius: 4,
        }]
      },
      options: {
        indexAxis: 'y',   // horizontal bar
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { beginAtZero: true, ticks: { stepSize: 1 } }
        }
      }
    });
  });
