import time
import json
import urllib.request
import os
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from selenium import webdriver
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
    "chequeos": 0,
    "ultima_verificacion": "-",
    "logs": [],
    "discord_activo": False,
    "modo_headless": False,
    "inicio": time.strftime("%Y-%m-%d %H:%M:%S")
}

def log_event(mensaje):
    """Imprime un mensaje en consola y lo registra en los logs en vivo."""
    timestamp = time.strftime('%H:%M:%S')
    formatted = f"[{timestamp}] {mensaje}"
    print(formatted)
    STATUS_DATA["logs"].append(formatted)
    # Conservar últimos 30 logs
    if len(STATUS_DATA["logs"]) > 30:
        STATUS_DATA["logs"].pop(0)


class StatusServerHandler(BaseHTTPRequestHandler):
    """Maneja las peticiones del panel Web de estado."""
    def log_message(self, format, *args):
        # Silenciar logs del servidor HTTP interno para no ensuciar la consola
        pass

    def do_GET(self):
        if self.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(STATUS_DATA).encode("utf-8"))
            return

        # Renderizar dashboard HTML interactivo
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AmazonAutoCompra — Panel de Estado</title>
    <style>
        :root {{
            --bg: #0f172a;
            --card: #1e293b;
            --accent: #ff9900;
            --text: #f8fafc;
            --muted: #94a3b8;
            --success: #22c55e;
            --warning: #eab308;
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
            max-width: 800px;
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
            background: #334155;
        }}
        .status-running {{ background: #15803d; color: #fff; }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
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
            font-size: 0.8rem;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .card .val {{
            font-size: 1.4rem;
            font-weight: bold;
            margin-top: 5px;
        }}
        .logs-box {{
            background: #020617;
            border-radius: 10px;
            padding: 15px;
            font-family: monospace;
            font-size: 0.9rem;
            height: 250px;
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
            <h1>⚡ AmazonAutoCompra Dashboard</h1>
            <span class="badge status-running" id="state-badge">EN EJECUCIÓN</span>
        </div>

        <div class="grid">
            <div class="card">
                <div class="title">Estado</div>
                <div class="val" id="state-text" style="color: var(--accent);">--</div>
            </div>
            <div class="card">
                <div class="title">Chequeos Realizados</div>
                <div class="val" id="checks-count">0</div>
            </div>
            <div class="card">
                <div class="title">Última Verificación</div>
                <div class="val" id="last-check">--</div>
            </div>
        </div>

        <div class="card" style="margin-bottom: 20px;">
            <div class="title">Producto Monitoreado</div>
            <div style="margin-top: 5px; word-break: break-all;" id="product-url">--</div>
        </div>

        <h3>📋 Registros de Actividad (En Vivo)</h3>
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
                document.getElementById('checks-count').innerText = data.chequeos;
                document.getElementById('last-check').innerText = data.ultima_verificacion;
                document.getElementById('product-url').innerHTML = data.url ? `<a href="${{data.url}}" target="_blank">${{data.url}}</a>` : 'Sin URL';

                const logsContainer = document.getElementById('logs-container');
                logsContainer.innerHTML = data.logs.map(l => `<div class="log-line">${{l}}</div>`).join('');
                logsContainer.scrollTop = logsContainer.scrollHeight;
            }} catch(e) {{
                console.error("Error al actualizar dashboard:", e);
            }}
        }}

        setInterval(updateDashboard, 2000);
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
        "footer": {"text": "AmazonAutoCompra Bot v2.2"},
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    if url_producto:
        embed["url"] = url_producto

    payload = json.dumps({"embeds": [embed]}).encode("utf-8")

    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "AmazonAutoCompra/2.2"},
    )

    try:
        urllib.request.urlopen(req)
    except Exception as e:
        print(f"  [Discord] Error al enviar notificación: {e}")


