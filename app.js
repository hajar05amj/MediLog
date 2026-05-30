// Mock Data Initialization
const initialData = {
    users: [
        { id: 1, username: 'patient', password: '123', role: 'patient', name: 'M. Ahmed (Patient)' },
        { id: 2, username: 'medecin', password: '123', role: 'medecin', name: 'Dr. Bennani (Médecin)' },
        { id: 3, username: 'livreur', password: '123', role: 'livreur', name: 'Karim (Coursier)' }
    ],
    services: [
        { id: 'transport_analyse', name: 'Transport des analyses médicales' },
        { id: 'reception_resultat', name: 'Réception des résultats à domicile' },
        { id: 'accompagnement', name: 'Accompagnement physique chez le médecin' }
    ],
    doctors: [
        { id: 2, name: 'Dr. Bennani - Cardiologue' },
        { id: 101, name: 'Dr. Tazi - Généraliste' },
        { id: 102, name: 'Dr. Chraibi - Laboratoire Central' }
    ],
    requests: [
        {
            id: 1001,
            patientId: 1,
            medecinId: 2,
            medecinName: 'Dr. Bennani - Cardiologue',
            service: 'transport_analyse',
            serviceName: 'Transport des analyses médicales',
            date: '2026-05-10',
            time: '10:00',
            address: 'Quartier Hassan, Rabat',
            status: 'attente', // attente, cours, livre, resultat
            createdAt: new Date().toISOString()
        }
    ]
};

// Initialize LocalStorage if empty
if (!localStorage.getItem('mediLogData')) {
    localStorage.setItem('mediLogData', JSON.stringify({
        requests: initialData.requests
    }));
}

// State
let currentUser = JSON.parse(localStorage.getItem('mediLogUser')) || null;
let currentView = currentUser ? `${currentUser.role}_dashboard` : 'login';

// Helpers
function getData() {
    return JSON.parse(localStorage.getItem('mediLogData'));
}

function saveData(data) {
    localStorage.setItem('mediLogData', JSON.stringify(data));
}

function generateId() {
    return Math.floor(Math.random() * 10000);
}

function formatDate(dateStr) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateStr).toLocaleDateString('fr-FR', options);
}

// Main Render Function
function render() {
    const appEl = document.getElementById('app');
    appEl.innerHTML = '';

    if (!currentUser) {
        appEl.innerHTML = renderLogin();
        bindLoginEvents();
        return;
    }

    // Render Navbar
    appEl.innerHTML += `
        <nav class="navbar animate-fade-in">
            <div class="nav-brand">
                <i class="fa-solid fa-truck-medical"></i> MediLog
            </div>
            <div class="user-info">
                <span class="badge badge-role">${currentUser.role.toUpperCase()}</span>
                <span><b>${currentUser.name}</b></span>
                <button id="logoutBtn" class="btn btn-outline" style="padding: 0.5rem 1rem;">Déconnexion</button>
            </div>
        </nav>
    `;

    // Render Views
    const content = document.createElement('div');
    content.className = 'animate-fade-in';
    content.style.flexGrow = '1';

    if (currentView === 'patient_dashboard') {
        content.innerHTML = renderPatientDashboard();
        appEl.appendChild(content);
        bindPatientEvents();
    } else if (currentView === 'new_request') {
        content.innerHTML = renderNewRequest();
        appEl.appendChild(content);
        bindNewRequestEvents();
    } else if (currentView === 'medecin_dashboard') {
        content.innerHTML = renderMedecinDashboard();
        appEl.appendChild(content);
        bindMedecinEvents();
    } else if (currentView === 'livreur_dashboard') {
        content.innerHTML = renderLivreurDashboard();
        appEl.appendChild(content);
        bindLivreurEvents();
    }

    // Bind Logout
    document.getElementById('logoutBtn').addEventListener('click', () => {
        currentUser = null;
        currentView = 'login';
        localStorage.removeItem('mediLogUser');
        render();
    });
}

// ---------------- VIEWS ----------------

