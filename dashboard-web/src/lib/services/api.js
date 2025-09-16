// src/lib/services/api.js

const BASE_URL = 'https://floodcast-service-669250331086.asia-southeast2.run.app';

/**
 * Fetches sensor history data from the backend
 * @param {string} sensorId
 * @returns {Promise<any>}
 */
export async function getHistory(sensorId) {
    const response = await fetch(`${BASE_URL}/sensors/${sensorId}/history`);
    if (!response.ok) {
        throw new Error('Failed to fetch sensor history data');
    }
    return await response.json();
}

/**
 * Fetches alert history data from the backend
 * @returns {Promise<any[]>}
 */
export async function getAlerts() {
    const response = await fetch(`${BASE_URL}/alerts/alerts`);
    if (!response.ok) {
        throw new Error('Failed to load alert data');
    }
    return await response.json();
}

/**
 * Submits officer feedback to the backend
 * @param {string} alertId
 * @param {string} feedback - "valid" or "false_alarm"
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
        throw new Error(errorData.detail || 'Failed to submit feedback');
    }
    return await response.json();
}

/**
 * Sends a manual notification from an officer
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
        throw new Error(errorData.detail || 'Failed to send manual alert');
    }
    return await response.json();
}

/**
 * Fetches the latest status from the backend.
 * @returns {Promise<any>}
 */
export async function getLatestStatus() {
    const response = await fetch(`${BASE_URL}/status/latest`);
    if (!response.ok) {
        throw new Error('Failed to fetch the latest status');
    }
    return await response.json();
}