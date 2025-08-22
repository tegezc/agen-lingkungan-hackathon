<script>
    import { onMount } from 'svelte';
    import { getAlerts, submitFeedback } from '$lib/services/api.js';

    let alerts = [];
    let isLoading = true;
    let error = null;

    async function updateTable() {
        try {
            alerts = await getAlerts();
            error = null;
        } catch (e) {
            console.error(e);
            error = e.message;
        } finally {
            isLoading = false;
        }
    }

    async function handleFeedback(alertId, feedback) {
        try {
            await submitFeedback(alertId, feedback);
            // Refresh tabel untuk menunjukkan perubahan
            updateTable(); 
        } catch (e) {
            console.error(e);
            alert(`Gagal mengirim umpan balik: ${e.message}`);
        }
    }

    onMount(() => {
        updateTable();
        setInterval(updateTable, 10000); // Refresh tabel setiap 10 detik
    });
</script>

<h2>Log Keputusan & Umpan Balik Agen AI</h2>

{#if isLoading}
    <p>Memuat data peringatan...</p>
{:else if error}
    <p style="color: red;">{error}</p>
{:else}
    <table>
        <thead>
            <tr>
                <th>Waktu</th>
                <th>Alasan dari AI</th>
                <th>Kepercayaan AI</th>
                <th>Umpan Balik Petugas</th>
                <th>Aksi</th>
            </tr>
        </thead>
        <tbody>
            {#each alerts as alert (alert.id)}
                <tr>
                    <td>{new Date(alert.timestamp).toLocaleString('id-ID')}</td>
                    <td>{alert.reasoning}</td>
                    <td>{alert.confidence ? `${(alert.confidence * 100).toFixed(1)}%` : 'N/A'}</td>
                    <td><b>{alert.feedback ? alert.feedback.replace('_', ' ').toUpperCase() : 'Menunggu...'}</b></td>
                    <td class="feedback-buttons">
                        <button class="valid" on:click={() => handleFeedback(alert.id, 'valid')}>Valid 👍</button>
                        <button class="false-alarm" on:click={() => handleFeedback(alert.id, 'false_alarm')}>Alarm Palsu 👎</button>
                    </td>
                </tr>
            {/each}
        </tbody>
    </table>
{/if}

<style>
    /* ... (Salin-tempel semua style untuk tabel dan tombol dari index.html lama Anda ke sini) ... */
    table { border-collapse: collapse; width: 100%; margin-top: 20px; font-size: 14px; }
    th, td { padding: 12px 15px; border-bottom: 1px solid #ddd; text-align: left; }
    thead tr { background-color: #f7f7f7; font-weight: bold; }
    .feedback-buttons button { margin: 0 5px; padding: 5px 10px; border-radius: 5px; cursor: pointer; border: 1px solid #ccc; font-size: 12px; }
    .feedback-buttons .valid { background-color: #d4edda; border-color: #c3e6cb;}
    .feedback-buttons .false-alarm { background-color: #f8d7da; border-color: #f5c6cb;}
</style>