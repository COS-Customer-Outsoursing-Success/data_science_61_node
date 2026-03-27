/**
 * test_envio.js
 * Script de prueba para verificar el envio de imagen via el servicio HTTP
 * Ejecutar: node whatsapp_service/test_envio.js
 */

const http = require('http');

const datos = JSON.stringify({
    group: "Notas",
    image_path: "C:\\01_github\\data_science_61_node\\data\\img\\pdc\\Colsubsidio Atraccion\\Corte_X_Hora.jpg",
    caption: "Test envio desde Node.js"
});

const opciones = {
    hostname: 'localhost',
    port: 3000,
    path: '/send-image',
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(datos)
    }
};

const req = http.request(opciones, (res) => {
    let respuesta = '';
    res.on('data', (chunk) => respuesta += chunk);
    res.on('end', () => {
        console.log('Respuesta del servidor:', respuesta);
    });
});

req.on('error', (e) => {
    console.error('Error:', e.message);
});

req.write(datos);
req.end();
