/**
 * logger.js
 * Espeja console.log/warn/error a un archivo diario en logs/, ademas
 * de seguir mostrandolo en consola (para no perder el QR ni la
 * visibilidad en vivo). Retiene 7 dias.
 */

'use strict';

const fs = require('fs');
const path = require('path');

const LOGS_DIR = path.join(__dirname, '..', 'logs');
const RETENCION_DIAS = 7;

function _rutaLogHoy() {
    const fecha = new Date().toISOString().slice(0, 10);
    return path.join(LOGS_DIR, `wpp_service_${fecha}.log`);
}

function _limpiarLogsViejos() {
    const limiteMs = RETENCION_DIAS * 24 * 60 * 60 * 1000;
    const ahora = Date.now();
    for (const archivo of fs.readdirSync(LOGS_DIR)) {
        if (!archivo.startsWith('wpp_service_')) continue;
        const ruta = path.join(LOGS_DIR, archivo);
        try {
            if (ahora - fs.statSync(ruta).mtimeMs > limiteMs) fs.unlinkSync(ruta);
        } catch (e) {
            // archivo ya removido por otro proceso, ignorar
        }
    }
}

function _aArchivo(nivel, args) {
    const linea = `[${new Date().toISOString()}] [${nivel}] ${args.map(String).join(' ')}\n`;
    fs.appendFileSync(_rutaLogHoy(), linea);
}

function activarLogPersistente() {
    fs.mkdirSync(LOGS_DIR, { recursive: true });
    _limpiarLogsViejos();

    const _log = console.log.bind(console);
    const _error = console.error.bind(console);
    const _warn = console.warn.bind(console);

    console.log = (...args) => { _log(...args); _aArchivo('INFO', args); };
    console.error = (...args) => { _error(...args); _aArchivo('ERROR', args); };
    console.warn = (...args) => { _warn(...args); _aArchivo('WARN', args); };
}

module.exports = { activarLogPersistente };
