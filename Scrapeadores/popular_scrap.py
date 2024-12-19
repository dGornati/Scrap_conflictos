import os
import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuración del navegador
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("--blink-settings=imagesEnabled=false")  # No cargar imágenes
options.add_argument("--disable-plugins")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def wait_for_element(driver, by, selector, timeout=10):
    """Espera dinámica para la presencia de un elemento."""
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, selector)))

def scrape_section(section_url):
    """Extrae los enlaces de las noticias de una sección específica."""
    print(f"Accediendo a la sección: {section_url}")
    driver.get(section_url)
    wait_for_element(driver, By.CSS_SELECTOR, ".title-item a")  # Esperar a que los enlaces estén presentes
    articles = driver.find_elements(By.CSS_SELECTOR, ".title-item a")
    article_links = list(set([article.get_attribute('href') for article in articles]))
    print(f"Enlaces encontrados en {section_url}: {len(article_links)}")
    time.sleep(random.uniform(1, 3))  # Espera aleatoria para evitar bloqueos
    return article_links[:30]  # Limitar a 30 noticias

def scrape_article(link):
    """Extrae los datos de una noticia específica."""
    print(f"Accediendo al artículo: {link}")
    driver.get(link)
    try:
        wait_for_element(driver, By.CSS_SELECTOR, "#article-post > header > div.row > div > h1")
        title = driver.find_element(By.CSS_SELECTOR, "#article-post > header > div.row > div > h1").text.strip()
        date = driver.find_element(By.CSS_SELECTOR, "time").text.strip()
        body_elements = driver.find_elements(By.CSS_SELECTOR, "#article-post p")
        body = " ".join([element.text.strip() for element in body_elements])
        print(f"Título: {title}, Fecha: {date}")
        return {"Título": title, "Fecha": date, "Cuerpo": body, "URL": link}
    except Exception as e:
        print(f"Error procesando {link}: {e}")
        return None

def main():
    sections = {
        "Provincia": "https://www.diariopopular.com.ar/provincia",
        "Política": "https://www.diariopopular.com.ar/politica"
    }
    all_news = []

    for section_name, section_url in sections.items():
        print(f"Scrapeando sección: {section_name}")
        links = scrape_section(section_url)
        print(f"Sección: {section_name}, Links encontrados: {len(links)}")

        for i, link in enumerate(links):
            print(f"Procesando {i + 1}/{len(links)}: {link}")
            article_data = scrape_article(link)
            if article_data:
                #article_data["Sección"] = section_name
                all_news.append(article_data)

    driver.quit()

    # Crear carpeta de salida si no existe
    os.makedirs("output", exist_ok=True)

    # Guardar resultados
    if all_news:
        df = pd.DataFrame(all_news)
        output_path = "output/noticias_popular.csv"
        df.to_csv(output_path, index=False, encoding="utf-8-sig")
        print(f"Scraping completado. Datos guardados en '{output_path}'.")
    else:
        print("No se encontraron noticias para guardar.")

if __name__ == "__main__":
    main()
