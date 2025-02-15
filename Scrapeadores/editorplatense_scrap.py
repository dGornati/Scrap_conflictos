import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

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

def scroll_and_click_more(repetitions=2):
    """Scroll hacia el final de la página y presiona el botón 'Ver más'."""
    for _ in range(repetitions):
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)  # Espera para cargar el contenido dinámico

            load_more_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".QjWxu"))
            )
            load_more_button.click()
            print("Botón 'Ver más' presionado.")
            time.sleep(5)  # Espera para cargar el contenido después del clic
        except Exception as e:
            print(f"No se pudo presionar 'Ver más': {e}")
            break

def extract_date_from_url(url):
    """Extrae la fecha (AAAA-MM-DD) desde la URL."""
    try:
        match = re.search(r"/\d{4}/\d{2}/\d{2}/", url)
        if match:
            date_parts = match.group(0).strip("/").split("/")
            return f"{date_parts[0]}-{date_parts[1]}-{date_parts[2]}"
    except Exception as e:
        print(f"Error extrayendo la fecha de la URL {url}: {e}")
    return None

def scrape_section(section_url):
    """Extrae los enlaces de noticias de una sección específica."""
    driver.get(section_url)
    scroll_and_click_more(repetitions=2)

    # Extraer los enlaces de noticias
    wait_for_element(driver, By.CSS_SELECTOR, "a")  # Selector más general
    articles = driver.find_elements(By.CSS_SELECTOR, "a")

    # Diagnóstico: Imprimir todos los textos y atributos de href
    print("Elementos detectados:")
    for article in articles:
        print(f"Texto: {article.text}, Href: {article.get_attribute('href')}")

    # Filtrar los enlaces relevantes basados en patrones de URL
    article_links = list(set([
        article.get_attribute("href")
        for article in articles
        if article.get_attribute("href") and re.search(r"/\d{4}/\d{2}/\d{2}/", article.get_attribute("href"))
    ]))

    print(f"Enlaces extraídos de {section_url}: {len(article_links)}")
    return article_links

def scrape_article(link):
    """Extrae los datos de una noticia específica."""
    driver.get(link)
    try:
        wait_for_element(driver, By.CSS_SELECTOR, "#TextTituloID")
        title = driver.find_element(By.CSS_SELECTOR, "#TextTituloID").text.strip()
        body_elements = driver.find_elements(By.CSS_SELECTOR, ".bUUTFp")
        body = " ".join([element.text.strip() for element in body_elements if element.text.strip()])
        date = extract_date_from_url(link)
        return {"Título": title, "Fecha": date, "Cuerpo": body, "URL": link}
    except Exception as e:
        print(f"Error procesando {link}: {e}")
        return None

def main():
    sections = [
        "https://eleditorplatense.com/categoria/Política",
        "https://eleditorplatense.com/categoria/La%20Región",
        "https://eleditorplatense.com/categoria/Economía"
    ]

    all_links = []
    for section in sections:
        print(f"Scrapeando sección: {section}")
        section_links = scrape_section(section)
        all_links.extend(section_links)

    # Eliminar duplicados
    unique_links = list(set(all_links))
    print(f"Enlaces únicos extraídos: {len(unique_links)}")

    all_news = []
    for i, link in enumerate(unique_links):
        print(f"Procesando {i + 1}/{len(unique_links)}: {link}")
        article_data = scrape_article(link)
        if article_data:
            all_news.append(article_data)

    driver.quit()

    # Guardar resultados
    if all_news:
        df = pd.DataFrame(all_news)
        df.to_csv("output/noticias_editorplatense.csv", index=False, encoding="utf-8-sig")
        print("Scraping completado. Datos guardados en 'noticias_editorplatense.csv'.")
    else:
        print("No se encontraron noticias para guardar.")

if __name__ == "__main__":
    main()
