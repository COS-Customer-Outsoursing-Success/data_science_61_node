/**
 * wpp_client.js
 * Cliente WhatsApp usando Baileys (WebSocket directo, sin Puppeteer/Chrome).
 * Sesion persistida en perfil_bot/. Se auto-elimina si hay corrupcion o cierre de sesion.
 *
 * Exports: iniciarCliente, enviarImagen, enviarTexto, getChats, getEstado
 */

'use strict';

const qrcode   = require('qrcode-terminal');
const path     = require('path');
const fs       = require('fs');

// ─── Rutas ────────────────────────────────────────────────────────────────────
const PERFIL_BOT = path.join(__dirname, 'perfil_bot');
const CACHE_FILE = path.join(PERFIL_BOT, 'chat_cache.json');

// ─── Estado global ────────────────────────────────────────────────────────────
let clienteReady = false;
let sock         = null;
let chatCache    = {};   // { "nombre grupo": "XXXX@g.us" }

// ─── Cache en disco ───────────────────────────────────────────────────────────
function cargarCacheDesdeArchivo() {
    try {
        if (fs.existsSync(CACHE_FILE)) {
            chatCache = JSON.parse(fs.readFileSync(CACHE_FILE, 'utf8'));
            console.log(`[WPP] Cache cargado desde disco: ${Object.keys(chatCache).length} grupos.`);
        }
    } catch (e) {
        console.warn('[WPP] No se pudo leer cache de disco:', e.message);
    }
}

function guardarCacheEnArchivo() {
    try {
        fs.mkdirSync(path.dirname(CACHE_FILE), { recursive: true });
        fs.writeFileSync(CACHE_FILE, JSON.stringify(chatCache, null, 2), 'utf8');
    } catch (e) {
        console.warn('[WPP] No se pudo guardar cache en disco:', e.message);
    }
}

// ─── Gestion de sesion ────────────────────────────────────────────────────────
function eliminarSesion() {
    try {
        if (fs.existsSync(PERFIL_BOT)) {
            // Preservar solo el cache de grupos (no credenciales)
            const cacheTemp = { ...chatCache };
            fs.rmSync(PERFIL_BOT, { recursive: true, force: true });
            chatCache = cacheTemp;
            console.log('[WPP] Sesion eliminada. Se solicitara nuevo QR al reconectar.');
        }
    } catch (e) {
        console.warn('[WPP] No se pudo eliminar sesion:', e.message);
    }
}

// ─── Carga de grupos ──────────────────────────────────────────────────────────
async function cargarGrupos() {
    try {
        const grupos = await sock.groupFetchAllParticipating();
        const nuevos = {};
        Object.values(grupos).forEach(g => {
            if (g.subject && g.id) nuevos[g.subject] = g.id;
        });
        chatCache = { ...chatCache, ...nuevos };
        guardarCacheEnArchivo();
        console.log(`[WPP] Grupos sincronizados: ${Object.keys(nuevos).length} grupos cargados.`);
    } catch (err) {
        console.warn('[WPP] No se pudieron cargar grupos:', String(err));
    }
}

