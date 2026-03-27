/**
 * listar_chats.js
 * Lista todos los chats disponibles para identificar el nombre exacto del grupo
 * Ejecutar: node whatsapp_service/listar_chats.js
 */

const http = require('http');

const opciones = {
    hostname: 'localhost',
    port: 3000,
    path: '/list-chats',
    method: 'GET'
};

const req = http.request(opciones, (res) => {
    let respuesta = '';
    res.on('data', (chunk) => respuesta += chunk);
    res.on('end', () => {
        const chats = JSON.parse(respuesta);
        console.log('\n=== CHATS DISPONIBLES ===');
        chats.forEach(c => {
            console.log(`[${c.tipo}] "${c.nombre}"`);
        });
    });
});

req.on('error', (e) => console.error('Error:', e.message));
req.end();
