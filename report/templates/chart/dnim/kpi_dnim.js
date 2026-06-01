fetch("/Api/sumario/api/dnim/kpi/")
    .then(response => response.json())
    .then(data => {
        document.getElementById('totalGrupu').innerText = data.total_grupu || 0;
        document.getElementById('totalParado').innerText = data.total_parado || 0;
        document.getElementById('totalValor').innerText = '$' + (data.total_valor || 0).toLocaleString();
        document.getElementById('totalMembro').innerText = data.total_membro || 0;
    })
    .catch(error => {
        console.error('Error loading KPI:', error);
    });