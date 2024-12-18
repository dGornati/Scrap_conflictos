from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import time
import pandas as pd
from datetime import datetime

# Set up Chrome options
options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def main():
    dias_hacia_atras = 3
    fecha_hoy        = datetime.now()
    fecha_inicial    = fecha_hoy - pd.Timedelta(days=dias_hacia_atras)

    url_base = "https://quedigital.com.ar"
    secciones = ["sociedad"]  # Solo scrapear la sección "sociedad"

    try:
        all_data = []

        for seccion in secciones:
            message = f"\nScrapeando sección '{seccion}' entre fechas {fecha_inicial.strftime('%Y-%m-%d')} y {fecha_hoy.strftime('%Y-%m-%d')}"
            print(message)

            # Extraer artículos de la página principal
            article_links = scrape_seccion_articles(url_base, seccion, fecha_hoy, fecha_inicial)
            all_data.extend(article_links)

        # Guardar los artículos en un CSV
        df = pd.DataFrame(all_data)
        df.to_csv("output/noticias_quedigital.csv", index=False)

    finally:
        message = "Scraping completado con exito."
        print(message)
        driver.quit()

def scrape_seccion_articles(url_base, seccion, fecha_hoy, fecha_inicial):
    '''
    Función que scrapea los artículos de la sección de "Sociedad" de Qué Digital
    entre las fechas `fecha_hoy` y `fecha_inicial`.
    
    Devuelve una lista de diccionarios con los artículos de la sección y sus enlaces.
    '''
    
    url = f"{url_base}/{seccion}/"
    driver.get(url)
    
    # Esperar 3 segundos para permitir que los elementos se carguen
    time.sleep(3)
    
    # Chequear si el botón "Consentir" está presente y hacer clic en él
    try:
        boton_consentir = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "fc-cta-consent"))
        )
        boton_consentir.click()
        print(f"\tBotón 'Consentir' clickeado en la sección '{seccion}'.")
    except:
        pass

    # Cerrar el modal de notificación si está presente
    close_notification_modal()

    # Realizar scroll hacia abajo hasta la fecha inicial y hacer clic en el botón "Más noticias"
    scroll_down_until_last_week_date(fecha_inicial)

    # Extraer los artículos a un DataFrame
    links_data = extract_articles_to_dataframe()

    # Caso cuando no se encuentran artículos
    if not links_data:
        message = "   No se encontraron artículos"
        print(message)
        return []

    # Acceder a los artículos y extraer los detalles de cada uno
    all_article_data = []
    for link in links_data:
        article_details = scrape_article_details(link['link'])
        if article_details:  # Si el artículo tiene detalles, lo agregamos
            all_article_data.append(article_details)

    return all_article_data

def close_notification_modal():
    """Cerrar el modal de notificación si está presente."""
    try:
        # Verificar si el modal de notificación está presente y hacer clic en el botón de cancelar
        modal = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#onesignal-slidedown-dialog"))
        )
        cancel_button = modal.find_element(By.CSS_SELECTOR, "#onesignal-slidedown-cancel-button")
        cancel_button.click()
        print("\tModal de notificación cerrado.")
    except (TimeoutException, NoSuchElementException):
        print("\tNo se encontró el modal de notificación o ya estaba cerrado.")

def scroll_down_until_last_week_date(fecha_inicial, max_scrolls=25):
    formatted_date = fecha_inicial.strftime("%d/%m/%Y")

    print(f"\tYendo hacia abajo hasta encontrar la fecha inicial: {formatted_date}.")
    scroll_count = 0
    while scroll_count < max_scrolls:
        try:
            # Hacer scroll hasta el final de la página
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)  # Esperar que la página cargue

            # Hacer clic en el botón "Más noticias" si está disponible
            try:
                load_more_button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "#ajax-load-more > div.alm-btn-wrap > button"))
                )
                # Asegurarnos de que el botón está visible y hacer scroll hasta él
                driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
                load_more_button.click()
                print("\tBotón 'Más noticias' clickeado.")
                time.sleep(2)  # Esperar a que se carguen los artículos después de hacer clic
            except (TimeoutException, NoSuchElementException):
                pass

            # Esperar a que los artículos se carguen
            time.sleep(2)

            # Extraer todos los títulos y enlaces de los artículos
            articles = driver.find_elements(By.CSS_SELECTOR, ".clearfix div div > :nth-child(1) a")

            links = []
            for article in articles:
                try:
                    link = article.get_attribute("href")
                    print(f"Enlace encontrado: {link}")
                    links.append({'link': link})
                except NoSuchElementException:
                    continue

            scroll_count += 1
            return links

        except (TimeoutException, NoSuchElementException):
            print("Elemento no encontrado, haciendo scroll nuevamente.")
            scroll_count += 1

        except Exception as e:
            print(f"Ocurrió un error: {e}")
            break

    print("Se alcanzó el máximo de scrolls sin encontrar la fecha inicial.")
    return []

def extract_articles_to_dataframe():
    """Extrae los datos de los artículos de la página actual y los devuelve como un DataFrame."""
    
    # Extraer los artículos usando el único selector
    articles = driver.find_elements(By.CSS_SELECTOR, ".clearfix div div > :nth-child(1) a")
    
    message = f"\tSe encontraron {len(articles)} artículos"
    print(message)
    
    links = []
    for article in articles:
        try:
            link = article.get_attribute("href")
            links.append({'link': link})
        except NoSuchElementException:
            continue

    return links

def scrape_article_details(link):
    """Abre el artículo y extrae el título, la fecha, el cuerpo y el link"""
    driver.get(link)
    time.sleep(3)

    try:
        # Extraer título
        title = driver.find_element(By.CSS_SELECTOR, ".main-title").text.strip()
    except NoSuchElementException:
        title = "No disponible"

    try:
        # Extraer fecha
        date = driver.find_element(By.CSS_SELECTOR, ".fecha").text.strip()
    except NoSuchElementException:
        date = "No disponible"

    try:
        # Extraer cuerpo (todos los párrafos)
        body = " ".join([p.text for p in driver.find_elements(By.CSS_SELECTOR, "p")]).strip()
    except NoSuchElementException:
        body = "No disponible"

    return {'titulo': title, 'fecha': date, 'cuerpo': body, 'link': link}

if __name__ == "__main__":
    main()