function renderLogin() {
    return `
        <div class="login-container animate-fade-in card">
            <div class="login-logo">
                <i class="fa-solid fa-heart-pulse"></i>
            </div>
            <h1>Bienvenue sur MediLog</h1>
            <p>Plateforme e-logistique médicale</p>
            
            <form id="loginForm" style="margin-top: 2rem; text-align: left;">
                <div class="form-group">
                    <label>Nom d'utilisateur</label>
                    <input type="text" id="username" required placeholder="Ex: patient, medecin, livreur">
                </div>
                <div class="form-group">
                    <label>Mot de passe</label>
                    <input type="password" id="password" required placeholder="Ex: 123">
                </div>
                <button type="submit" class="btn btn-primary btn-large" style="width: 100%;">Se connecter</button>
            </form>

            <div class="login-demo-info">
                <strong>Comptes de démonstration (mdp: 123) :</strong>
                <ul style="margin-top:0.5rem; margin-left: 1.5rem;">
                    <li><b>patient</b> : Espace Patient</li>
                    <li><b>medecin</b> : Espace Médecin</li>
                    <li><b>livreur</b> : Espace Coursier</li>
                </ul>
            </div>
        </div>
    `;
}

function getStatusBadge(status) {
    const statusMap = {
        'attente': { class: 'status-attente', text: 'En attente', icon: 'fa-clock' },
        'cours': { class: 'status-cours', text: 'En cours de livraison', icon: 'fa-motorcycle' },
        'livre': { class: 'status-livre', text: 'Livré au médecin', icon: 'fa-check-circle' },
        'resultat': { class: 'status-resultat', text: 'Résultat disponible', icon: 'fa-file-pdf' }
    };
    const s = statusMap[status];
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

function renderPatientDashboard() {
    const data = getData();
    const myRequests = data.requests.filter(r => r.patientId === currentUser.id).reverse();

    let requestsHtml = '';
    if (myRequests.length === 0) {
        requestsHtml = '<p>Aucune demande pour le moment.</p>';
    } else {
        requestsHtml = myRequests.map(r => `
            <div class="request-item">
                <div class="request-header">
                    <div>
                        <div class="request-title">Demande #${r.id}</div>
                        <div class="request-date">${formatDate(r.createdAt)}</div>
                    </div>
                    ${getStatusBadge(r.status)}
                </div>
                <div class="request-details">
                    <p><i class="fa-solid fa-briefcase-medical"></i> <b>Service :</b> ${r.serviceName}</p>
                    <p><i class="fa-solid fa-user-doctor"></i> <b>Destinataire :</b> ${r.medecinName}</p>
                    <p><i class="fa-regular fa-calendar"></i> <b>Rendez-vous :</b> ${formatDate(r.date)} à ${r.time}</p>
                    <p><i class="fa-solid fa-location-dot"></i> <b>Adresse :</b> ${r.address}</p>
                </div>
                ${renderTracker(r.status)}
                ${r.status === 'resultat' ? `
                    <div style="margin-top: 1rem; text-align: center;">
                        <button class="btn btn-primary" onclick="alert('Téléchargement du PDF en cours...')">
                            <i class="fa-solid fa-download"></i> Télécharger le résultat (PDF)
                        </button>
                    </div>
                ` : ''}
            </div>
        `).join('');
    }

    return `
        <div class="dashboard-grid">
            <div>
                <div class="card">
                    <h2>Que souhaitez-vous faire ?</h2>
                    <p>Réservez un nouveau service de transport ou d'accompagnement.</p>
                    <button id="btnNewRequest" class="btn btn-primary btn-large" style="margin-top: 1rem;">
                        <i class="fa-solid fa-plus-circle"></i> Nouvelle Demande
                    </button>
                </div>
                <img src="https://images.unsplash.com/photo-1579684385127-1ef15d508118?auto=format&fit=crop&w=500&q=80" 
                     alt="Medical logistics" 
                     style="width: 100%; border-radius: 16px; object-fit: cover; height: 200px; box-shadow: var(--box-shadow);">
            </div>
            <div>
                <h2>Mes demandes récentes</h2>
                ${requestsHtml}
            </div>
        </div>
    `;
}

function renderNewRequest() {
    const servicesOptions = initialData.services.map(s => `<option value="${s.id}">${s.name}</option>`).join('');
    const doctorsOptions = initialData.doctors.map(d => `<option value="${d.id}">${d.name}</option>`).join('');

    return `
        <div class="card" style="max-width: 800px; margin: 0 auto;">
            <button id="btnBack" class="btn btn-outline" style="margin-bottom: 2rem; padding: 0.5rem 1rem;">
                <i class="fa-solid fa-arrow-left"></i> Retour
            </button>
            
            <h2>Réserver un service</h2>
            <form id="newRequestForm" style="margin-top: 2rem;">
                <div class="form-group">
                    <label>Type de service</label>
                    <select id="serviceType" required>
                        <option value="">-- Sélectionnez un service --</option>
                        ${servicesOptions}
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Médecin / Laboratoire de destination</label>
                    <select id="doctorSelect" required>
                        <option value="">-- Sélectionnez un médecin --</option>
                        ${doctorsOptions}
                    </select>
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                    <div class="form-group">
                        <label>Date de récupération</label>
                        <input type="date" id="reqDate" required>
                    </div>
                    <div class="form-group">
                        <label>Heure</label>
                        <input type="time" id="reqTime" required>
                    </div>
                </div>

                <div class="form-group">
                    <label>Adresse complète (Domicile)</label>
                    <textarea id="reqAddress" rows="3" required placeholder="Saisissez votre adresse complète..."></textarea>
                </div>

                <button type="submit" class="btn btn-primary btn-large">
                    <i class="fa-solid fa-check"></i> Confirmer la réservation
                </button>
            </form>
        </div>
    `;
}

function renderMedecinDashboard() {
    const data = getData();
    const myRequests = data.requests.filter(r => r.medecinId === currentUser.id && (r.status === 'livre' || r.status === 'resultat')).reverse();

    let requestsHtml = '';
    if (myRequests.length === 0) {
        requestsHtml = '<p>Aucune analyse reçue ou en attente de résultat.</p>';
    } else {
        requestsHtml = myRequests.map(r => `
            <div class="request-item">
                <div class="request-header">
                    <div>
                        <div class="request-title">Analyse #${r.id} - Patient ID: ${r.patientId}</div>
                        <div class="request-date">Reçu le ${formatDate(r.createdAt)}</div>
                    </div>
                    ${getStatusBadge(r.status)}
                </div>
                
                ${r.status === 'livre' ? `
                    <div class="request-actions">
                        <div class="file-upload-wrapper btn btn-success" style="padding: 1rem 1.5rem; text-align:center; flex-grow: 1;">
                            <i class="fa-solid fa-upload"></i> Envoyer le résultat (PDF)
                            <input type="file" accept=".pdf" onchange="window.appUploadResult(${r.id})" />
                        </div>
                    </div>
                    <p style="font-size: 0.8rem; color: var(--text-light); text-align: center; margin-top: 0.5rem;">
                        Cliquez pour sélectionner un fichier PDF de votre ordinateur
                    </p>
                ` : `
                    <div style="margin-top: 1rem; color: var(--accent-color); font-weight: 500;">
                        <i class="fa-solid fa-check-circle"></i> Résultat transmis au patient avec succès.
                    </div>
                `}
            </div>
        `).join('');
    }

    return `
        <div class="dashboard-grid">
            <div style="grid-column: 1 / -1;">
                <div class="card">
                    <h2>Espace Praticien - Gestion des résultats</h2>
                    <p>Téléchargez les résultats d'analyses pour les patients ayant utilisé le service de transport.</p>
                </div>
            </div>
            <div style="grid-column: 1 / -1;">
                ${requestsHtml}
            </div>
        </div>
    `;
}

function renderLivreurDashboard() {
    const data = getData();
    // Livreur voit toutes les demandes en attente ou en cours
    const activeRequests = data.requests.filter(r => r.status === 'attente' || r.status === 'cours').reverse();

    let requestsHtml = '';
    if (activeRequests.length === 0) {
        requestsHtml = '<p>Aucune course disponible.</p>';
    } else {
        requestsHtml = activeRequests.map(r => `
            <div class="request-item">
                <div class="request-header">
                    <div>
                        <div class="request-title">Course #${r.id}</div>
                        <div class="request-date">${r.serviceName}</div>
                    </div>
                    ${getStatusBadge(r.status)}
                </div>
                <div class="request-details">
                    <p><i class="fa-solid fa-location-dot"></i> <b>Départ :</b> ${r.address}</p>
                    <p><i class="fa-solid fa-flag-checkered"></i> <b>Destination :</b> ${r.medecinName}</p>
                    <p><i class="fa-regular fa-calendar"></i> <b>Pour le :</b> ${formatDate(r.date)} à ${r.time}</p>
                </div>
                
                <div class="request-actions">
                    ${r.status === 'attente' ? `
                        <button class="btn btn-primary" onclick="window.appUpdateStatus(${r.id}, 'cours')" style="flex-grow: 1;">
                            <i class="fa-solid fa-motorcycle"></i> Accepter et Démarrer
                        </button>
                    ` : ''}
                    
                    ${r.status === 'cours' ? `
                        <button class="btn btn-success" onclick="window.appUpdateStatus(${r.id}, 'livre')" style="flex-grow: 1;">
                            <i class="fa-solid fa-check-double"></i> Confirmer la Livraison
                        </button>
                    ` : ''}
                </div>
            </div>
        `).join('');
    }

    return `
        <div class="dashboard-grid">
            <div style="grid-column: 1 / -1;">
                <div class="card">
                    <h2>Espace Coursier Médical</h2>
                    <p>Consultez les courses disponibles et mettez à jour leur statut en temps réel.</p>
                </div>
            </div>
            <div style="grid-column: 1 / -1; display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 1.5rem;">
                ${requestsHtml}
            </div>
        </div>
    `;
}

// ---------------- EVENTS ----------------

function bindLoginEvents() {
    document.getElementById('loginForm').addEventListener('submit', (e) => {
        e.preventDefault();
        const u = document.getElementById('username').value.trim();
        const p = document.getElementById('password').value.trim();

        const user = initialData.users.find(x => x.username === u && x.password === p);
        if (user) {
            currentUser = user;
            currentView = `${user.role}_dashboard`;
            localStorage.setItem('mediLogUser', JSON.stringify(user));
            render();
        } else {
            alert('Identifiants incorrects. Essayez patient/123, medecin/123 ou livreur/123');
        }
    });
}

function bindPatientEvents() {
    document.getElementById('btnNewRequest').addEventListener('click', () => {
        currentView = 'new_request';
        render();
    });
}

function bindNewRequestEvents() {
    document.getElementById('btnBack').addEventListener('click', () => {
        currentView = 'patient_dashboard';
        render();
    });

    document.getElementById('newRequestForm').addEventListener('submit', (e) => {
        e.preventDefault();

        const serviceSelect = document.getElementById('serviceType');
        const docSelect = document.getElementById('doctorSelect');

        const newReq = {
            id: generateId(),
            patientId: currentUser.id,
            medecinId: parseInt(docSelect.value),
            medecinName: docSelect.options[docSelect.selectedIndex].text,
            service: serviceSelect.value,
            serviceName: serviceSelect.options[serviceSelect.selectedIndex].text,
            date: document.getElementById('reqDate').value,
            time: document.getElementById('reqTime').value,
            address: document.getElementById('reqAddress').value,
            status: 'attente',
            createdAt: new Date().toISOString()
        };

        const data = getData();
        data.requests.push(newReq);
        saveData(data);

        alert('Demande enregistrée avec succès !');
        currentView = 'patient_dashboard';
        render();
    });
}

function bindMedecinEvents() {
    // Handled by inline onclick handlers
}

function bindLivreurEvents() {
    // Handled by inline onclick handlers
}

// Global functions for inline handlers
window.appUpdateStatus = function (reqId, newStatus) {
    const data = getData();
    const req = data.requests.find(r => r.id === reqId);
    if (req) {
        req.status = newStatus;
        saveData(data);
        render();
    }
};

window.appUploadResult = function (reqId) {
    setTimeout(() => {
        window.appUpdateStatus(reqId, 'resultat');
        alert('Résultat (PDF) envoyé avec succès ! Le patient a été notifié.');
    }, 500); // Simulate upload time
};

// Initial Render
render();
