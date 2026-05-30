// Common functionality for dashboards
const userJson = localStorage.getItem('mediLogUser');
const path = window.location.pathname;

// Redirect to login if not logged in
if (!userJson && !path.endsWith('index.html') && !path.endsWith('/')) {
    window.location.href = 'index.html';
}

// Export currentUser for other scripts synchronously
let currentUser = null;
if (userJson) {
    try {
        currentUser = JSON.parse(userJson);
    } catch(e) {
        localStorage.removeItem('mediLogUser');
        window.location.href = 'index.html';
    }
}
window.currentUser = currentUser;

document.addEventListener('DOMContentLoaded', () => {
    // Setup navbar user info
    const userInfoEl = document.getElementById('navbar-user-info');
    if (userInfoEl && window.currentUser) {
        userInfoEl.innerHTML = `
            <span class="badge badge-role">${window.currentUser.role.toUpperCase()}</span>
            <span><b>${window.currentUser.name}</b></span>
            <button id="logoutBtn" class="btn btn-outline" style="padding: 0.5rem 1rem;">Déconnexion</button>
        `;
        
        document.getElementById('logoutBtn').addEventListener('click', () => {
            localStorage.removeItem('mediLogUser');
            window.location.href = 'index.html';
        });
    }
});

// Format dates nicely
function formatDate(dateStr) {
    const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(dateStr).toLocaleDateString('fr-FR', options);
}

function getStatusBadge(status) {
    const statusMap = {
        'attente': { class: 'status-attente', text: 'En attente', icon: 'fa-clock' },
        'cours': { class: 'status-cours', text: 'En cours de livraison', icon: 'fa-motorcycle' },
        'livre': { class: 'status-livre', text: 'Livré au médecin', icon: 'fa-check-circle' },
        'resultat': { class: 'status-resultat', text: 'Résultat disponible', icon: 'fa-file-pdf' }
    };
    const s = statusMap[status] || statusMap['attente'];
    return `<span class="badge ${s.class}"><i class="fa-solid ${s.icon}"></i> ${s.text}</span>`;
}

function renderTracker(status) {
    const steps = ['attente', 'cours', 'livre', 'resultat'];
    const currentIndex = steps.indexOf(status);
    let html = '<div class="tracker">';
    const labels = ['En attente', 'En transit', 'Livré', 'Terminé'];
    const icons = ['fa-clipboard-list', 'fa-truck', 'fa-box-open', 'fa-file-medical'];

    steps.forEach((step, index) => {
        let stepClass = '';
        if (index < currentIndex) stepClass = 'completed';
        if (index === currentIndex) stepClass = 'active';

        let iconHtml = index < currentIndex ? '<i class="fa-solid fa-check"></i>' : `<i class="fa-solid ${icons[index]}"></i>`;
        html += `
            <div class="tracker-step ${stepClass}">
                <div class="step-icon">${iconHtml}</div>
                <div class="step-label">${labels[index]}</div>
            </div>
        `;
    });
    html += '</div>';
    return html;
}
