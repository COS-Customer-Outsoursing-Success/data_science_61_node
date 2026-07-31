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

const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '.env') });

require('./logger').activarLogPersistente();

const express = require('express');
const { iniciarCliente, enviarImagen, enviarTexto, getEstado } = require('./wpp_client');

const app = express();
app.use(express.json());

const PUERTO = 3000;
const HOST = '127.0.0.1';

// ─── Autenticacion ────────────────────────────────────────────────────────────
// Exige un token compartido en el header x-api-token para todas las rutas.
// Sin esto, cualquier proceso local podria enviar mensajes/imagenes sin control.
const API_TOKEN = process.env.WPP_API_TOKEN;
if (!API_TOKEN) {
    console.error('[SERVER] Falta WPP_API_TOKEN en whatsapp_service/.env. El servicio no puede iniciar sin token.');
    process.exit(1);
}

app.use((req, res, next) => {
    if (req.headers['x-api-token'] !== API_TOKEN) {
        return res.status(401).json({ error: 'Token invalido o ausente' });
    }
    next();
});

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
        const errorMsg = err instanceof Error ? err.message : JSON.stringify(err) || String(err);
        console.log('[ERROR /send-image] Full error:', JSON.stringify(err), String(err), '| Msg:', errorMsg);
        res.status(500).json({ ok: false, error: errorMsg });
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

app.listen(PUERTO, HOST, () => {
    console.log(`[SERVER] Servicio WhatsApp escuchando en http://${HOST}:${PUERTO}`);
    console.log('[SERVER] Esperando que el cliente WhatsApp se conecte...');
});
