document.addEventListener("DOMContentLoaded", function () {
    // Gráfico 1: Ventas vs Gastos + Remuneración Mensual
    const kpi_01 = JSON.parse(document.getElementById('kpi_01').textContent);

    const ctx1 = document.getElementById('ventasGastosChart').getContext('2d');
    const ventasGastosChart = new Chart(ctx1, {
        type: 'bar',
        data: {
            labels: kpi_01[0],
            datasets: [
                {
                    label: 'Ventas',
                    data: kpi_01[1],
                    backgroundColor: '#4a90e2'
                },
                {
                    label: 'Gastos',
                    data: kpi_01[2],
                    backgroundColor: '#e94e4e'
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'top' },
                title: { display: true, text: 'Ventas vs Gastos + Remuneración Mensual' }
            }
        }
    });

    // Gráfico 2: Gastos por Categoría (Ejemplo de referencia)
    const kpi_02 = JSON.parse(document.getElementById('kpi_02').textContent);
    const ctx2 = document.getElementById('gastosCategoriaChart').getContext('2d');

    const gastosCategoriaChart = new Chart(ctx2, {
        type: 'pie',
        data: {
            labels: kpi_02[0],
            datasets: [{
                label: 'Gastos por Categoría',
                data: kpi_02[1],
                backgroundColor: ['#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'right' },
                title: { display: true, text: 'Gastos por Categoría del Mes Actual' }
            }
        }
    });
});
