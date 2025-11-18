const analyzeBtn = document.getElementById('analyzeBtn');
const areaInput = document.getElementById('areaInput');
const summaryText = document.getElementById('summaryText');
const tableHeader = document.getElementById('tableHeader');
const tableBody = document.getElementById('tableBody');
const chartCanvas = document.getElementById('chartCanvas');

let myChart;

analyzeBtn.addEventListener('click', () => {
    const area = areaInput.value.trim();
    if (!area) {
        alert("Please enter an area!");
        return;
    }

    // Example summary
    summaryText.innerText = `Data for ${area}: Population, Weather, and Services overview`;

    // Example table data
    const headers = ["Category", "Value"];
    const data = [
        ["Population", Math.floor(Math.random()*1000000)],
        ["Average Temperature", `${Math.floor(Math.random()*40)} °C`],
        ["Number of Schools", Math.floor(Math.random()*500)],
        ["Number of Hospitals", Math.floor(Math.random()*50)]
    ];

    // Populate table header
    tableHeader.innerHTML = "<tr>" + headers.map(h => `<th>${h}</th>`).join('') + "</tr>";

    // Populate table body
    tableBody.innerHTML = data.map(row => "<tr>" + row.map(cell => `<td>${cell}</td>`).join('') + "</tr>").join('');

    // Prepare chart data
    const chartLabels = data.map(item => item[0]);
    const chartValues = data.map(item => {
        const value = item[1];
        if (typeof value === "number") return value;
        const num = parseFloat(value);
        return isNaN(num) ? 0 : num;
    });

    // Destroy previous chart if exists
    if (myChart) myChart.destroy();

    // Create animated bar chart
    myChart = new Chart(chartCanvas, {
        type: 'bar',
        data: {
            labels: chartLabels,
            datasets: [{
                label: `Data for ${area}`,
                data: chartValues,
                backgroundColor: [
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(255, 159, 64, 0.8)',
                    'rgba(153, 102, 255, 0.8)',
                    'rgba(255, 99, 132, 0.8)'
                ],
                borderColor: [
                    'rgba(75, 192, 192, 1)',
                    'rgba(255, 159, 64, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 99, 132, 1)'
                ],
                borderWidth: 2,
                borderRadius: 10, // rounded bars for 3D feel
                hoverBorderWidth: 3
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.label}: ${context.raw}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 50
                    }
                },
                x: {
                    ticks: {
                        font: { size: 14 }
                    }
                }
            },
            animation: {
                duration: 1500,
                easing: 'easeOutBounce'
            }
        }
    });
});
