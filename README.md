# Bot de Auto Compra para Amazon

Un bot automatizado creado en Python con Selenium para monitorear el stock de un producto en Amazon y comprarlo automáticamente en cuanto esté disponible.

## Cómo Usarlo

### Opción 1: Usar el ejecutable (Recomendado para usuarios sin Python)
Si solo quieres usar la herramienta, descarga el archivo `bot.exe` y haz doble clic en él.

1. Al abrirlo, verás las instrucciones en pantalla.
2. Pega el enlace del artículo de Amazon en la consola negra y presiona ENTER.
3. Se abrirá Google Chrome. Inicia sesión en tu cuenta de Amazon ahí mismo.
4. Vuelve a la consola negra y presiona ENTER para iniciar el monitoreo.

### Opción 2: Desde el código fuente
Si eres desarrollador y quieres ejecutar o modificar el código:

1. Asegúrate de tener Python y Google Chrome instalados.
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Ejecuta el script:
   ```bash
   python bot.py
   ```

## Advertencia
El uso de herramientas de automatización en plataformas de comercio electrónico puede ir en contra de sus términos de servicio. Úsalo bajo tu propia responsabilidad.
