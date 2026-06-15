fetch("/Api/sumario/grafiku/size/")
.then(response => response.json())
.then(data => {
    new Chart(document.getElementById('sizeChart'), {
        type: 'bar',
        data: {
            labels: data.label,
            datasets: [{
                label: 'Business Size',
                data: data.obj
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true
        }
    });
});