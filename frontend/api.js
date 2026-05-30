const API_BASE = '';

async function apiFetch(endpoint, options = {}) {
    const userJson = localStorage.getItem('mediLogUser');
    const headers = { ...options.headers };

    // Don't set Content-Type if we're sending FormData (browser handles it)
    if (!(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
    }

    if (userJson) {
        const user = JSON.parse(userJson);
        if (user.token) {
            headers['Authorization'] = `Token ${user.token}`;
        }
    }

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(errorText || `HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (err) {
        console.error('API Error:', err);
        throw err;
    }
}

async function login(username, password) {
    return apiFetch('/auth/login/', {
        method: 'POST',
        body: JSON.stringify({ username, password })
    });
}

async function register(data) {
    return apiFetch('/auth/register/', {
        method: 'POST',
        body: JSON.stringify(data)
    });
}

async function getReservations(role, userId) {
    return apiFetch(`/reservations/?role=${role}&userId=${userId}`);
}

async function createReservation(data) {
    const isFormData = data instanceof FormData;
    return apiFetch('/reservations/', {
        method: 'POST',
        body: isFormData ? data : JSON.stringify(data)
    });
}

async function updateStatus(id, status, metadata = {}) {
    // metadata can include { prescription, events, pin, location }
    return apiFetch(`/reservations/${id}/status/`, {
        method: 'PUT',
        body: JSON.stringify({ status, ...metadata })
    });
}

async function getTraceability(id) {
    // This will return the mission events history
    return apiFetch(`/reservations/${id}/traceability/`);
}

async function getReferenceData() {
    return apiFetch('/users/reference/');
}

// Upload is slightly different due to FormData
async function uploadResult(id, file) {
    const formData = new FormData();
    formData.append('resultFile', file);

    try {
        const response = await fetch(`${API_BASE}/files/upload/${id}`, {
            method: 'POST',
            body: formData
        });
        return await response.json();
    } catch (err) {
        console.error('Upload Error:', err);
        throw err;
    }
}

async function getOrdonnances(patientId) {
    return apiFetch(`/patient/${patientId}/ordonnances/`);
}

async function getAnalyses(patientId) {
    return apiFetch(`/patient/${patientId}/analyses/`);
}

async function createOrdonnance(data) {
    return apiFetch('/ordonnance/', {
        method: 'POST',
        body: JSON.stringify(data)
    });
}

// --- Admin Panel API ---
async function getAdminStats() {
    return apiFetch('/users/admin/stats/');
}

async function getAdminUsers(role = '') {
    return apiFetch(`/users/admin/users/?role=${role}`);
}

async function getAdminActivity() {
    return apiFetch('/users/admin/activity/');
}

async function deleteUser(id) {
    return apiFetch(`/users/admin/users/${id}/`, { method: 'DELETE' });
}

async function updateUserAdmin(id, data) {
    return apiFetch(`/users/admin/users/${id}/`, {
        method: 'PUT',
        body: JSON.stringify(data)
    });
}

async function updateReservationStatusAdmin(id, status) {
    return apiFetch(`/reservations/${id}/status`, {
        method: 'PUT',
        body: JSON.stringify({ status })
    });
}
