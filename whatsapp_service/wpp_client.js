/**
 * wpp_client.js
 * Maneja la conexion con WhatsApp Web via whatsapp-web.js
 * La sesion se guarda en .wwebjs_auth/ para no escanear QR cada vez
 */

const { Client, LocalAuth, MessageMedia } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const path = require('path');
const fs = require('fs');

// Estado del cliente
let clienteReady = false;
let client = null;

function iniciarCliente() {
    client = new Client({
        authStrategy: new LocalAuth({
            // Guarda la sesion en esta carpeta del proyecto
            dataPath: path.join(__dirname, '..', '.wwebjs_auth')
        }),
        puppeteer: {
            headless: true,         // Sin ventana visible
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--log-level=3'
            ]
        }
    });

    // Evento: muestra el QR en consola la PRIMERA vez (o si vence la sesion)
    client.on('qr', (qr) => {
        console.log('\n[WPP] Escanea este QR con tu WhatsApp:');
        qrcode.generate(qr, { small: true });
    });

    // Evento: cliente listo para enviar mensajes
    client.on('ready', () => {
        clienteReady = true;
        console.log('[WPP] Cliente WhatsApp listo.');
    });

    // Evento: sesion autenticada (no necesita QR de nuevo)
    client.on('authenticated', () => {
        console.log('[WPP] Sesion autenticada correctamente.');
    });

    // Evento: fallo de autenticacion (QR vencio o sesion invalida)
    client.on('auth_failure', (msg) => {
        clienteReady = false;
        console.error('[WPP] Error de autenticacion:', msg);
    });

    // Evento: cliente desconectado
    client.on('disconnected', (reason) => {
        clienteReady = false;
        console.warn('[WPP] Cliente desconectado:', reason);
    });

    client.initialize();
}

/**
 * Busca el chat ID de un grupo por su nombre exacto
 * @param {string} nombreGrupo - Nombre del grupo en WhatsApp
 * @returns {string|null} - Chat ID o null si no se encontro
 */
async function buscarGrupo(nombreGrupo) {
    const chats = await client.getChats();
    const grupo = chats.find(c => c.name === nombreGrupo);
    if (!grupo) {
        console.error(`[WPP] Grupo no encontrado: "${nombreGrupo}"`);
        return null;
    }
    return grupo.id._serialized;
}

/**
 * Envia una imagen con caption a un grupo de WhatsApp
 * @param {string} nombreGrupo - Nombre exacto del grupo
 * @param {string} rutaImagen  - Ruta absoluta al archivo .jpg
 * @param {string} caption     - Texto que acompana la imagen
 */
async function enviarImagen(nombreGrupo, rutaImagen, caption) {
    if (!clienteReady) throw new Error('Cliente WhatsApp no esta listo');

    const chatId = await buscarGrupo(nombreGrupo);
    if (!chatId) throw new Error(`Grupo no encontrado: ${nombreGrupo}`);

    if (!fs.existsSync(rutaImagen)) throw new Error(`Imagen no encontrada: ${rutaImagen}`);

    const media = MessageMedia.fromFilePath(rutaImagen);
    await client.sendMessage(chatId, media, { caption });
    console.log(`[WPP] Imagen enviada a "${nombreGrupo}"`);
}

/**
 * Envia solo texto a un grupo de WhatsApp
 * @param {string} nombreGrupo - Nombre exacto del grupo
 * @param {string} mensaje     - Texto a enviar
 */
async function enviarTexto(nombreGrupo, mensaje) {
    if (!clienteReady) throw new Error('Cliente WhatsApp no esta listo');

    const chatId = await buscarGrupo(nombreGrupo);
    if (!chatId) throw new Error(`Grupo no encontrado: ${nombreGrupo}`);

    await client.sendMessage(chatId, mensaje);
    console.log(`[WPP] Texto enviado a "${nombreGrupo}"`);
}

async function getChats() {
    if (!clienteReady) throw new Error('Cliente WhatsApp no esta listo');
    const chats = await client.getChats();
    return chats.map(c => ({
        nombre: c.name,
        tipo: c.isGroup ? 'grupo' : 'contacto'
    }));
}

module.exports = {
    iniciarCliente,
    enviarImagen,
    enviarTexto,
    getChats,
    getEstado: () => ({ listo: clienteReady })
};
