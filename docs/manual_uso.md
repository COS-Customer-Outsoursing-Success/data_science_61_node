# Manual de uso — Proceso PDC (envío WhatsApp + cargue a servidor)

> Guía operativa: cómo ejecutar cada script del día a día. Para arquitectura, riesgos y qué se corrigió, ver [`ARQUITECTURA_WHATSAPP.md`](./ARQUITECTURA_WHATSAPP.md).

## 1. Qué hace este proceso

Refresca un Excel de indicadores (Corte X Hora, Ausentismo, etc.), captura pantallazos de rangos específicos y los envía por WhatsApp a un grupo — para 4 campañas (Colas, Colsubsidio, Colsubsidio Atracción, TrueBlue). Aparte, 2 scripts independientes cargan bases de Excel (IA Clarita y SMS Fidelización) a las tablas del servidor `.61`.

## 2. Requisitos previos (una sola vez por máquina)

| # | Qué | Cómo |
|---|---|---|
| 1 | Python + entorno virtual | `venv\Scripts\python.exe` ya debe existir en la raíz del proyecto, con `pip install -r requirements.txt` aplicado |
| 2 | Node.js | Versión fijada en `.nvmrc` (24.12.0). Luego `npm install` en la raíz |
| 3 | Archivos `.env` (no van en git, hay que crearlos a mano) | `src/conexiones_db/.env` (`DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`) · `src/conexiones_db/.env.trueblue` (mismas 4 claves, servidor de TrueBlue) · `whatsapp_service/.env` (`WPP_API_TOKEN`, cualquier cadena secreta que tú definas) |
| 4 | Acceso a la unidad de red `Z:\WORKFORCE\...` | Los Excel de cada campaña viven ahí; sin acceso, la campaña falla al abrir el libro |
| 5 | Excel con licencia instalado en la máquina | La actualización de datos y captura de imágenes se hace vía COM (Excel real, no una librería) |
| 6 | Carpetas del proyecto | Si es una máquina nueva, correr `create_folders.bat` una vez para crear `data/`, `logs/`, etc. |

## 3. Envío de reportes por WhatsApp

### 3.1 Cómo se ejecuta cada campaña

Cada campaña tiene su propio `.bat` en la raíz del proyecto — doble clic o programarlo en el Task Scheduler de Windows:

| Campaña | `.bat` | Config en `config_pdc.json` | Grupo de WhatsApp destino |
|---|---|---|---|
| Colsubsidio | `01_PDC_COLSUBSIDIO.bat` | `config_pdc_colsubsidio` | "Colsubsidio Empresas - Data Science" |
| Colsubsidio Atracción | `01_PDC_COLSUBSIDIO_ATRACCION.bat` | `config_pdc_colsubsidio_atraccion` | "Colsubsidio Empresas - Data Science" |
| TrueBlue Pet | `01_PDC_TRUEBLUEPET.bat` | `config_pdc_trueblue` | 2 grupos por JID directo |
| Colas / WhatsApp | `01_PDC_COLAS_WHAT.bat` | `config_pdc_what_colas` | 1 grupo por JID directo |

Solo puede correr **una campaña a la vez** usando WhatsApp — si otra sigue en curso, la nueva espera hasta 10 minutos y luego aborta con el mensaje `Otra campaña sigue usando el servicio WhatsApp`. En operación normal (corridas de ~90 segundos) esto no debería pasar.

### 3.2 Qué hace internamente (en orden)

1. Evalúa si la campaña "cumple ventana" (la última llamada registrada en BD está reciente); si no, reintenta cada 2 minutos hasta 5 veces.
2. Descarga el detalle de agente desde Vicidial (si la campaña lo usa).
3. Abre el Excel de la campaña, ejecuta los stored procedures configurados y refresca conexiones/tablas dinámicas.
   - Si el libro está siendo usado por otra persona/máquina, lo abre en **solo lectura** automáticamente (no se pierde el envío, pero tampoco se guardan cambios en ese archivo).
4. Captura como imagen cada rango configurado y el texto del caption asociado.
5. Levanta el microservicio de WhatsApp (`whatsapp_service/index.js`) y envía cada imagen al grupo configurado, con 3 reintentos.
6. Cierra el servicio de WhatsApp y libera el candado para la siguiente campaña.

Si ninguna de las 5 evaluaciones cumple ventana, se envía una alerta de texto al grupo **"Mediciones Data strategies Latam"** avisando que la tabla de marcaciones no se actualiza.

### 3.3 Primera vez / reconexión de WhatsApp (código QR)