def mostrar_instrucciones(modo_headless=False):
    if modo_headless or not TK_AVAILABLE:
        print("\n" + "="*60)
        print("          INSTRUCCIONES DE USO (MODO SERVIDOR)")
        print("="*60)
        print("1. El bot utilizará el perfil guardado en ./chrome_profile.")
        print("2. Si es la primera vez en un servidor headless, asegúrate de")
        print("   tener tu cuenta de Amazon con dirección y pago guardados.")
        print("3. Puedes seguir el estado en vivo desde el Dashboard Web")
        print("   o mediante las notificaciones de Discord.")
        print("="*60 + "\n")
        return

    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        instrucciones = (
            "¡Bienvenido al Bot de Auto Compra para Amazon!\n\n"
            "PASOS A SEGUIR:\n"
            "1. Haz clic en 'Aceptar' en este mensaje.\n"
            "2. En la consola, pega el enlace (URL) del artículo de Amazon y presiona ENTER.\n"
            "3. (Opcional) Pega la URL de tu Webhook de Discord para notificaciones o presiona ENTER para omitir.\n"
            "4. Se abrirá Google Chrome. ¡INICIA SESIÓN EN TU CUENTA AHÍ MISMO!\n"
            "5. Resuelve captchas si aparecen y asegúrate de tener tarjeta y dirección predeterminadas.\n"
            "6. Vuelve a la consola y PRESIONA ENTER para iniciar el monitoreo.\n\n"
            "El bot refrescará la página cada 5 segundos y comprará el producto por ti automáticamente."
        )
        
        messagebox.showinfo("Instrucciones - Bot de Auto Compra", instrucciones)
        root.destroy()
    except Exception:
        pass


def main():
    print("="*50)
    print("      BOT DE AUTO COMPRA AMAZON v2.2")
    print("="*50)
    
    # Preguntar si desea modo servidor / headless
    resp_headless = input("¿Deseas ejecutar en MODO SERVIDOR HEADLESS (sin ventana de navegador)? (s/N):\n> ").strip().lower()
    modo_headless = resp_headless in ['s', 'si', 'y', 'yes', 'true']
    STATUS_DATA["modo_headless"] = modo_headless

    mostrar_instrucciones(modo_headless)
    
    url = input("Pega aquí el enlace (URL) del producto de Amazon y presiona ENTER:\n> ").strip()
    if not url:
        print("No ingresaste ningún enlace. Cerrando...")
        input("Presiona Enter para salir...")
        return
    STATUS_DATA["url"] = url

    discord_webhook = input("\n(Opcional) Pega la URL del Webhook de Discord para recibir notificaciones (o presiona ENTER para omitir):\n> ").strip()

    if discord_webhook:
        STATUS_DATA["discord_activo"] = True
        enviar_discord(discord_webhook, "🤖 Bot Iniciado (Servidor)", f"Iniciando monitoreo de stock en Amazon.\n**Modo:** {'Headless (Servidor)' if modo_headless else 'Normal (GUI)'}\n**Producto:** {url}", color=0x3498DB, url_producto=url)

    # Iniciar servidor Web de monitoreo
    iniciar_servidor_web(puerto=8080)

    interval = 5
    selector = "#buy-now-button"

    log_event("Iniciando navegador Chrome...")
    from selenium.webdriver.chrome.options import Options
    options = Options()
    
    # Deshabilitar algunas banderas de automatización para ser menos detectables
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # Guardar sesión en carpeta de perfil de usuario local para no perder login
    profile_dir = os.path.abspath("./chrome_profile")
    options.add_argument(f"--user-data-dir={profile_dir}")

    if modo_headless:
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        log_event("Modo Headless (Servidor sin pantalla) activado ✓")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        log_event(f"Error al iniciar Chrome: {e}")
        input("Presiona Enter para salir...")
        return

    try:
        log_event(f"Navegando a la URL del producto: {url}")
        driver.get(url)
        
        if not modo_headless:
            print("\n" + "="*50)
            print("IMPORTANTE:")
            print("1. Por favor, inicia sesión en tu cuenta de Amazon en la ventana que se abrió.")
            print("2. Resuelve cualquier CAPTCHA si aparece.")
            print("3. Asegúrate de tener configurado tu método de pago y dirección.")
            print("4. Vuelve a esta consola y presiona ENTER cuando estés listo en la página del producto.")
            print("="*50 + "\n")
            
            input("Presiona ENTER aquí para comenzar a monitorear el stock... ")
        else:
            log_event("Iniciando monitoreo continuo en modo servidor...")
            time.sleep(3)

        STATUS_DATA["estado"] = "Monitoreando Stock 🟢"
        log_event("Comenzando monitoreo de stock...")
        
        while True:
            try:
                STATUS_DATA["chequeos"] += 1
                STATUS_DATA["ultima_verificacion"] = time.strftime('%H:%M:%S')
                compra_exitosa = False

                # Heartbeat de estado a Discord cada 100 chequeos (~10 minutos)
                if discord_webhook and STATUS_DATA["chequeos"] % 100 == 0:
                    enviar_discord(discord_webhook, "💚 Estado del Monitoreo", f"El bot sigue activo y monitoreando.\n**Chequeos realizados:** {STATUS_DATA['chequeos']}\n**Producto:** {url}", color=0x3498DB, url_producto=url)

                # === ESTRATEGIA 1: Botón "Comprar ahora" directo ===
                try:
                    button = driver.find_element(By.CSS_SELECTOR, selector)
                    if button.is_displayed():
                        log_event("¡BOTÓN DE COMPRA ENCONTRADO!")
                        STATUS_DATA["estado"] = "Comprando ⚡"

                        if discord_webhook:
                            enviar_discord(discord_webhook, "⚡ Stock Detectado!", "¡Botón 'Comprar ahora' encontrado! Intentando realizar la compra...", color=0xF1C40F, url_producto=url)

                        button.click()
                        log_event("Haciendo clic en Comprar ahora...")

                        compra_exitosa = intentar_confirmar_pedido(driver)

                        if compra_exitosa:
                            STATUS_DATA["estado"] = "¡Compra Completada! 🎉"
                            log_event("¡¡¡COMPRA COMPLETADA EXITOSAMENTE!!!")
                            if discord_webhook:
                                enviar_discord(discord_webhook, "🎉 ¡COMPRA COMPLETADA!", f"El producto fue comprado exitosamente.\n**Producto:** {url}", color=0x2ECC71, url_producto=url)
                            break
                        else:
                            STATUS_DATA["estado"] = "Monitoreando Stock 🟢"
                            log_event("No se pudo confirmar el pedido. Volviendo a la página del producto para reintentar...")
                            if discord_webhook:
                                enviar_discord(discord_webhook, "⚠️ Falló la Confirmación", "Se hizo clic en comprar pero no se pudo confirmar la orden. Reintentando...", color=0xE67E22, url_producto=url)
                            driver.get(url)
                            time.sleep(3)
                            continue

                    else:
                        log_event("Sin stock (botón oculto). Revisando opciones alternativas...")
                except NoSuchElementException:
                    log_event("Sin stock (botón no existe). Revisando opciones alternativas...")

                # === ESTRATEGIA 2: "Ver otras opciones de compra" / "Other buying options" ===
                try:
                    compra_exitosa = intentar_otras_opciones(driver, url)
                    if compra_exitosa:
                        STATUS_DATA["estado"] = "¡Compra Completada desde Ofertas! 🎉"
                        log_event("¡¡¡COMPRA COMPLETADA EXITOSAMENTE desde otra opción de compra!!!")
                        if discord_webhook:
                            enviar_discord(discord_webhook, "🎉 ¡COMPRA COMPLETADA!", f"El producto fue comprado exitosamente desde otra opción de compra.\n**Producto:** {url}", color=0x2ECC71, url_producto=url)
                        break
                except Exception as e:
                    pass

            except Exception as e:
                log_event(f"Error durante el chequeo: {e}")

            # Refrescar y esperar
            time.sleep(interval)
            driver.refresh()
            time.sleep(2)

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


