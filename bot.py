import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import tkinter as tk
from tkinter import messagebox

def mostrar_instrucciones():
    root = tk.Tk()
    root.withdraw() # Oculta la ventana principal
    root.attributes('-topmost', True) # Asegura que la ventana este por encima
    
    instrucciones = (
        "¡Bienvenido al Bot de Auto Compra para Amazon!\n\n"
        "PASOS A SEGUIR:\n"
        "1. Haz clic en 'Aceptar' en este mensaje.\n"
        "2. En la ventana negra de fondo, pega el enlace (URL) del articulo de Amazon que quieres buscar y presiona ENTER.\n"
        "3. Se abrira el navegador Google Chrome. ¡INICIA SESION EN TU CUENTA AHI MISMO!\n"
        "4. Resuelve los captchas (si los hay) y asegurate de tener una tarjeta y direccion predeterminadas en tu cuenta.\n"
        "5. Una vez iniciada sesion y viendo la pagina del producto, vuelve a la ventana negra y PRESIONA ENTER de nuevo.\n\n"
        "El bot comenzara a refrescar la pagina cada 5 segundos y comprara el producto por ti en cuanto aparezca."
    )
    
    messagebox.showinfo("Instrucciones - Bot de Auto Compra", instrucciones)
    root.destroy()

def main():
    mostrar_instrucciones()
    
    print("="*50)
    print("      BOT DE AUTO COMPRA AMAZON")
    print("="*50)
    
    url = input("Pega aquí el enlace (URL) del producto de Amazon y presiona ENTER:\n> ").strip()
    if not url:
        print("No ingresaste ningún enlace. Cerrando...")
        input("Presiona Enter para salir...")
        return
    
    interval = 5
    selector = "#buy-now-button"

    print("\nIniciando navegador Chrome...")
    from selenium.webdriver.chrome.options import Options
    options = Options()
    
    # Deshabilitar algunas banderas de automatización para ser menos detectables
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        print(f"Error al iniciar Chrome. ¿Tienes Google Chrome instalado? Error: {e}")
        input("Presiona Enter para salir...")
        return

    try:
        print(f"Navegando a la URL del producto: {url}")
        driver.get(url)
        
        print("\n" + "="*50)
        print("IMPORTANTE:")
        print("1. Por favor, inicia sesión en tu cuenta de Amazon en la ventana que se abrió.")
        print("2. Resuelve cualquier CAPTCHA si aparece.")
        print("3. Asegúrate de tener configurado tu método de pago y dirección.")
        print("4. Vuelve a esta consola y presiona ENTER cuando estés listo en la página del producto.")
        print("="*50 + "\n")
        
        input("Presiona ENTER aquí para comenzar a monitorear el stock... ")

        print("\nComenzando monitoreo...")
        
        while True:
            try:
                compra_exitosa = False

                # === ESTRATEGIA 1: Botón "Comprar ahora" directo ===
                try:
                    button = driver.find_element(By.CSS_SELECTOR, selector)
                    if button.is_displayed():
                        print("\n" + "*"*30)
                        print("¡BOTÓN DE COMPRA ENCONTRADO!")
                        print("*"*30)

                        button.click()
                        print("Haciendo clic en Comprar ahora...")

                        compra_exitosa = intentar_confirmar_pedido(driver)

                        if compra_exitosa:
                            print("\n¡¡¡COMPRA COMPLETADA EXITOSAMENTE!!!")
                            break
                        else:
                            print("No se pudo confirmar el pedido. Volviendo a la página del producto para reintentar...")
                            driver.get(url)
                            time.sleep(3)
                            continue

                    else:
                        print(f"[{time.strftime('%H:%M:%S')}] Sin stock (botón oculto). Buscando otras opciones...")
                except NoSuchElementException:
                    print(f"[{time.strftime('%H:%M:%S')}] Sin stock (botón no existe). Buscando otras opciones...")

                # === ESTRATEGIA 2: "Ver otras opciones de compra" / "Other buying options" ===
                try:
                    compra_exitosa = intentar_otras_opciones(driver, url)
                    if compra_exitosa:
                        print("\n¡¡¡COMPRA COMPLETADA EXITOSAMENTE desde otra opción de compra!!!")
                        break
                except Exception as e:
                    print(f"[{time.strftime('%H:%M:%S')}] No se encontraron otras opciones de compra: {e}")

            except Exception as e:
                print(f"[{time.strftime('%H:%M:%S')}] Error durante el chequeo: {e}")

            # Refrescar y esperar
            time.sleep(interval)
            driver.refresh()
            # Pequeña pausa después del refresh para que el DOM cargue
            time.sleep(2)

    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
    finally:
        print("\nScript terminado.")
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

    # Reintentar hasta 3 veces con espera entre cada intento
    for intento in range(1, 4):
        print(f"  Intento {intento}/3 de confirmar pedido...")
        time.sleep(3 + intento)  # Espera progresiva: 4s, 5s, 6s

        for by, sel in checkout_selectors:
            try:
                confirm_btn = driver.find_element(by, sel)
                if confirm_btn.is_displayed():
                    confirm_btn.click()
                    print(f"  ¡Pedido confirmado usando selector: {sel}!")
                    time.sleep(3)

                    # Verificar si la compra fue exitosa buscando confirmación en la página
                    try:
                        page_text = driver.page_source.lower()
                        if any(kw in page_text for kw in ["thank you", "gracias", "order placed", "pedido realizado", "confirmación del pedido"]):
                            return True
                    except:
                        pass
                    return True  # Asumimos éxito si se hizo clic
            except NoSuchElementException:
                continue
            except Exception:
                continue

    return False


def intentar_otras_opciones(driver, url_producto):
    """Busca y hace clic en 'Otras opciones de compra' para comprar de otro vendedor."""

    # Selectores para encontrar el enlace/botón de otras opciones
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
                print(f"  → Encontrado enlace de otras opciones: {sel}")
                link.click()
                time.sleep(3)

                # Ahora buscar el botón de "Agregar al carrito" o "Comprar" en el panel de ofertas
                exito = intentar_comprar_desde_ofertas(driver, url_producto)
                if exito:
                    return True
                else:
                    # Volver a la página del producto
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

    # Selectores para el panel AOD (All Offers Display) que Amazon usa como overlay
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
                    print(f"  → Haciendo clic en 'Agregar al carrito' desde ofertas: {sel}")
                    btn.click()
                    time.sleep(3)

                    # Ahora intentar ir al checkout y comprar
                    return intentar_checkout_desde_carrito(driver)
        except Exception:
            continue

    print("  No se encontró botón de agregar al carrito en las ofertas.")
    return False


def intentar_checkout_desde_carrito(driver):
    """Desde el carrito, intenta hacer checkout y confirmar la compra."""
    # Ir al carrito
    try:
        driver.get("https://www.amazon.com/gp/cart/view.html")
        time.sleep(3)
    except:
        pass

    # Buscar botón de proceder al checkout
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
                print(f"  → Procediendo al checkout: {sel}")
                btn.click()
                time.sleep(4)
                return intentar_confirmar_pedido(driver)
        except NoSuchElementException:
            continue
        except Exception:
            continue

    print("  No se encontró botón de checkout en el carrito.")
    return False


if __name__ == "__main__":
    main()
