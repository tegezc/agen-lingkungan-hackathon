<script>
    import SensorChart from '$lib/components/SensorChart.svelte';
    import AlertsTable from '$lib/components/AlertsTable.svelte';
    import ManualAlertPanel from '$lib/components/ManualAlertPanel.svelte';
</script>

<div class="container">
    <h1>Live Monitoring: Ketinggian Air Katulampa</h1>
    <p>Sensor ID: <b>clw-ktl-01</b></p>
    
    <div class="chart-container">
        <SensorChart sensorId={'clw-ktl-01'} />
    </div>
    
     <hr class="divider" />
    
    <AlertsTable />

    <hr class="divider" />
    
    <ManualAlertPanel />
</div>

<style>
    .container {
        max-width: 900px;
        margin: 2rem auto;
        padding: 2rem;
        background: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        font-family: sans-serif;
    }
    .chart-container {
        margin-top: 2rem;
    }
    .divider {
        margin-top: 2.5rem;
        margin-bottom: 2.5rem;
        border: 0;
        border-top: 1px solid #eee;
    }
</style>