def intentar_confirmar_pedido(driver):
    """Intenta confirmar el pedido en la página de checkout. Reintenta varias veces."""
    checkout_selectors = [
        (By.NAME, "placeYourOrder1"),
        (By.ID, "submitOrderButtonId"),
        (By.ID, "bottomSubmitOrderButtonId"),
        (By.CSS_SELECTOR, "input[aria-labelledby='submitOrderButtonId-announce']"),
        (By.CSS_SELECTOR, "input[title='Place your order']"),
        (By.CSS_SELECTOR, "span.place-your-order-button input"),
        (By.CSS_SELECTOR, ".place-your-order-button"),
        (By.CSS_SELECTOR, "#placeYourOrder input"),
        (By.CSS_SELECTOR, "#submitOrderButtonId input"),
        (By.XPATH, "//input[contains(@name,'placeYourOrder')]"),
        (By.XPATH, "//span[contains(@id,'submit')]//input"),
    ]

    for intento in range(1, 4):
        log_event(f"Intento {intento}/3 de confirmar pedido...")
        time.sleep(3 + intento)

        for by, sel in checkout_selectors:
            try:
                confirm_btn = driver.find_element(by, sel)
                if confirm_btn.is_displayed():
                    confirm_btn.click()
                    log_event(f"¡Pedido confirmado usando selector: {sel}!")
                    time.sleep(3)

                    try:
                        page_text = driver.page_source.lower()
                        if any(kw in page_text for kw in ["thank you", "gracias", "order placed", "pedido realizado", "confirmación del pedido"]):
                            return True
                    except:
                        pass
                    return True
            except NoSuchElementException:
                continue
            except Exception:
                continue

    return False


