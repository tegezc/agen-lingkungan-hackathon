<script>
    import SensorChart from '$lib/components/SensorChart.svelte';
    import AlertsTable from '$lib/components/AlertsTable.svelte';
    import ManualAlertPanel from '$lib/components/ManualAlertPanel.svelte';
    import SystemStatusCard from '$lib/components/SystemStatusCard.svelte';
</script>

<div class="container">
     <h1>Dasbor Pemantauan & Komando Lingkungan</h1>
    <p>Sensor ID: <b>clw-ktl-01</b></p>
    <SystemStatusCard /> <hr class="divider" />
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
        max-width: 1100px;
        margin: 2rem auto;
        padding: 2.5rem;
        background: white;
        border-radius: 12px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    .chart-container {
        margin-top: 2rem;
        margin-bottom: 2.5rem;
    }
    .divider { 
        margin-top: 2.5rem;
        margin-bottom: 2.5rem;
        border: 0;
         border-top: 1px solid #e2e8f0;
    }
    h1 {
        color: #1a202c;
        font-size: 2.5em;
        margin-bottom: 0.5em;
    }
    p {
        color: #4a5568;
    }
</style>