// ─── Inicializacion principal (async, usa import() para ESM de Baileys) ───────
async function _iniciar() {
    const {
        default: makeWASocket,
        useMultiFileAuthState,
        DisconnectReason,
        fetchLatestWaWebVersion,
        makeCacheableSignalKeyStore,
        Browsers
    } = await import('@whiskeysockets/baileys');

    const pino = (await import('pino')).default;

    fs.mkdirSync(PERFIL_BOT, { recursive: true });

    const { state, saveCreds } = await useMultiFileAuthState(PERFIL_BOT);
    const { version }          = await fetchLatestWaWebVersion();
    const logger               = pino({ level: 'silent' });

    console.log(`[WPP] Iniciando con Baileys v${version.join('.')}`);

    sock = makeWASocket({
        version,
        auth: {
            creds: state.creds,
            keys:  makeCacheableSignalKeyStore(state.keys, logger)
        },
        logger,
        printQRInTerminal: false,
        browser: Browsers.ubuntu('PDC Bot'),
        syncFullHistory: false,
    });

    // Persistir credenciales al actualizarse
    sock.ev.on('creds.update', saveCreds);

    // Evento principal de conexion
    sock.ev.on('connection.update', async ({ connection, lastDisconnect, qr }) => {

        // Mostrar QR cuando lo pida WA
        if (qr) {
            console.log('\n[WPP] Escanea este QR con tu WhatsApp:');
            qrcode.generate(qr, { small: true });
        }

        if (connection === 'open') {
            console.log('[WPP] Sesion autenticada y conectada.');
            await cargarGrupos();
            clienteReady = true;
            console.log('[WPP] Cliente WhatsApp listo.');
        }

        if (connection === 'close') {
            clienteReady = false;
            const statusCode = lastDisconnect?.error?.output?.statusCode;
            console.warn(`[WPP] Conexion cerrada. Codigo: ${statusCode}`);

            // Codigos que indican sesion invalida o corrupta -> borrar y re-QR
            const SESION_INVALIDA = [
                DisconnectReason.loggedOut,        // 401 — usuario cerro sesion
                DisconnectReason.badSession,       // 500 — archivos corruptos
                DisconnectReason.connectionReplaced, // 440 — otra instancia conectada
            ];

            if (SESION_INVALIDA.includes(statusCode)) {
                console.warn('[WPP] Sesion invalida o corrupta detectada. Eliminando perfil_bot...');
                eliminarSesion();
            } else {
                console.log('[WPP] Reconectando en 4s...');
            }

            setTimeout(() => _iniciar().catch(e => console.error('[WPP] Error al reconectar:', e.message)), 4000);
        }
    });
}

// ─── API publica ──────────────────────────────────────────────────────────────

function iniciarCliente() {
    cargarCacheDesdeArchivo();
    _iniciar().catch(err => console.error('[WPP] Error fatal al iniciar:', err.message));
}

async function buscarGrupo(grupoRef) {
    // Si ya es un JID directo (viene del config como "XXXX@g.us"), usarlo sin buscar
    if (grupoRef.includes('@')) {
        console.log(`[WPP] JID directo desde config: ${grupoRef}`);
        return grupoRef;
    }
    // Busqueda por nombre: cache en memoria
    if (chatCache[grupoRef]) {
        console.log(`[WPP] JID desde cache: "${grupoRef}"`);
        return chatCache[grupoRef];
    }
    // Refrescar desde WA
    console.log(`[WPP] "${grupoRef}" no en cache. Sincronizando grupos...`);
    await cargarGrupos();
    if (chatCache[grupoRef]) return chatCache[grupoRef];

    console.error(`[WPP] Grupo no encontrado: "${grupoRef}"`);
    return null;
}

async function enviarImagen(nombreGrupo, rutaImagen, caption) {
    console.log(`[WPP] [1] Verificando cliente listo: ${clienteReady}`);
    if (!clienteReady) throw new Error('Cliente WhatsApp no esta listo');

    console.log(`[WPP] [2] Buscando grupo: "${nombreGrupo}"`);
    const jid = await buscarGrupo(nombreGrupo);
    if (!jid) throw new Error(`Grupo no encontrado: ${nombreGrupo}`);
    console.log(`[WPP] [3] JID encontrado: ${jid}`);

    if (!fs.existsSync(rutaImagen)) throw new Error(`Imagen no encontrada: ${rutaImagen}`);
    console.log(`[WPP] [4] Enviando imagen...`);

    await sock.sendMessage(jid, {
        image:   fs.readFileSync(rutaImagen),
        caption: caption || ''
    });
    console.log(`[WPP] Imagen enviada a "${nombreGrupo}"`);
}

async function enviarTexto(nombreGrupo, mensaje) {
    if (!clienteReady) throw new Error('Cliente WhatsApp no esta listo');

    const jid = await buscarGrupo(nombreGrupo);
    if (!jid) throw new Error(`Grupo no encontrado: ${nombreGrupo}`);

    await sock.sendMessage(jid, { text: mensaje });
    console.log(`[WPP] Texto enviado a "${nombreGrupo}"`);
}

async function getChats() {
    if (!clienteReady) throw new Error('Cliente WhatsApp no esta listo');
    const grupos = await sock.groupFetchAllParticipating();
    return Object.values(grupos).map(g => ({
        nombre: g.subject,
        tipo:   'grupo'
    }));
}

module.exports = {
    iniciarCliente,
    enviarImagen,
    enviarTexto,
    getChats,
    getEstado: () => ({ listo: clienteReady })
};
