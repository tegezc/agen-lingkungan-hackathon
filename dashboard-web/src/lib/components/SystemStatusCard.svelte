<script>
    import { onMount } from 'svelte';
    import { getLatestStatus } from '$lib/services/api.js';

    let status = {
        status: 'loading', // default state
        level: 0,
        message: 'Loading system status...',
    };
    let intervalId;

    $: cardColor = getCardColor(status.status, status.level);
    $: textColor = getTextColor(status.status);
    $: icon = getStatusIcon(status.status);

    function getCardColor(currentStatus, level) {
        if (currentStatus === 'danger' && level >= 3) return '#dc3545'; // Merah (Bahaya)
        if (currentStatus === 'danger' && level === 2) return '#ffc107'; // Kuning (Waspada)
        if (currentStatus === 'safe') return '#28a745'; // Hijau (Aman)
        return '#6c757d'; // Abu-abu (Memuat/Unknown)
    }

    function getTextColor(currentStatus) {
        if (currentStatus === 'safe' || currentStatus === 'danger') {
            return 'white';
        }
        return 'white'; // Default white for loading/unknown
    }

    function getStatusIcon(currentStatus) {
        if (currentStatus === 'safe') return '✅';
        if (currentStatus === 'danger') return '⚠️';
        return '🔄'; // Loading/Unknown
    }

    async function fetchStatus() {
        try {
            const fetchedStatus = await getLatestStatus();
            status = fetchedStatus;
        } catch (e) {
            console.error('Failed to fetch system status:', e);
            status = {
                status: 'error',
                level: -1,
                message: `Failed to load: ${e.message}`,
            };
        }
    }

    onMount(() => {
        fetchStatus();
        intervalId = setInterval(fetchStatus, 10000); // Perbarui setiap 10 detik

        return () => clearInterval(intervalId); // Bersihkan interval saat komponen dihancurkan
    });
</script>

<div class="status-card" style="background-color: {cardColor}; color: {textColor};">
    <div class="status-icon">{icon}</div>
    <div class="status-content">
        <h2 class="status-title">{status.status.toUpperCase()}</h2>
        <p class="status-message">{status.message}</p>
        {#if status.level > 0}
            <p class="status-level">Alert Level: {status.level}</p>
        {/if}
    </div>
</div>

<style>
    .status-card {
        display: flex;
        align-items: center;
        gap: 20px;
        padding: 25px 30px;
        border-radius: 12px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
        margin-bottom: 30px;
        transition: background-color 0.3s ease, transform 0.2s ease;
        text-align: left;
    }
    .status-card:hover {
        transform: translateY(-3px);
    }
    .status-icon {
        font-size: 4em; /* Ukuran ikon emoji */
        line-height: 1;
    }
    .status-content {
        flex-grow: 1;
    }
    .status-title {
        margin: 0;
        font-size: 2.2em; /* Ukuran teks "AMAN", "BAHAYA" */
        font-weight: 700;
        letter-spacing: 1px;
    }
    .status-message {
        margin: 5px 0 0;
        font-size: 1.1em;
        line-height: 1.4;
    }
    .status-level {
        margin: 10px 0 0;
        font-size: 0.9em;
        font-weight: 600;
        opacity: 0.9;
    }
</style>