# Bot de Auto Compra para Amazon Ultra-Fast v3.0

Un bot automatizado de alta velocidad creado en Python con Selenium para monitorear el stock de un producto en Amazon y comprarlo automáticamente en cuanto esté disponible. Diseñado para competir eficazmente en **drops de alta demanda y compras ultrarrápidas**.

## Novedades en v3.0 (Ultra-Fast Edition)

- ⚡ **Motor de Compra Sub-Milisegundo (JS Execution)**: Inyección directa de JavaScript nativo en Chromium para detectar y hacer clic en el botón *"Comprar ahora"* en **< 1ms**, superando los métodos estándar de simulación de ratón de Selenium.
- 🏎️ **Modo Turbo Speed & Estrategia Eager Loading**:
  - `page_load_strategy = 'eager'`: Retorna el control en cuanto el DOMHTML básico carga (<200ms) sin esperar imágenes ni rastreadores pesados.
  - Bloqueo inteligente de imágenes y assets pesados opcional.
  - Refresco en tiempo real en sub-segundos (0.5s configurable).
- 🌍 **Soporte Multi-Región de Amazon**: Selección de dominios internacionales integrados:
  - Amazon USA / Global (`amazon.com`)
  - Amazon España (`amazon.es`)
  - Amazon México (`amazon.com.mx`)
  - Amazon Reino Unido (`amazon.co.uk`)
  - Amazon Alemania (`amazon.de`)
  - Amazon Italia (`amazon.it`)
  - Amazon Francia (`amazon.fr`)
  - Amazon Canadá (`amazon.ca`)
  - Amazon Japón (`amazon.co.jp`)
  - Dominio personalizado editable.
- 🔐 **Gestión de Login en Headless / Consola (CLI & GUI)**:
  - En servidores sin interfaz gráfica (Headless), el bot permite iniciar sesión interactivamente mediante la consola (prompts para correo, contraseña y código 2FA/OTP), o mediante una ventana temporal con GUI.
- 🌐 **Dashboard Web en Vivo (Puerto 8080)**: Visualización en tiempo real desde cualquier dispositivo del estado del monitoreo, región, contador de chequeos y logs en vivo.
- 📢 **Notificaciones por Discord**: Alertas en tiempo real sobre detección de stock, compras completadas y reportes de estado.

## Cómo Usarlo

### Opción 1: Usar el ejecutable (Recomendado)

Descarga el archivo `AmazonAutoCompra.exe` y haz doble clic en él.

1. **Selecciona la Región de Amazon**: Elige entre 1 y 10.
2. **Selecciona el Modo Servidor Headless**: `S` para modo sin ventana gráfica o `N` para modo normal.
3. **Selecciona el Modo Turbo Speed**: `S` para habilitar refresco ultrarrápido sub-segundo (<1s).
4. **Ingresa el Enlace del Producto o ASIN**: Pega la URL del producto o su código ASIN (ej: `B08N5WRWNW`).
5. **(Opcional) Webhook de Discord**: Pega tu URL de Webhook para recibir notificaciones.
6. **Autenticación**: El bot verificará tu sesión. Si no estás logueado en modo Headless, podrás ingresar tus datos o abrir una ventana de login.
7. ¡El monitoreo comenzará automáticamente a máxima velocidad! Abre `http://localhost:8080` para ver el Dashboard.

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

## Panel de Estado Web (Dashboard)

- **URL Local**: `http://localhost:8080`
- **URL Servidor Remoto**: `http://<IP_DE_TU_SERVIDOR>:8080`
- **API Status JSON**: `http://localhost:8080/api/status`

## Requisitos

- Google Chrome instalado en el sistema.
- Conexión a internet estable.
- Cuenta de Amazon con método de pago y dirección de envío predeterminadas.

## Advertencia

El uso de herramientas de automatización en plataformas de comercio electrónico puede ir en contra de sus términos de servicio. Úsalo bajo tu propia responsabilidad.