def intentar_otras_opciones(driver, url_producto):
    """Busca y hace clic en 'Otras opciones de compra' para comprar de otro vendedor."""
    otras_opciones_selectores = [
        (By.CSS_SELECTOR, "#mbc-action-panel-wrapper a"),
        (By.CSS_SELECTOR, "#mbc a.a-touch-link"),
        (By.CSS_SELECTOR, ".olp-text-box a"),
        (By.CSS_SELECTOR, "#olp_feature_div a"),
        (By.CSS_SELECTOR, "#usedBuySection a"),
        (By.CSS_SELECTOR, "#buybox-see-all-buying-choices a"),
        (By.CSS_SELECTOR, "#buybox-see-all-buying-choices button"),
        (By.CSS_SELECTOR, "a[href*='offer-listing']"),
        (By.CSS_SELECTOR, "#all-offers-display a"),
        (By.CSS_SELECTOR, ".a-section #aod-pinned-offer"),
        (By.XPATH, "//a[contains(text(),'otras opciones')]"),
        (By.XPATH, "//a[contains(text(),'Otras opciones')]"),
        (By.XPATH, "//a[contains(text(),'opciones de compra')]"),
        (By.XPATH, "//a[contains(text(),'buying options')]"),
        (By.XPATH, "//a[contains(text(),'other sellers')]"),
        (By.XPATH, "//span[contains(text(),'Ver otras opciones')]/.."),
        (By.XPATH, "//a[contains(text(),'Ver otras opciones')]"),
        (By.XPATH, "//input[@id='buybox-see-all-buying-choices-announce']"),
        (By.XPATH, "//span[contains(text(),'See All Buying Options')]/.."),
    ]

    for by, sel in otras_opciones_selectores:
        try:
            link = driver.find_element(by, sel)
            if link.is_displayed():
                log_event(f"Encontrado enlace de otras opciones: {sel}")
                link.click()
                time.sleep(3)

                exito = intentar_comprar_desde_ofertas(driver, url_producto)
                if exito:
                    return True
                else:
                    driver.get(url_producto)
                    time.sleep(2)
                    return False
        except NoSuchElementException:
            continue
        except Exception:
            continue

    return False


def intentar_comprar_desde_ofertas(driver, url_producto):
    """Desde el panel/página de ofertas, intenta comprar la primera opción disponible."""
    time.sleep(2)

    add_to_cart_selectors = [
        (By.CSS_SELECTOR, "#aod-offer input[name='submit.addToCart']"),
        (By.CSS_SELECTOR, "#aod-pinned-offer input[name='submit.addToCart']"),
        (By.CSS_SELECTOR, "input[name='submit.addToCart']"),
        (By.CSS_SELECTOR, ".aod-offer input.a-button-input"),
        (By.XPATH, "//input[@name='submit.addToCart']"),
        (By.XPATH, "//span[contains(text(),'Agregar al carrito')]/.."),
        (By.XPATH, "//span[contains(text(),'Add to Cart')]/.."),
        (By.XPATH, "//input[contains(@aria-labelledby,'addToCart')]"),
    ]

    for by, sel in add_to_cart_selectors:
        try:
            btns = driver.find_elements(by, sel)
            for btn in btns:
                if btn.is_displayed():
                    log_event(f"Haciendo clic en 'Agregar al carrito' desde ofertas: {sel}")
                    btn.click()
                    time.sleep(3)
                    return intentar_checkout_desde_carrito(driver)
        except Exception:
            continue

    return False


def intentar_checkout_desde_carrito(driver):
    """Desde el carrito, intenta hacer checkout y confirmar la compra."""
    try:
        driver.get("https://www.amazon.com/gp/cart/view.html")
        time.sleep(3)
    except:
        pass

    checkout_btns = [
        (By.CSS_SELECTOR, "input[name='proceedToRetailCheckout']"),
        (By.CSS_SELECTOR, "#sc-buy-box-ptc-button input"),
        (By.CSS_SELECTOR, "input[value='Proceed to checkout']"),
        (By.XPATH, "//input[contains(@name,'proceedToCheckout')]"),
        (By.XPATH, "//input[contains(@value,'Tramitar pedido')]"),
        (By.XPATH, "//input[contains(@value,'Proceed to checkout')]"),
        (By.XPATH, "//span[contains(text(),'Tramitar pedido')]/.."),
        (By.XPATH, "//span[contains(text(),'Proceed to checkout')]/.."),
    ]

    for by, sel in checkout_btns:
        try:
            btn = driver.find_element(by, sel)
            if btn.is_displayed():
                log_event(f"Procediendo al checkout desde carrito: {sel}")
                btn.click()
                time.sleep(4)
                return intentar_confirmar_pedido(driver)
        except NoSuchElementException:
            continue
        except Exception:
            continue

    return False


if __name__ == "__main__":
    main()
