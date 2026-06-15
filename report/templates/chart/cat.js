fetch("/Api/sumario/grafiku/cat/")
.then(response => response.json())
.then(data => {
    new Chart(document.getElementById('catChart'), {
        type: 'bar',
        data: {
            labels: data.label,
            datasets: [{
                label: 'Category Emp',
                data: data.obj
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true
        }
    });
});