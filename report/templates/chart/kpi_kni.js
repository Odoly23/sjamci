fetch("/Api/sumario/grafiku/kpi/")
.then(response => response.json())
.then(data => {

    document.getElementById('totalBenef').innerHTML =
        data.total_benefisiariu;

    document.getElementById('totalBusiness').innerHTML =
        data.total_business;

    document.getElementById('totalBudget').innerHTML =
        data.total_budget;

    document.getElementById('totalEmployee').innerHTML =
        data.total_employee;

});