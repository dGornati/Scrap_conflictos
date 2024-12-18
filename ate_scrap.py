import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Configuración del navegador
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("--blink-settings=imagesEnabled=false")  # No cargar imágenes
options.add_argument("--disable-plugins")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def wait_for_element(driver, by, selector, timeout=10):
    """Espera dinámica para la presencia de un elemento."""
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, selector)))

def scroll_to_load_all(driver, scroll_pause_time=2):
    """Desplaza la página hacia abajo para cargar todo el contenido."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def scrape_links():
    """Extrae los enlaces de las noticias desde la página principal."""
    url = "https://atepba.org.ar/"
    driver.get(url)
    scroll_to_load_all(driver)

    # Esperar a que los enlaces estén presentes
    wait_for_element(driver, By.CSS_SELECTOR, "article a")

    # Extraer enlaces de todas las secciones relevantes
    articles = driver.find_elements(By.CSS_SELECTOR, "article a")

    # Debug: Imprimir los textos y enlaces encontrados
    print("Artículos encontrados:")
    for article in articles:
        print(f"Título: {article.text}, Enlace: {article.get_attribute('href')}")

    # Obtener los enlaces únicos
    article_links = list(set([article.get_attribute("href") for article in articles if article.get_attribute("href")]))

    print(f"Enlaces únicos extraídos: {len(article_links)}")
    return article_links


def process_date(date_text):
    """Divide el texto de la fecha en Sección y Fecha."""
    try:
        section, date = date_text.split(" | ")
        return section.strip(), date.strip()
    except ValueError:
        return None, date_text.strip()  # Si no se encuentra el separador, retorna el texto completo como fecha

def scrape_article(link):
    """Extrae los datos de una noticia específica."""
    driver.get(link)
    try:
        wait_for_element(driver, By.CSS_SELECTOR, ".lh46")
        title = driver.find_element(By.CSS_SELECTOR, ".lh46").text.strip()
        date_text = driver.find_element(By.CSS_SELECTOR, ".ttu.mb5").text.strip()
        section, date = process_date(date_text)
        body_elements = driver.find_elements(By.CSS_SELECTOR, ".wysiwyg p")
        body = " ".join([element.text.strip() for element in body_elements])
        return {"Título": title, "Sección": section, "Fecha": date, "Cuerpo": body, "URL": link}
    except Exception as e:
        print(f"Error procesando {link}: {e}")
        return None

def main():
    print("Scrapeando ATE...")
    links = scrape_links()
    print(f"Se encontraron {len(links)} enlaces de noticias.")

    all_news = []
    for i, link in enumerate(links):
        print(f"Procesando {i + 1}/{len(links)}: {link}")
        article_data = scrape_article(link)
        if article_data:
            all_news.append(article_data)

    driver.quit()

    # Guardar resultados
    if all_news:
        df = pd.DataFrame(all_news)
        df.to_csv("output/noticias_ate.csv", index=False, encoding="utf-8-sig")
        print("Scraping completado. Datos guardados en 'noticias_ate.csv'.")
    else:
        print("No se encontraron noticias para guardar.")

if __name__ == "__main__":
    main()
