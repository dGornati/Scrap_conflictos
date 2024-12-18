from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time

# Configuración del navegador
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def scroll_and_load_more(section_url, max_loads=5):
    """Scrollea y presiona el botón para cargar más noticias."""
    driver.get(section_url)
    time.sleep(3)  # Esperar que la página cargue

    for _ in range(max_loads):
        try:
            load_more_button = driver.find_element(By.CSS_SELECTOR, "#vermasboton")
            load_more_button.click()
            time.sleep(3)  # Esperar que las noticias se carguen
        except Exception:
            print("No se pudo cargar más noticias o no hay más botón disponible.")
            break

def scrape_section(section_url, section_name, max_loads=5):
    """Scrapea una sección específica y devuelve una lista de diccionarios con la información."""
    scroll_and_load_more(section_url, max_loads)

    # Extraer enlaces de las noticias
    articles = driver.find_elements(By.CSS_SELECTOR, "#main-content a")
    article_links = [article.get_attribute('href') for article in articles]

    news_data = []
    for link in article_links:
        try:
            driver.get(link)
            time.sleep(2)

            # Extraer datos de la noticia
            title = driver.find_element(By.CSS_SELECTOR, ".titular").text.strip()
            date = driver.find_element(By.CSS_SELECTOR, ".fecha").text.strip()
            body_element = driver.find_element(By.CSS_SELECTOR, "#cuerpo-nota")
            body = body_element.text.strip()

            news_data.append({
                "Sección": section_name,
                "Título": title,
                "Fecha": date,
                "Cuerpo": body,
                "URL": link
            })
        except Exception as e:
            print(f"Error procesando {link}: {e}")
            continue
    return news_data

def main():
    sections = {
        "Necochea": "https://www.diario4v.com/necochea/"
    }

    all_news = []
    for section_name, section_url in sections.items():
        print(f"Scrapeando sección: {section_name}")
        section_news = scrape_section(section_url, section_name)
        all_news.extend(section_news)

    # Guardar resultados en CSV
    df = pd.DataFrame(all_news)
    df.to_csv("output/noticias_cuatrovientos.csv", index=False, encoding="utf-8-sig")
    print("Scraping completado. Datos guardados en 'noticias_cuatrovientos.csv'.")

if __name__ == "__main__":
    try:
        main()
    finally:
        driver.quit()
