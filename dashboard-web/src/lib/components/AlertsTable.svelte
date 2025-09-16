<script>
    import { onMount } from 'svelte';
    import { getAlerts, submitFeedback } from '$lib/services/api.js';

    let alerts = [];
    let isLoading = true;
    let error = null;
    let updatingId = null;

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
        updatingId = alertId;
        try {
            await submitFeedback(alertId, feedback);
            // Refresh table
            await updateTable(); 
        } catch (e) {
            console.error(e);
            alert(`Failed manual fedback: ${e.message}`);
        } finally {
            updatingId = null;
        }
    }

    onMount(() => {
        updateTable();
        setInterval(updateTable, 10000); // Refresh table 10 second
    });
</script>

<h2>AI Agent Decision & Feedback Log</h2>

{#if isLoading}
    <p>Loading alert data...</p>
{:else if error}
    <p style="color: red;">{error}</p>
{:else}
    <table>
        <thead>
            <tr>
                <th>Time</th>
                <th>AI Reasoning</th>
                <th>AI Confidence</th>
                <th>Operator Feedback</th>
                <th>Action</th>
            </tr>
        </thead>
        <tbody>
            {#each alerts as alert (alert.id)}
                <tr class:warning={alert.level === 2} class:danger={alert.level >= 3}>
                    <td>{new Date(alert.timestamp).toLocaleString('id-ID')}</td>
                    <td>{alert.reasoning}</td>
                    <td>{alert.confidence ? `${(alert.confidence * 100).toFixed(1)}%` : 'N/A'}</td>
                    <td><b>{alert.feedback ? alert.feedback.replace('_', ' ').toUpperCase() : 'Pending...'}</b></td>
                    <td class="feedback-buttons">
                        <button 
                            class="valid" 
                            disabled={updatingId === alert.id || alert.feedback}
                            on:click={() => handleFeedback(alert.id, 'valid')}>
                            {#if updatingId === alert.id}Saving...{:else}Valid 👍{/if}
                        </button>
                        <button 
                            class="false-alarm" 
                            disabled={updatingId === alert.id || alert.feedback}
                            on:click={() => handleFeedback(alert.id, 'false_alarm')}>
                            {#if updatingId === alert.id}Saving...{:else}False Alarm 👎{/if}
                        </button>
                    </td>
                </tr>
            {/each}
        </tbody>
    </table>
{/if}

<style>
   table { border-collapse: collapse; width: 100%; margin-top: 20px; font-size: 14px; }
    th, td { padding: 12px 15px; border-bottom: 1px solid #ddd; text-align: left; }
    thead tr { background-color: #f7f7f7; font-weight: bold; }
    .feedback-buttons button { margin: 0 5px; padding: 5px 10px; border-radius: 5px; cursor: pointer; border: 1px solid #ccc; font-size: 12px; transition: background-color 0.2s; }
    .feedback-buttons .valid { background-color: #d4edda; border-color: #c3e6cb;}
    .feedback-buttons .false-alarm { background-color: #f8d7da; border-color: #f5c6cb;}
    button:disabled { cursor: not-allowed; opacity: 0.6; }

    tr.warning {
        background-color: #fff3cd; 
    }
    tr.danger {
        background-color: #f8d7da; 
    }
    :global(tr.warning) {
        background-color: #fff3cd !important; 
    }
    :global(tr.danger) {
        background-color: #f8d7da !important; 
    }
</style>