La sesión de WhatsApp se guarda en `whatsapp_service/perfil_bot/`. Si nunca se ha vinculado, o si la sesión se invalidó (cierre de sesión desde el celular, límite de dispositivos), al ejecutar cualquier `.bat` va a aparecer un **código QR en la consola**. Hay que escanearlo con la app de WhatsApp del número asignado al bot, en menos de 5 minutos (la corrida aborta después de 300 segundos sin conexión).

> Importante: esto requiere que alguien vea la consola en el momento. Si el `.bat` corre desatendido por Task Scheduler y la sesión se cae, la corrida simplemente fallará sin que nadie lo note salvo revisando logs (ver 3.4).

Para identificar el nombre exacto o el JID de un grupo nuevo antes de agregarlo al config:
```
npm run wpp
```
(déjalo corriendo con la sesión ya vinculada) y en otra consola:
```
node whatsapp_service/listar_chats.js
```

### 3.4 Dónde revisar si algo falla

| Log | Contenido |
|---|---|
| `logs/{campana}_YYYY-MM-DD.log` | Todo el stdout/stderr de esa corrida (colas, colsubsidio, colsubsidio_atraccion, trueblue) |
| `logs/wpp_service_YYYY-MM-DD.log` | Todo lo que hace el microservicio Node: conexión, envíos, errores de Baileys |

Ambos se retienen 7 días y se limpian solos. Buscar la palabra `Error` es el punto de partida más rápido.

## 4. Cargue de bases al servidor `.61`

Estos 2 scripts **no tienen `.bat`** — se ejecutan manualmente desde consola cuando hay un archivo nuevo que cargar. No dependen del servicio de WhatsApp.

| Script | Carpeta de origen | Pestaña esperada del Excel | Tabla destino |
|---|---|---|---|
| `main_load_IA_Clarita_fidelizacion.py` | `data/Bases_IA/Nuevo/` | `IA` | `bbdd_cos_bog_claro_fidelizacion.tb_ia_clarita_fidelizacion_ds` |
| `main_load_mensajeria_fidelizacion.py` | `data/Bases_SMS/Nuevo/` | `SMS` | `bbdd_cos_bog_claro_fidelizacion.tb_sms_fidelizacion_ds` |

**Pasos:**
1. Copiar el/los `.xlsx` a la carpeta `Nuevo/` correspondiente (puede haber más de uno, se procesan todos juntos).
2. Ejecutar:
   ```
   venv\Scripts\python.exe src\main_load_IA_Clarita_fidelizacion.py
   ```
   o el de mensajería, según corresponda.
3. El script compara contra lo ya existente en la tabla (llave `fecha_envio + cuenta + servicio`), inserta solo lo nuevo, y mueve automáticamente los archivos procesados a `Cargado/`.

Es seguro volver a correrlo sobre el mismo archivo por error: los registros ya cargados se detectan y no se duplican.

## 5. Problemas comunes

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| Aparece un QR en consola y la corrida no avanza | Sesión de WhatsApp vencida | Escanear el QR con el celular del bot antes de que pasen 5 minutos |
| `Otra campaña sigue usando el servicio WhatsApp` | Dos campañas se programaron muy cerca en el tiempo | Esperar a que termine la otra (normalmente ~90s); si persiste, revisar si quedó un proceso Node colgado |
| `No se pudo abrir en modo escritura... Reintentando en solo lectura` | Alguien tiene el Excel de la campaña abierto | Es informativo, no un error: el envío sale igual, solo no se guardan cambios en ese archivo. Si se necesita que sí guarde, pedir que cierren el libro |
| Falta una imagen en el envío de WhatsApp | Falló la captura de ese rango tras 5 intentos | Revisar `logs/{campana}_*.log` buscando el nombre de la hoja; suele ser una hoja/rango mal escrito en `config_pdc.json` o datos que no cargaron a tiempo |
| `Faltan variables de conexión` al conectar a MySQL | Falta o está incompleto el `.env` correspondiente | Revisar `src/conexiones_db/.env` (o `.env.trueblue`) |
| El script de cargue dice `No se encontraron archivos .xlsx` | No hay nada en `Nuevo/` | Confirmar que el archivo se copió a la carpeta correcta antes de ejecutar |

## 6. Más detalle

Para el diagrama de flujo completo, el detalle de cada componente y el historial de riesgos identificados/corregidos, ver [`ARQUITECTURA_WHATSAPP.md`](./ARQUITECTURA_WHATSAPP.md).
