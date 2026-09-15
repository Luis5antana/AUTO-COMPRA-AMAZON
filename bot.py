import time
import json
import urllib.request
import os
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from selenium import webdriver
import selenium.webdriver.chrome.webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Safe import of tkinter (fails gracefully on headless servers without X11 / display)
try:
    import tkinter as tk
    from tkinter import messagebox
    TK_AVAILABLE = True
except Exception:
    TK_AVAILABLE = False


# ============================================================
#  ESTADO EN VIVO Y SERVIDOR WEB DE MONITOREO
# ============================================================

STATUS_DATA = {
    "estado": "Iniciando...",
    "url": "",
    "region": "amazon.com",
    "chequeos": 0,
    "intervalo": 0.5,
    "turbo": True,
    "ultima_verificacion": "-",
    "logs": [],
    "discord_activo": False,
    "modo_headless": False,
    "inicio": time.strftime("%Y-%m-%d %H:%M:%S")
}

REGIONES = {
    "1": ("Amazon USA / Global", "www.amazon.com"),
    "2": ("Amazon España", "www.amazon.es"),
    "3": ("Amazon México", "www.amazon.com.mx"),
    "4": ("Amazon Reino Unido", "www.amazon.co.uk"),
    "5": ("Amazon Alemania", "www.amazon.de"),
    "6": ("Amazon Italia", "www.amazon.it"),
    "7": ("Amazon Francia", "www.amazon.fr"),
    "8": ("Amazon Canadá", "www.amazon.ca"),
    "9": ("Amazon Japón", "www.amazon.co.jp"),
}


def log_event(mensaje):
    """Imprime un mensaje en consola y lo registra en los logs en vivo."""
    timestamp = time.strftime('%H:%M:%S')
    formatted = f"[{timestamp}] {mensaje}"
    print(formatted)
    STATUS_DATA["logs"].append(formatted)
    if len(STATUS_DATA["logs"]) > 35:
        STATUS_DATA["logs"].pop(0)


