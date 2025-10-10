// Gráfico 1: Ventas vs Gastos (Ejemplo de referencia)
const kpi_01 = JSON.parse(document.getElementById('kpi_01').value)

const ctx1 = document.getElementById('ventasGastosChart').getContext('2d');
const ventasGastosChart = new Chart(ctx1, {
    type: 'bar',
    data: {
        labels: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
        datasets: [
            {
                label: 'Ventas',
                data: kpi_01[0],
                backgroundColor: '#4a90e2'
            },
            {
                label: 'Gastos',
                data: kpi_01[1],
                backgroundColor: '#e94e4e'
            }
        ]
    },
    options: {
        responsive: true,
        plugins: {
            legend: { position: 'top' },
            title: { display: true, text: 'Ventas vs Gastos Mensual' }
        }
    }
});

// Gráfico 2: Gastos por Categoría (Ejemplo de referencia)
const kpi_02 = JSON.parse(document.getElementById('kpi_02').value)
const ctx2 = document.getElementById('gastosCategoriaChart').getContext('2d');

const gastosCategoriaChart = new Chart(ctx2, {
    type: 'pie',
    data: {
        labels: ['EPP', 'M', 'H', 'GG'],
        datasets: [{
            label: 'Gastos por Categoría',
            data: kpi_02,
            backgroundColor: ['#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: { position: 'right' },
            title: { display: true, text: 'Gastos por Categoría' }
        }
    }
});