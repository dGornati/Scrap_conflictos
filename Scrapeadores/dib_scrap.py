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
options.add_argument("--blink-settings=imagesEnabled=false")
options.add_argument("--disable-plugins")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def wait_for_element(driver, by, selector, timeout=10):
    """Espera dinámica para la presencia de un elemento."""
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, selector)))

def scroll_and_load_more(repetitions=2):
    """Scroll hacia el final de la página y presiona el botón 'Cargar más'."""
    for _ in range(repetitions):
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Espera para cargar el contenido dinámico

            load_more_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#next-page-tdi_50"))
            )
            load_more_button.click()
            print("Botón 'Cargar más' presionado.")
            time.sleep(3)  # Espera para cargar el contenido después del clic
        except Exception as e:
            print(f"No se pudo presionar 'Cargar más': {e}")
            break

def scrape_links():
    """Extrae los enlaces de noticias desde la página principal."""
    url = "https://dib.com.ar/ultimas-noticias/"
    driver.get(url)
    scroll_and_load_more(repetitions=2)

    # Extraer los enlaces de noticias
    wait_for_element(driver, By.CSS_SELECTOR, ".td-module-title a")
    articles = driver.find_elements(By.CSS_SELECTOR, ".td-module-title a")
    article_links = list(set([article.get_attribute("href") for article in articles if article.get_attribute("href")]))

    print(f"Enlaces únicos extraídos: {len(article_links)}")
    return article_links

def scrape_article(link):
    """Extrae los datos de una noticia específica."""
    driver.get(link)
    try:
        wait_for_element(driver, By.CSS_SELECTOR, ".td-post-title .entry-title")
        title = driver.find_element(By.CSS_SELECTOR, ".td-post-title .entry-title").text.strip()
        date = driver.find_element(By.CSS_SELECTOR, ".td-module-date").text.strip()
        body_elements = driver.find_elements(By.CSS_SELECTOR, ".tagdiv-type")
        body = " ".join([element.text.strip() for element in body_elements if element.text.strip()])
        return {"Título": title, "Fecha": date, "Cuerpo": body, "URL": link}
    except Exception as e:
        print(f"Error procesando {link}: {e}")
        return None

def main():
    print("Scrapeando DIB...")
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
        df.to_csv("output/noticias_dib.csv", index=False, encoding="utf-8-sig")
        print("Scraping completado. Datos guardados en 'noticias_dib.csv'.")
    else:
        print("No se encontraron noticias para guardar.")

if __name__ == "__main__":
    main()