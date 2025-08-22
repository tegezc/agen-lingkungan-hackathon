<script>
    import { sendManualAlert } from '$lib/services/api.js';

    let message = '';
    let isLoading = false;
    let statusMessage = '';

    async function handleSubmit() {
        if (!message) {
            statusMessage = 'Pesan tidak boleh kosong!';
            return;
        }

        isLoading = true;
        statusMessage = 'Mengirim...';

        try {
            const result = await sendManualAlert(message);
            statusMessage = `Pesan berhasil dikirim ke ${result.sent_to} perangkat.`;
            message = ''; // Kosongkan textarea setelah berhasil
        } catch (e) {
            statusMessage = `Error: ${e.message}`;
        } finally {
            isLoading = false;
        }
    }
</script>

<div class="manual-alert">
    <h3>Kirim Peringatan Manual</h3>
    <textarea bind:value={message} placeholder="Ketik pesan peringatan di sini..." disabled={isLoading}></textarea>
    <button on:click={handleSubmit} disabled={isLoading}>
        {#if isLoading}
            Mengirim...
        {:else}
            Kirim ke Semua Pengguna
        {/if}
    </button>
    {#if statusMessage}
        <p class="status">{statusMessage}</p>
    {/if}
</div>

<style>
    .manual-alert {
        margin-top: 30px;
        padding-top: 20px;
        border-top: 1px solid #eee;
    }
    textarea {
        width: 100%;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #ccc;
        margin-bottom: 10px;
        min-height: 80px;
        box-sizing: border-box; /* Important for width 100% */
    }
    button {
        padding: 10px 15px;
        border: none;
        background-color: #007bff;
        color: white;
        border-radius: 5px;
        cursor: pointer;
        width: 100%;
        font-weight: bold;
    }
    button:disabled {
        background-color: #a0cffc;
        cursor: not-allowed;
    }
    .status {
        margin-top: 10px;
        font-size: 14px;
        color: #555;
    }
</style>