document.addEventListener("DOMContentLoaded", function () {
    f_kpi_03();
    f_kpi_04();
    f_kpi_05();
    f_kpi_06();
    f_kpi_07();
    f_kpi_08();
})

function f_kpi_03() {
    //Número de transacciones y crecimiento mensual
    const kpi_03 = JSON.parse(document.getElementById('kpi_03').textContent);
    const datosTransacciones = kpi_03[0];
    const datosCrecimiento = kpi_03[1];

    const etiquetasTrans = datosTransacciones[0];
    const valoresTrans = datosTransacciones[1];

    const etiquetasCrec = datosCrecimiento[0];
    const valoresCrec = datosCrecimiento[1];
    const ctx1 = document.getElementById('ventasGastosChart').getContext('2d');
    new Chart(ctx1, {
        type: 'bar', // base: barras
        data: {
            labels: etiquetasTrans,
            datasets: [
                {
                    label: 'Número de transacciones',
                    data: valoresTrans,
                    backgroundColor: 'rgba(75, 192, 192, 0.6)',
                    yAxisID: 'yTrans'
                },
                {
                    label: 'Crecimiento mensual (%)',
                    data: valoresCrec,
                    type: 'line', // línea sobre las barras
                    borderColor: 'rgba(255, 99, 132, 1)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    yAxisID: 'yCrec'
                }
            ]
        },
        options: {
            maintainAspectRatio: false,
            responsive: true,
            interaction: {
                mode: 'index',
                intersect: false
            },
            scales: {
                yTrans: {
                    type: 'linear',
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Número de transacciones'
                    },
                    beginAtZero: true
                },
                yCrec: {
                    type: 'linear',
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Crecimiento mensual (%)'
                    },
                    beginAtZero: false,
                    grid: {
                        drawOnChartArea: false
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Ventas: Número de transacciones y crecimiento mensual'
                },
                legend: {
                    position: 'top'
                }
            }
        }
    });
}

function f_kpi_04() {
    // Ticket Promedio Mensual
    const kpi_04 = JSON.parse(document.getElementById('kpi_04').textContent);
    const datosTicket = kpi_04;
    const etiquetas = datosTicket[0];
    const valores = datosTicket[1];

    const ctx = document.getElementById('graficoTicket').getContext('2d');

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: etiquetas,
            datasets: [{
                label: 'Ticket Promedio',
                data: valores,
                borderColor: 'rgba(54, 162, 235, 1)',
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            maintainAspectRatio: false,
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Ticket Promedio Mensual'
                },
                legend: { position: 'top' }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Ticket Promedio ($)'
                    }
                }
            }
        }
    });
}

function f_kpi_05() {
    //Gasto promedio por transacción (tipo barra horizontal simple)
    const datosGastos = JSON.parse(document.getElementById('kpi_05').textContent);
    const etiquetas = datosGastos[0];
    const gastoPromedio = datosGastos[1];
    new Chart(document.getElementById('graficoGastoPromedio'), {
        type: 'bar',
        data: {
            labels: etiquetas,
            datasets: [{
                label: 'Monto $',
                data: gastoPromedio,
                backgroundColor: ['rgba(255, 99, 132, 0.6)'],
                borderColor: ['rgba(255, 99, 132, 1)'],
                borderWidth: 1
            }]
        },
        options: {
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                legend: { display: false },
                title: {
                    display: true,
                    text: 'Gasto promedio por transacción'
                }
            },
            scales: {
                x: { beginAtZero: true }
            }
        }
    });
}

function f_kpi_06() {
    // Gráfico de eficiencia de gastos
    const datosGastos = JSON.parse(document.getElementById('kpi_06').textContent);
    const etiquetas = datosGastos[0];
    const eficiencia = datosGastos[1];
    const ctx2 = document.getElementById('graficoEficienciaGastos').getContext('2d');
    new Chart(ctx2, {
        type: 'bar',
        data: {
            labels: etiquetas,
            datasets: [{
                label: '% Gastos / Ventas',
                data: eficiencia,
                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            maintainAspectRatio: false,
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: '% de Gastos respecto a Ventas'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: 'Porcentaje (%)' },
                    max: 100
                }
            }
        }
    });
}

function f_kpi_07() {
    const datosGastos = JSON.parse(document.getElementById('kpi_07').textContent);
    const etiquetas = datosGastos[0];
    const gastos = datosGastos[1];
    const ctx1 = document.getElementById('graficoEvolucionGastos').getContext('2d');
    new Chart(ctx1, {
        type: 'line',
        data: {
            labels: etiquetas,
            datasets: [{
                label: 'Total de Gastos ($)',
                data: gastos,
                borderColor: 'rgba(255, 99, 132, 1)',
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            maintainAspectRatio: false,
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Evolución Mensual de Gastos'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: 'Monto ($)' }
                }
            }
        }
    });
}
function f_kpi_08() {
    //Gasto promedio por transacción (tipo barra horizontal simple)
    const kpi_08 = JSON.parse(document.getElementById('kpi_08').textContent);
    const etiquetas = kpi_08[0];
    const rentabilidad = kpi_08[1];

    const rentabilidadColores = rentabilidad.map(v => v >= 0 ? 'rgba(75,192,192,0.7)' : 'rgba(255,99,132,0.7)');
    new Chart(document.getElementById('graficoRentabilidadMensual'), {
        type: 'bar',
        data: {
            labels: etiquetas,
            datasets: [{
                label: 'Rentabilidad (%)',
                data: rentabilidad,
                backgroundColor: rentabilidadColores,
            }]
        },
        options: {
            maintainAspectRatio: false,
            indexAxis: 'y',
            scales: {
                x: {
                    max: 100,
                    ticks: { callback: v => v + '%' }
                }
            },
            plugins: {
                legend: { display: false },
                title: {
                    display: true,
                    text: 'Rentabilidad mensual en el año'
                },
                tooltip: {
                    callbacks: {
                        label: ctx => `${ctx.parsed.x.toFixed(1)}%`
                    }
                }
            },
        }
    });
}