/**
 * index.js
 * Servidor HTTP (Express) que expone endpoints para enviar mensajes por WhatsApp
 * Python llama a este servidor con requests.post()
 *
 * Endpoints:
 *   GET  /status        -> estado de conexion del cliente WhatsApp
 *   POST /send-image    -> envia imagen + caption a un grupo
 *   POST /send-text     -> envia texto a un grupo
 */

const express = require('express');
const { iniciarCliente, enviarImagen, enviarTexto, getEstado } = require('./wpp_client');

const app = express();
app.use(express.json());

const PUERTO = 3000;

// ─── GET /status ─────────────────────────────────────────────────────────────
// Permite verificar si el cliente WhatsApp esta listo antes de enviar
app.get('/status', (req, res) => {
    res.json(getEstado());
});

// ─── GET /list-chats ──────────────────────────────────────────────────────────
// Lista todos los chats para identificar nombres exactos de grupos
app.get('/list-chats', async (req, res) => {
    try {
        const { getChats } = require('./wpp_client');
        const chats = await getChats();
        res.json(chats);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// ─── POST /send-image ─────────────────────────────────────────────────────────
// Body esperado: { "group": "Nombre del grupo", "image_path": "C:\\ruta\\img.jpg", "caption": "texto" }
app.post('/send-image', async (req, res) => {
    const { group, image_path, caption } = req.body;

    if (!group || !image_path) {
        return res.status(400).json({ error: 'Se requieren: group, image_path' });
    }

    try {
        await enviarImagen(group, image_path, caption || '');
        res.json({ ok: true, message: `Imagen enviada a "${group}"` });
    } catch (err) {
        console.error('[ERROR /send-image] Full error:', err);
        res.status(500).json({ ok: false, error: err.message || String(err) });
    }
});

// ─── POST /send-text ──────────────────────────────────────────────────────────
// Body esperado: { "group": "Nombre del grupo", "message": "texto a enviar" }
app.post('/send-text', async (req, res) => {
    const { group, message } = req.body;

    if (!group || !message) {
        return res.status(400).json({ error: 'Se requieren: group, message' });
    }

    try {
        await enviarTexto(group, message);
        res.json({ ok: true, message: `Texto enviado a "${group}"` });
    } catch (err) {
        console.error('[ERROR /send-text]', err.message);
        res.status(500).json({ ok: false, error: err.message });
    }
});

// ─── Inicio ───────────────────────────────────────────────────────────────────
iniciarCliente();

app.listen(PUERTO, () => {
    console.log(`[SERVER] Servicio WhatsApp escuchando en http://localhost:${PUERTO}`);
    console.log('[SERVER] Esperando que el cliente WhatsApp se conecte...');
});