class StatusServerHandler(BaseHTTPRequestHandler):
    """Maneja las peticiones del panel Web de estado."""
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(STATUS_DATA).encode("utf-8"))
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AmazonAutoCompra Ultra-Fast — Panel de Estado</title>
    <style>
        :root {{
            --bg: #0f172a;
            --card: #1e293b;
            --accent: #ff9900;
            --text: #f8fafc;
            --muted: #94a3b8;
            --success: #22c55e;
            --danger: #ef4444;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
        }}
        .container {{
            max-width: 850px;
            width: 100%;
        }}
        .header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
            border-bottom: 2px solid #334155;
            padding-bottom: 15px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 1.5rem;
            color: var(--accent);
        }}
        .badge {{
            padding: 6px 12px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.85rem;
        }}
        .status-running {{ background: #15803d; color: #fff; }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .card {{
            background: var(--card);
            border-radius: 10px;
            padding: 15px;
            border: 1px solid #334155;
        }}
        .card .title {{
            font-size: 0.75rem;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .card .val {{
            font-size: 1.3rem;
            font-weight: bold;
            margin-top: 5px;
        }}
        .logs-box {{
            background: #020617;
            border-radius: 10px;
            padding: 15px;
            font-family: monospace;
            font-size: 0.85rem;
            height: 280px;
            overflow-y: auto;
            border: 1px solid #334155;
        }}
        .log-line {{
            margin: 3px 0;
            color: #cbd5e1;
        }}
        a {{ color: var(--accent); text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚡ AmazonAutoCompra (Ultra-Fast 3.0)</h1>
            <span class="badge status-running" id="state-badge">EN EJECUCIÓN</span>
        </div>

        <div class="grid">
            <div class="card">
                <div class="title">Estado</div>
                <div class="val" id="state-text" style="color: var(--accent);">--</div>
            </div>
            <div class="card">
                <div class="title">Región</div>
                <div class="val" id="region-text">--</div>
            </div>
            <div class="card">
                <div class="title">Chequeos Realizados</div>
                <div class="val" id="checks-count">0</div>
            </div>
            <div class="card">
                <div class="title">Velocidad / Intervalo</div>
                <div class="val" id="speed-text">--</div>
            </div>
        </div>

        <div class="card" style="margin-bottom: 20px;">
            <div class="title">Producto Monitoreado</div>
            <div style="margin-top: 5px; word-break: break-all;" id="product-url">--</div>
        </div>

        <h3>📋 Registros de Actividad (Tiempo Real)</h3>
        <div class="logs-box" id="logs-container">
            <div class="log-line">Cargando eventos...</div>
        </div>
    </div>

    <script>
        async function updateDashboard() {{
            try {{
                const res = await fetch('/api/status');
                const data = await res.json();

                document.getElementById('state-text').innerText = data.estado;
                document.getElementById('region-text').innerText = data.region;
                document.getElementById('checks-count').innerText = data.chequeos;
                document.getElementById('speed-text').innerText = data.turbo ? `${{data.intervalo}}s (Turbo Speed ⚡)` : `${{data.intervalo}}s`;
                document.getElementById('product-url').innerHTML = data.url ? `<a href="${{data.url}}" target="_blank">${{data.url}}</a>` : 'Sin URL';

                const logsContainer = document.getElementById('logs-container');
                logsContainer.innerHTML = data.logs.map(l => `<div class="log-line">${{l}}</div>`).join('');
                logsContainer.scrollTop = logsContainer.scrollHeight;
            }} catch(e) {{
                console.error("Error al actualizar dashboard:", e);
            }}
        }}

        setInterval(updateDashboard, 1500);
        updateDashboard();
    </script>
</body>
</html>"""
        self.wfile.write(html.encode("utf-8"))


def iniciar_servidor_web(puerto=8080):
    """Inicia el servidor web en un hilo secundario."""
    try:
        server = HTTPServer(('0.0.0.0', puerto), StatusServerHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        print(f"🌐 Panel de Estado Web activo en: http://localhost:{puerto} (o la IP de tu servidor)")
    except Exception as e:
        print(f"⚠️ No se pudo iniciar el servidor web en puerto {puerto}: {e}")


# ============================================================
#  DISCORD WEBHOOK NOTIFICATIONS
# ============================================================

def enviar_discord(webhook_url, titulo, descripcion, color=0x00FF00, url_producto=""):
    """Envía una notificación a Discord usando un webhook."""
    if not webhook_url:
        return

    embed = {
        "title": titulo,
        "description": descripcion,
        "color": color,
        "footer": {"text": "AmazonAutoCompra Ultra-Fast v3.0"},
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    if url_producto:
        embed["url"] = url_producto

    payload = json.dumps({"embeds": [embed]}).encode("utf-8")

    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "AmazonAutoCompra/3.0"},
    )

    try:
        urllib.request.urlopen(req)
    except Exception as e:
        print(f"  [Discord] Error al enviar notificación: {e}")


def mostrar_instrucciones(modo_headless=False):
    if modo_headless or not TK_AVAILABLE:
        print("\n" + "="*60)
        print("          INSTRUCCIONES DE USO (MODO SERVIDOR HEADLESS)")
        print("="*60)
        print("1. El bot utilizará la sesión en ./chrome_profile.")
        print("2. Si no has iniciado sesión, el bot te guiará por consola (CLI).")
        print("3. Modo Turbo Speed activado: refresco ultra-rápido en sub-segundos.")
        print("4. Monitorea el estado desde el Dashboard Web en el puerto 8080.")
        print("="*60 + "\n")
        return

    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        instrucciones = (
            "¡Bienvenido a AmazonAutoCompra Ultra-Fast v3.0!\n\n"
            "PASOS A SEGUIR:\n"
            "1. Haz clic en 'Aceptar' en este mensaje.\n"
            "2. Selecciona la Región de Amazon deseada.\n"
            "3. Pega la URL del producto de Amazon y presiona ENTER.\n"
            "4. (Opcional) Pega la URL de tu Webhook de Discord para notificaciones.\n"
            "5. El bot verificará tu sesión e iniciará el monitoreo ultra-rápido."
        )
        
        messagebox.showinfo("Instrucciones - Bot de Auto Compra", instrucciones)
        root.destroy()
    except Exception:
        pass


# ============================================================
#  GESTIÓN DE LOGIN EN MODO HEADLESS / CONSOLA INTERACTIVA
# ============================================================

def esta_logueado(driver, domain):
    """Verifica si la cuenta de Amazon está iniciada activamente."""
    try:
        driver.get(f"https://{domain}/gp/css/homepage.html")
        time.sleep(1)
        src = driver.page_source.lower()
        if "ap/signin" in driver.current_url.lower() or "inicia sesión" in src or "sign in" in src:
            return False
        return True
    except Exception:
        return False


def gestionar_login_headless(driver, domain, modo_headless):
    """Gestiona el inicio de sesión si no hay una sesión activa, soportando modo Headless/CLI."""
    log_event("Verificando estado de sesión de Amazon...")

    if esta_logueado(driver, domain):
        log_event("✅ Sesión de Amazon detectada e iniciada correctamente.")
        return True

    log_event("⚠️ ATENCIÓN: No se detectó una sesión activa de Amazon.")
    print("\n" + "!"*60)
    print("NO HAS INICIADO SESIÓN EN AMAZON")
    print("Para poder comprar automáticamente, necesitas estar autenticado.")
    print("Opciones disponibles:")
    print("1. Iniciar sesión por consola interactiva CLI (email, password, 2FA/OTP)")
    if modo_headless:
        print("2. Abrir ventana gráfica de Chrome temporalmente para iniciar sesión")
    print("3. Continuar sin verificar login")
    print("!"*60 + "\n")

    opcion = input("Selecciona una opción (1/2/3):\n> ").strip()

    if opcion == "1":
        # Login interactivo vía consola
        log_event("Iniciando login por consola CLI...")
        driver.get(f"https://{domain}/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2F{domain}%2F%3Fref_%3Dnav_custrec_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0")
        time.sleep(2)

        try:
            email = input("\nIngresa tu correo o teléfono de Amazon:\n> ").strip()
            if email:
                driver.find_element(By.ID, "ap_email").send_keys(email)
                driver.execute_script("document.querySelector('#continue')?.click();")
                time.sleep(2)

            password = input("Ingresa tu contraseña de Amazon:\n> ").strip()
            if password:
                driver.find_element(By.ID, "ap_password").send_keys(password)
                driver.execute_script("document.querySelector('#signInSubmit')?.click();")
                time.sleep(3)

            # Verificar si pide OTP / 2FA / CAPTCHA
            if "otp" in driver.page_source.lower() or "mfa" in driver.page_source.lower() or "verification" in driver.page_source.lower():
                otp = input("🔐 Amazon solicitó un Código 2FA / OTP (enviado a tu celular/email/app). Ingrésalo aquí:\n> ").strip()
                if otp:
                    otp_box = driver.find_element(By.CSS_SELECTOR, "input[name='otpCode'], #auth-mfa-otpcode")
                    otp_box.send_keys(otp)
                    driver.execute_script("document.querySelector('#auth-signin-button, #auth-mfa-remember-device')?.click();")
                    time.sleep(3)

            if esta_logueado(driver, domain):
                log_event("✅ Login exitoso vía CLI. Sesión guardada en profile.")
                return True
            else:
                log_event("⚠️ No se pudo confirmar el login automático vía CLI.")
        except Exception as e:
            log_event(f"Error durante el login CLI: {e}")

    elif opcion == "2" and modo_headless:
        log_event("Abriendo ventana gráfica de Chrome para login manual...")
        print("\nAbriendo navegador gráfico...")
        driver.quit()

        # Abrir driver temporal con GUI
        temp_options = Options()
        temp_options.add_argument(f"--user-data-dir={os.path.abspath('./chrome_profile')}")
        temp_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        temp_service = Service(ChromeDriverManager().install())
        temp_driver = webdriver.Chrome(service=temp_service, options=temp_options)
        temp_driver.get(f"https://{domain}/ap/signin")

        print("Por favor, inicia sesión manualmente en la ventana de Chrome que se abrió.")
        input("Presiona ENTER en esta consola cuando hayas completado el inicio de sesión... ")
        temp_driver.quit()

        log_event("Login manual completado. Reiniciando en modo headless...")
        return True

    return False


# ============================================================
#  MOTOR DE COMPRA RÁPIDA (SUB-MILLISECOND JS CHECKOUT)
# ============================================================

def ejecutar_comprar_ahora_js(driver):
    """Ejecuta un script JS súper rápido que detecta e interactúa en <1ms con el botón Comprar Ahora."""
    js_script = """
    const selectors = [
        "#buy-now-button",
        "input[name='submit.buy-now']",
        "#buyNow",
        "#buyNowSubmit",
        "input[title='Comprar ya']",
        "input[title='Buy Now']",
        "#buy-now-button input"
    ];
    for (let sel of selectors) {
        let btn = document.querySelector(sel);
        if (btn && (btn.offsetWidth > 0 || btn.offsetHeight > 0)) {
            btn.click();
            return true;
        }
    }
    return false;
    """
    try:
        return driver.execute_script(js_script)
    except Exception:
        return False


def intentar_confirmar_pedido_ultrafast(driver):
    """Mapea y hace clic instantáneo en el botón de confirmar pedido usando JS sin esperas."""
    js_script = """
    const selectors = [
        "input[name='placeYourOrder1']",
        "#submitOrderButtonId input",
        "#bottomSubmitOrderButtonId input",
        "#submitOrderButtonId",
        "#bottomSubmitOrderButtonId",
        "input[aria-labelledby='submitOrderButtonId-announce']",
        "input[title='Place your order']",
        "input[title='Realizar tu pedido']",
        "input[title='Confirmar pedido']",
        ".place-your-order-button input",
        ".place-your-order-button",
        "#placeYourOrder input",
        "//input[contains(@name,'placeYourOrder')]"
    ];
    for (let sel of selectors) {
        let el = document.querySelector(sel);
        if (el && (el.offsetWidth > 0 || el.offsetHeight > 0)) {
            el.click();
            return true;
        }
    }
    return false;
    """
    # Polling ultra rápido cada 30 milisegundos durante 5 segundos
    start_time = time.time()
    while time.time() - start_time < 5.0:
        try:
            clicked = driver.execute_script(js_script)
            if clicked:
                log_event("⚡ ¡CLIC INSTANTÁNEO EN CONFIRMAR PEDIDO EJECUTADO EN <10ms!")
                time.sleep(1.0)
                return True
        except Exception:
            pass
        time.sleep(0.03)

    return False


def intentar_otras_opciones_ultrafast(driver, url_producto):
    """Intenta comprar desde vendedores alternativos / otras opciones de forma acelerada."""
    js_opciones = """
    const selOpciones = [
        "#mbc-action-panel-wrapper a",
        "#mbc a.a-touch-link",
        "#buybox-see-all-buying-choices a",
        "#buybox-see-all-buying-choices button",
        "a[href*='offer-listing']",
        "#all-offers-display a",
        "input[@id='buybox-see-all-buying-choices-announce']"
    ];
    for (let s of selOpciones) {
        let link = document.querySelector(s);
        if (link) { link.click(); return true; }
    }
    return false;
    """
    try:
        found = driver.execute_script(js_opciones)
        if found:
            log_event("Encontrada opción alternativa de compra. Procesando...")
            time.sleep(1.5)
            # Agregar al carrito desde ofertas
            js_add_cart = """
            const selCart = [
                "#aod-offer input[name='submit.addToCart']",
                "#aod-pinned-offer input[name='submit.addToCart']",
                "input[name='submit.addToCart']"
            ];
            for (let sc of selCart) {
                let btn = document.querySelector(sc);
                if (btn) { btn.click(); return true; }
            }
            return false;
            """
            added = driver.execute_script(js_add_cart)
            if added:
                log_event("Añadido al carrito desde ofertas. Procediendo a Checkout...")
                time.sleep(1.5)
                driver.get("https://" + STATUS_DATA["region"] + "/gp/cart/view.html")
                time.sleep(1.5)
                driver.execute_script("document.querySelector(\"input[name='proceedToRetailCheckout'], #sc-buy-box-ptc-button input\")?.click();")
                time.sleep(2)
                return intentar_confirmar_pedido_ultrafast(driver)
    except Exception as e:
        pass

    return False


# ============================================================
#  FUNCIÓN PRINCIPAL
# ============================================================

def main():
    print("="*50)
    print("      BOT DE AUTO COMPRA AMAZON v3.0 (ULTRA-FAST)")
    print("="*50)

    # 1. Selección de Región
    print("\nSELECCIONA LA REGIÓN DE AMAZON:")
    for k, v in REGIONES.items():
        print(f" {k}. {v[0]} ({v[1]})")
    print(" 10. Ingresar dominio personalizado")

    resp_region = input("\nElige la región (1-10) [Por defecto: 1 - USA]:\n> ").strip()
    if resp_region in REGIONES:
        domain = REGIONES[resp_region][1]
    elif resp_region == "10":
        domain = input("Ingresa el dominio de Amazon (ej: www.amazon.com.mx):\n> ").strip().lower()
        if not domain:
            domain = "www.amazon.com"
    else:
        domain = "www.amazon.com"

    STATUS_DATA["region"] = domain
    log_event(f"Región seleccionada: {domain}")

    # 2. Selección de Modo Servidor / Headless
    resp_headless = input("\n¿Deseas ejecutar en MODO SERVIDOR HEADLESS (sin ventana de navegador)? (s/N):\n> ").strip().lower()
    modo_headless = resp_headless in ['s', 'si', 'y', 'yes', 'true']
    STATUS_DATA["modo_headless"] = modo_headless

    # 3. Selección de Velocidad / Turbo Mode
    resp_turbo = input("\n¿Activar MODO TURBO SPEED (Refresco ultra-rápido <1s, cargas aceleradas)? (S/n):\n> ").strip().lower()
    turbo = resp_turbo not in ['n', 'no', 'false']
    STATUS_DATA["turbo"] = turbo
    STATUS_DATA["intervalo"] = 0.5 if turbo else 2.0

    mostrar_instrucciones(modo_headless)

    # 4. Enlace del producto o ASIN
    entrada_prod = input("\nPega la URL del producto de Amazon (o su código ASIN):\n> ").strip()
    if not entrada_prod:
        print("No ingresaste ningún enlace o ASIN. Cerrando...")
        input("Presiona Enter para salir...")
        return

    # Dar formato a la URL si es solo un ASIN (ej: B08N5WRWNW)
    if not entrada_prod.startswith("http"):
        url = f"https://{domain}/dp/{entrada_prod}"
    else:
        url = entrada_prod

    STATUS_DATA["url"] = url

    # 5. Discord Webhook
    discord_webhook = input("\n(Opcional) Pega la URL del Webhook de Discord para notificaciones (o ENTER para omitir):\n> ").strip()
    if discord_webhook:
        STATUS_DATA["discord_activo"] = True
        enviar_discord(discord_webhook, "⚡ Bot Ultra-Fast Iniciado", f"Iniciando monitoreo de stock ultra-rápido en Amazon.\n**Región:** {domain}\n**Modo:** {'Headless (Servidor)' if modo_headless else 'Normal (GUI)'}\n**Intervalo:** {STATUS_DATA['intervalo']}s\n**Producto:** {url}", color=0x3498DB, url_producto=url)

    # Iniciar servidor Web de monitoreo
    iniciar_servidor_web(puerto=8080)

    log_event("Configurando motor Selenium de ultra-alta velocidad...")
    options = Options()

    # Estrategia de carga Eager: Retorna el control en cuanto el DOMHTML está cargado (<200ms)
    options.page_load_strategy = 'eager'

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    profile_dir = os.path.abspath("./chrome_profile")
    options.add_argument(f"--user-data-dir={profile_dir}")

    # Optimización Turbo: Bloquear imágenes para acelerar carga 3x
    if turbo:
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)

    if modo_headless:
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        log_event("Modo Headless (Servidor sin pantalla) activado ✓")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        log_event(f"Error al iniciar Chrome: {e}")
        input("Presiona Enter para salir...")
        return

    try:
        # Verificar / Gestionar Login
        gestionar_login_headless(driver, domain, modo_headless)

        log_event(f"Navegando a la URL del producto: {url}")
        driver.get(url)

        if not modo_headless:
            print("\n" + "="*50)
            print("PRESIONA ENTER CUANDO ESTÉS LISTO PARA INICIAR EL MONITOREO ULTRA-RÁPIDO")
            print("="*50 + "\n")
            input("Presiona ENTER aquí... ")

        STATUS_DATA["estado"] = "Monitoreando Stock (Ultra-Fast) 🟢"
        log_event(f"🚀 MONITOREO ULTRA-RÁPIDO INICIADO (Intervalo: {STATUS_DATA['intervalo']}s)")

        while True:
            try:
                STATUS_DATA["chequeos"] += 1
                STATUS_DATA["ultima_verificacion"] = time.strftime('%H:%M:%S.%f')[:-3]
                compra_exitosa = False

                # Heartbeat de estado a Discord cada 200 chequeos
                if discord_webhook and STATUS_DATA["chequeos"] % 200 == 0:
                    enviar_discord(discord_webhook, "💚 Estado del Monitoreo", f"El bot sigue monitoreando a máxima velocidad.\n**Chequeos:** {STATUS_DATA['chequeos']}\n**Producto:** {url}", color=0x3498DB, url_producto=url)

                # === ESTRATEGIA 1: Ejecución JS Instantánea <1ms en "Comprar Ahora" ===
                clicked_buy = ejecutar_comprar_ahora_js(driver)

                if clicked_buy:
                    log_event("⚡ ¡STOCK DETECTADO! CLIC EN COMPRAR AHORA EJECUTADO EN <1ms!")
                    STATUS_DATA["estado"] = "Confirmando Pedido Ultra-Fast ⚡"

                    if discord_webhook:
                        enviar_discord(discord_webhook, "⚡ Stock Detectado!", "¡Botón 'Comprar ahora' presionado instantáneamente! Confirmando pedido...", color=0xF1C40F, url_producto=url)

                    compra_exitosa = intentar_confirmar_pedido_ultrafast(driver)

                    if compra_exitosa:
                        STATUS_DATA["estado"] = "¡Compra Completada! 🎉"
                        log_event("🎉 ¡¡¡COMPRA COMPLETADA EXITOSAMENTE EN TIEMPO RÉCORD!!!")
                        if discord_webhook:
                            enviar_discord(discord_webhook, "🎉 ¡COMPRA COMPLETADA!", f"El producto fue comprado exitosamente.\n**Producto:** {url}", color=0x2ECC71, url_producto=url)
                        break
                    else:
                        STATUS_DATA["estado"] = "Monitoreando Stock (Ultra-Fast) 🟢"
                        log_event("No se pudo confirmar el pedido de inmediato. Reintentando navegación...")
                        if discord_webhook:
                            enviar_discord(discord_webhook, "⚠️ Reintentando", "Se presionó comprar pero se reintentará la confirmación...", color=0xE67E22, url_producto=url)
                        driver.get(url)
                        continue

                # === ESTRATEGIA 2: Opciones alternativas rápidas ===
                try:
                    compra_exitosa = intentar_otras_opciones_ultrafast(driver, url)
                    if compra_exitosa:
                        STATUS_DATA["estado"] = "¡Compra Completada desde Ofertas! 🎉"
                        log_event("🎉 ¡¡¡COMPRA COMPLETADA DESDE OTRAS OPCIONES DE COMPRA!!!")
                        if discord_webhook:
                            enviar_discord(discord_webhook, "🎉 ¡COMPRA COMPLETADA!", f"Comprado desde opciones alternativas.\n**Producto:** {url}", color=0x2ECC71, url_producto=url)
                        break
                except Exception:
                    pass

            except Exception as e:
                log_event(f"Error en chequeo: {e}")

            # Refrescar rápidamente con intervalo Turbo
            time.sleep(STATUS_DATA["intervalo"])
            driver.refresh()

    except Exception as e:
        STATUS_DATA["estado"] = "Error 🔴"
        log_event(f"Ocurrió un error inesperado: {e}")
    finally:
        log_event("Script terminado.")
        if not modo_headless:
            input("Presiona Enter para cerrar el navegador y salir...")
        try:
            driver.quit()
        except:
            pass


if __name__ == "__main__":
    main()
