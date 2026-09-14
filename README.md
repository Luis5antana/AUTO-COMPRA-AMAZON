# Bot de Auto Compra para Amazon v2.2

Un bot automatizado creado en Python con Selenium para monitorear el stock de un producto en Amazon y comprarlo automáticamente en cuanto esté disponible. Soporta ejecución con interfaz gráfica y **modo servidor headless (sin pantalla)** con un **Dashboard Web en vivo**.

## Características

- **Modo Servidor Headless** — Opción de ejecutarse en servidores Linux/Windows VPS sin interfaz gráfica o sin abrir la ventana del navegador Chrome (`--headless=new`).
- **Dashboard Web de Estado en Vivo** — Servidor web liviano integrado en el puerto `8080` (ej: `http://localhost:8080` o `http://TU_IP:8080`) que muestra en tiempo real:
  - Estado del proceso (Monitoreando, Comprando, Exitoso, Error).
  - Contador de chequeos realizados.
  - Hora de la última verificación.
  - Registros/Logs de eventos en vivo.
- **Notificaciones por Discord** — Integración nativa con Webhook de Discord para enviar alertas automáticas y reportes periódicos (heartbeats de estado).
- **Persistencia de Sesión de Amazon** — Guarda y reutiliza las cookies y perfil de usuario en `./chrome_profile` para mantener la sesión iniciada incluso entre reinicios del bot o en servidores headless.
- **Monitoreo continuo de stock** — Refresca la página cada 5 segundos hasta detectar disponibilidad.
- **Múltiples estrategias de compra** — "Comprar ahora" directo, "Otras opciones de compra" y checkout automático desde el carrito.
- **Reintentos inteligentes de confirmación** — Reintenta la confirmación del pedido progresivamente si Amazon tarda en procesar.
- **Compatibilidad bilingüe** — Funciona en Amazon en español e inglés.

## Cómo Usarlo

### Opción 1: Usar el ejecutable (Recomendado)

Descarga el archivo `AmazonAutoCompra.exe` y haz doble clic en él.

1. Selecciona el modo de ejecución:
   - **N** (por defecto): Modo normal con ventana de Chrome para iniciar sesión visualmente.
   - **S**: Modo Servidor Headless (sin ventana gráfica).
2. Pega el enlace (URL) del artículo de Amazon y presiona ENTER.
3. (Opcional) Pega la URL de tu Webhook de Discord para notificaciones.
4. Si estás en modo normal, inicia sesión en la ventana de Chrome que se abrirá.
5. Vuelve a la consola y presiona ENTER para comenzar el monitoreo.
6. Abre tu navegador y accede a `http://localhost:8080` para ver el **Dashboard de Estado en Vivo**.

### Opción 2: Desde el código fuente

1. Instala Python 3.8+ y Google Chrome.
2. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Ejecuta el script:
   ```bash
   python bot.py
   ```

## 🔔 ¿Cómo obtener tu Webhook de Discord?

Para recibir notificaciones en tu servidor de Discord:

1. Abre **Discord** e ingresa a tu servidor (o crea uno propio gratis).
2. Haz clic derecho en el canal de texto donde quieres recibir los avisos (ej: `#notificaciones`).
3. Selecciona **Editar Canal** (icono de engranaje ⚙️).
4. Ve a la pestaña **Integraciones** en el menú izquierdo.
5. Haz clic en **Webhooks** ➔ **Crear Webhook** (o *Nuevo Webhook*).
6. Haz clic en **Copiar URL del Webhook**.
7. ¡Pega esa URL en la consola del bot cuando te la pida!

## Panel de Estado Web (Dashboard)

Al iniciar el bot, se levantará automáticamente un servidor web en el puerto `8080`:
- **URL Local**: `http://localhost:8080`
- **URL Servidor Remote**: `http://<IP_DE_TU_SERVIDOR>:8080`
- **API Status JSON**: `http://localhost:8080/api/status`

## Requisitos

- Google Chrome instalado en el sistema.
- Conexión a internet estable.
- Cuenta de Amazon con método de pago y dirección configurados.

## Advertencia

El uso de herramientas de automatización en plataformas de comercio electrónico puede ir en contra de sus términos de servicio. Úsalo bajo tu propia responsabilidad.
