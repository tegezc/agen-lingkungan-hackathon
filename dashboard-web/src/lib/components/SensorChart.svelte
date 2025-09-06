<script>
    import { onMount } from 'svelte';
    import { Chart, registerables } from 'chart.js';
    import 'chartjs-adapter-date-fns';
    import { getHistory } from '$lib/services/api.js';

    export let sensorId;
    let canvasElement;
    let sensorChart;

    onMount(() => {
        Chart.register(...registerables);
        
        const ctx = canvasElement.getContext('2d');
        sensorChart = new Chart(ctx, {
            type: 'line',
            data: {
                datasets: [{
                    label: 'Ketinggian Air (cm)',
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1,
                    fill: false
                }]
            },
            options: {
                scales: {
                    x: {
                        type: 'time',
                        time: { unit: 'second', displayFormats: { second: 'HH:mm:ss' } },
                        title: { display: true, text: 'Time' }
                    },
                    y: {
                        beginAtZero: false,
                        title: { display: true, text: 'Water Level (cm)' }
                    }
                }
            }
        });

        updateChart();
        setInterval(updateChart, 5000); // Update setiap 5 detik
    });

    async function updateChart() {
        try {
            const data = await getHistory(sensorId);
            const labels = data.map(item => new Date(item.timestamp));
            const values = data.map(item => item.reading_value);

            sensorChart.data.labels = labels;
            sensorChart.data.datasets[0].data = values;
            sensorChart.update('quiet');
        } catch (error) {
            console.error('Error updating chart:', error);
        }
    }
</script>

<canvas bind:this={canvasElement}></canvas>