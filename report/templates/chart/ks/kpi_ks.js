fetch("/Api/sumario/grafiku/kpi/")
.then(response => response.json())
.then(data => {

    const setValue = (id, value) => {
        const el = document.getElementById(id);

        if (el) {
            el.innerHTML = value ?? 0;
        }
    };

    setValue('totalBenef', data.total_benefisiariu);
    setValue('totalBusiness', data.total_business);
    setValue('totalBudget', data.total_budget);
    setValue('totalEmployee', data.total_employee);

    setValue('totalTeam', data.total_team);
    setValue('totalRevenue', data.total_revenue);
    setValue('totalAsset', data.total_asset);
    setValue('riskBusiness', data.total_risk);

})
.catch(error => {
    console.log('ERROR:', error);
});