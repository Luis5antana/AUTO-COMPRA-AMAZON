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
                # Buscar el botón de compra
                button = driver.find_element(By.CSS_SELECTOR, selector)
                if button.is_displayed():
                    print("\n" + "*"*30)
                    print("¡BOTÓN DE COMPRA ENCONTRADO!")
                    print("*"*30)
                    
                    button.click()
                    print("Haciendo clic en Comprar ahora...")
                    
                    # Esperar un poco más para que la página de pago cargue completamente
                    time.sleep(4)
                    
                    # Intentar confirmar el pedido buscando los selectores más comunes de Amazon
                    order_placed = False
                    checkout_selectors = [
                        (By.NAME, "placeYourOrder1"),
                        (By.ID, "submitOrderButtonId"),
                        (By.ID, "bottomSubmitOrderButtonId"),
                        (By.CSS_SELECTOR, "input[aria-labelledby='submitOrderButtonId-announce']"),
                        (By.CSS_SELECTOR, "input[title='Place your order']"),
                        (By.CSS_SELECTOR, ".place-your-order-button")
                    ]
                    
                    for by, sel in checkout_selectors:
                        try:
                            confirm_btn = driver.find_element(by, sel)
                            if confirm_btn.is_displayed():
                                confirm_btn.click()
                                print(f"¡Pedido confirmado usando selector {sel}!")
                                order_placed = True
                                break
                        except NoSuchElementException:
                            continue
                    
                    if order_placed:
                        print("Compra completada automáticamente a la dirección y tarjeta predeterminadas.")
                        break # Salir del ciclo
                    else:
                        print("No se encontró el botón de confirmación final de Amazon.")
                        print("Por favor, revisa la ventana del navegador y COMPLETA LA COMPRA MANUALMENTE RÁPIDO.")
                        break

                else:
                    print(f"[{time.strftime('%H:%M:%S')}] Sin stock (botón oculto).")
                    
            except NoSuchElementException:
                print(f"[{time.strftime('%H:%M:%S')}] Sin stock (botón no existe).")
            except Exception as e:
                print(f"[{time.strftime('%H:%M:%S')}] Error durante el chequeo: {e}")
            
            # Refrescar y esperar
            time.sleep(interval)
            driver.refresh()
            # Pequeña pausa después del refresh para que el DOM cargue
            time.sleep(1.5)

    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
    finally:
        print("\nScript terminado.")
        input("Presiona Enter para cerrar el navegador y salir...")
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    main()
