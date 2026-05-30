const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const multer = require('multer');

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

// Data paths
const dbPath = path.join(__dirname, '../database/db.json');
const reservationsPath = path.join(__dirname, '../database/reservations.json');

// File upload config
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        const uploadDir = path.join(__dirname, 'uploads');
        if (!fs.existsSync(uploadDir)) {
            fs.mkdirSync(uploadDir);
        }
        cb(null, uploadDir);
    },
    filename: (req, file, cb) => {
        cb(null, `resultat_${req.params.id}_${Date.now()}.pdf`);
    }
});
const upload = multer({ storage });

// Helper to read/write JSON files
const readJson = (file) => JSON.parse(fs.readFileSync(file, 'utf-8'));
const writeJson = (file, data) => fs.writeFileSync(file, JSON.stringify(data, null, 2));

// ---- ROUTES ----

// Auth
app.post('/auth/login', (req, res) => {
    const { username, password } = req.body;
    const db = readJson(dbPath);
    const user = db.users.find(u => u.username === username && u.password === password);
    if (user) {
        // Simple mock token (in real world: JWT)
        res.json({ success: true, user: { id: user.id, username: user.username, role: user.role, name: user.name } });
    } else {
        res.status(401).json({ success: false, message: 'Identifiants incorrects' });
    }
});

// Reference Data
app.get('/users/reference', (req, res) => {
    const db = readJson(dbPath);
    res.json({ doctors: db.doctors, services: db.services });
});

// Reservations
app.get('/reservations', (req, res) => {
    const { role, userId } = req.query;
    let reservations = readJson(reservationsPath);

    if (role === 'patient') {
        reservations = reservations.filter(r => r.patientId == userId);
    } else if (role === 'medecin') {
        reservations = reservations.filter(r => r.medecinId == userId);
    } else if (role === 'livreur') {
        // Coursier voit celles en attente ou en cours
        reservations = reservations.filter(r => r.status === 'attente' || r.status === 'cours');
    }

    // Sort by latest
    reservations.reverse();
    res.json(reservations);
});

app.post('/reservations', (req, res) => {
    const newReq = req.body;
    const reservations = readJson(reservationsPath);

    newReq.id = Math.floor(Math.random() * 10000);
    newReq.createdAt = new Date().toISOString();
    newReq.status = 'attente';

    reservations.push(newReq);
    writeJson(reservationsPath, reservations);

    res.json({ success: true, reservation: newReq });
});

app.put('/reservations/:id/status', (req, res) => {
    const { id } = req.params;
    const { status } = req.body;
    const reservations = readJson(reservationsPath);

    const index = reservations.findIndex(r => r.id == id);
    if (index !== -1) {
        reservations[index].status = status;
        writeJson(reservationsPath, reservations);
        res.json({ success: true, reservation: reservations[index] });
    } else {
        res.status(404).json({ success: false, message: 'Non trouvé' });
    }
});

// Files
app.post('/files/upload/:id', upload.single('resultFile'), (req, res) => {
    const { id } = req.params;
    if (!req.file) return res.status(400).json({ success: false, message: 'Aucun fichier' });

    // Update reservation status to "resultat" and add file URL
    const reservations = readJson(reservationsPath);
    const index = reservations.findIndex(r => r.id == id);
    if (index !== -1) {
        reservations[index].status = 'resultat';
        reservations[index].fileUrl = `/uploads/${req.file.filename}`;
        writeJson(reservationsPath, reservations);
        res.json({ success: true, fileUrl: reservations[index].fileUrl });
    } else {
        res.status(404).json({ success: false, message: 'Réservation introuvable' });
    }
});

app.listen(PORT, () => {
    console.log(`Backend server running on http://localhost:${PORT}`);
});
