const { 
    default: makeWASocket, 
    useMultiFileAuthState, 
    DisconnectReason,
    fetchLatestBaileysVersion
} = require('@whiskeysockets/baileys');
const qrcode = require('qrcode-terminal');
const pino = require('pino');

async function iniciar() {
    console.log('🔄 Iniciando conexión limpia con WhatsApp (Baileys)...');

    // 1. Gestionar las credenciales en una carpeta local limpia
    const { state, saveCreds } = await useMultiFileAuthState('sesion_baileys');

    // 2. Obtener la última versión compatible de WhatsApp Web para evitar bloqueos
    let version;
    try {
        const latest = await fetchLatestBaileysVersion();
        version = latest.version;
        console.log(`📡 Usando versión de WhatsApp Web: ${version.join('.')}`);
    } catch (e) {
        // Versión de respaldo en caso de fallo de red en la consulta
        version = [2, 3000, 1017578415]; 
    }

    // 3. Inicializar el socket
    const sock = makeWASocket({
        version,
        auth: state,
        printQRInTerminal: false, // Lo manejaremos manualmente en el listener para asegurar que se imprima
        logger: pino({ level: 'silent' }),
        browser: ['Ubuntu', 'Chrome', '20.0.0']
    });

    // Guardar credenciales automáticamente ante cualquier cambio
    sock.ev.on('creds.update', saveCreds);

    // 4. Escuchar el estado de la conexión y capturar el QR
    sock.ev.on('connection.update', async (update) => {
        const { connection, lastDisconnect, qr } = update;

        // Si WhatsApp nos envía un código QR, lo mostramos inmediatamente
        if (qr) {
            console.log('\n================================================================');
            console.log('📱 ESCANEA ESTE CÓDIGO QR CON TU WHATSAPP:');
            console.log('================================================================\n');
            qrcode.generate(qr, { small: true });
        }

        if (connection === 'connecting') {
            console.log('⏳ Estableciendo conexión con el servidor...');
        }

        if (connection === 'close') {
            const razon = lastDisconnect?.error?.output?.statusCode;
            console.log(`\n🔌 Conexión cerrada (Código: ${razon})`);
            
            if (razon !== DisconnectReason.loggedOut) {
                console.log('🔄 Intentando reconectar de inmediato...');
                iniciar();
            } else {
                console.log('🛑 Sesión cerrada en el dispositivo móvil. Elimina la carpeta "sesion_baileys" y reinicia.');
            }
        } 
        
        if (connection === 'open') {
            console.log('\n✅ ¡Conectado con éxito a WhatsApp!');
            console.log('🔍 Cargando chats grupales en memoria (espera un momento)...');
            
            try {
                // Forzar un delay de 3 segundos para asegurar la sincronización inicial de metadatos
                await new Promise(res => setTimeout(res, 3000));

                const chats = await sock.groupFetchAllParticipating();
                const grupoIds = Object.keys(chats);

                if (grupoIds.length === 0) {
                    console.log('⚠️ No se encontraron grupos en tu cuenta.');
                } else {
                    console.log('\n================================================================');
                    console.log('             LISTA DE GRUPOS ENCONTRADOS                        ');
                    console.log('================================================================');
                    
                    grupoIds.forEach(id => {
                        const grupo = chats[id];
                        console.log(`📌 Nombre:  ${grupo.subject}`);
                        console.log(`   ID:      ${grupo.id}`);
                        console.log('----------------------------------------------------------------');
                    });

                    console.log(`\n🎉 Se listaron exitosamente ${grupoIds.length} grupos.`);
                }
            } catch (error) {
                console.error('❌ Error obteniendo grupos:', error);
            } finally {
                console.log('\nProceso completado de manera limpia. Finalizando...');
                process.exit(0);
            }
        }
    });
}

iniciar();