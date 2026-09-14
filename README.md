# Bot de Auto Compra para Amazon v2.1

Un bot automatizado creado en Python con Selenium para monitorear el stock de un producto en Amazon y comprarlo automáticamente en cuanto esté disponible. Incluye múltiples estrategias de compra y notificaciones por Discord.

## Características

- **Monitoreo continuo de stock** — Refresca la página del producto cada 5 segundos hasta detectar disponibilidad.
- **Compra directa con "Comprar ahora"** — Detecta y hace clic en el botón de compra inmediata en cuanto aparece.
- **Búsqueda de opciones alternativas** — Si el botón principal no está disponible, busca automáticamente en "Otras opciones de compra" y vendedores alternativos.
- **Confirmación automática del pedido** — Navega por el checkout y confirma el pedido con reintentos inteligentes (hasta 3 intentos con espera progresiva).
- **Flujo completo carrito → checkout** — Si compra desde un vendedor alternativo, agrega al carrito, procede al checkout y confirma automáticamente.
- **Notificaciones por Discord** — Opción de ingresar la URL de un Webhook de Discord para recibir alertas en tiempo real (inicio, detección de stock, compra exitosa o errores).
- **Ventana de instrucciones** — Al iniciar muestra un diálogo visual con los pasos a seguir.
- **Compatibilidad con Amazon en español e inglés** — Los selectores soportan ambos idiomas.

## Cómo Usarlo

### Opción 1: Usar el ejecutable (Recomendado para usuarios sin Python)

Descarga el archivo `AmazonAutoCompra.exe` y haz doble clic en él.

1. Al abrirlo, verás una ventana con las instrucciones.
2. Pega el enlace del artículo de Amazon en la consola y presiona ENTER.
3. (Opcional) Pega la URL de tu Webhook de Discord o presiona ENTER para omitir.
4. Se abrirá Google Chrome. **Inicia sesión en tu cuenta de Amazon** ahí mismo.
5. Resuelve cualquier CAPTCHA que aparezca.
6. Asegúrate de tener configurados tu **método de pago** y **dirección de envío** predeterminados.
7. Vuelve a la consola y presiona ENTER para iniciar el monitoreo.

El bot comenzará a refrescar la página y comprará el producto automáticamente en cuanto detecte disponibilidad.

### Opción 2: Desde el código fuente

Si eres desarrollador y quieres ejecutar o modificar el código:

1. Asegúrate de tener **Python 3.8+** y **Google Chrome** instalados.
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Ejecuta el script:
   ```bash
   python bot.py
   ```

## Requisitos

- Google Chrome instalado en el sistema.
- Conexión a internet estable.
- Cuenta de Amazon con método de pago y dirección configurados.

## Dependencias

- `selenium` — Automatización del navegador.
- `webdriver-manager` — Gestión automática del driver de Chrome.

## Estrategias de Compra

El bot utiliza un sistema de múltiples estrategias para maximizar las probabilidades de completar la compra:

1. **Botón "Comprar ahora"** — Primera prioridad. Busca el botón directo de compra inmediata.
2. **Otras opciones de compra** — Si el botón principal no está, busca vendedores alternativos en el panel de ofertas.
3. **Checkout desde carrito** — Si compra desde ofertas alternativas, completa el flujo a través del carrito de compras.

Cada estrategia incluye múltiples selectores CSS y XPath para adaptarse a las variaciones de la interfaz de Amazon.

## Advertencia

El uso de herramientas de automatización en plataformas de comercio electrónico puede ir en contra de sus términos de servicio. Úsalo bajo tu propia responsabilidad.
