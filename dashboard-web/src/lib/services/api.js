// src/lib/services/api.js

const BASE_URL = 'http://127.0.0.1:8000';

/**
 * Mengambil data histori sensor dari backend
 * @param {string} sensorId
 * @returns {Promise<any>}
 */
export async function getHistory(sensorId) {
    const response = await fetch(`${BASE_URL}/sensors/${sensorId}/history`);
    if (!response.ok) {
        throw new Error('Gagal mengambil data histori sensor');
    }
    return await response.json();
}

/**
 * Mengambil data riwayat peringatan dari backend
 * @returns {Promise<any[]>}
 */
export async function getAlerts() {
    const response = await fetch(`${BASE_URL}/alerts`);
    if (!response.ok) {
        throw new Error('Gagal memuat data peringatan');
    }
    return await response.json();
}

/**
 * Mengirim umpan balik petugas ke backend
 * @param {string} alertId
 * @param {string} feedback - "valid" atau "false_alarm"
 * @returns {Promise<any>}
 */
export async function submitFeedback(alertId, feedback) {
    const response = await fetch(`${BASE_URL}/alerts/${alertId}/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ feedback: feedback })
    });
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Gagal mengirim umpan balik');
    }
    return await response.json();
}

/**
 * Mengirim notifikasi manual dari petugas
 * @param {string} message
 * @returns {Promise<any>}
 */
export async function sendManualAlert(message) {
    const response = await fetch(`${BASE_URL}/notifications/manual`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message })
    });
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Gagal mengirim peringatan manual');
    }
    return await response.json();
}

/**
 * Mengambil status terbaru dari backend.
 * @returns {Promise<any>}
 */
export async function getLatestStatus() {
    const response = await fetch(`${BASE_URL}/status/latest`);
    if (!response.ok) {
        throw new Error('Gagal mengambil status terbaru');
    }
    return await response.json();
}