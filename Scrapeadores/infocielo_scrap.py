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

def scrape_section(section_url, section_name):
    """Scrapea una sección específica y devuelve una lista de diccionarios con la información."""
    driver.get(section_url)
    time.sleep(3)  # Esperar que cargue la página
    
    # Selección de enlaces de noticias
    articles = driver.find_elements(By.CSS_SELECTOR, ".col-md-4 .news-article_title a, .col-md-6 .news-article_title a, .justify-content-end .news-article_title a")
    article_links = [article.get_attribute('href') for article in articles]

    news_data = []
    for link in article_links:
        try:
            # Entrar al enlace de la noticia
            driver.get(link)
            time.sleep(2)

            # Extraer datos
            title = driver.find_element(By.CSS_SELECTOR, ".detail-note_header_title").text.strip()
            date = driver.find_element(By.CSS_SELECTOR, ".d-block").text.strip()
            body_elements = driver.find_elements(By.CSS_SELECTOR, ".detail-note_body h2, .detail-note_body p, strong")
            body = " ".join([element.text.strip() for element in body_elements])
            
            news_data.append({
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
        "La Plata": "https://infocielo.com/la-plata",
        "Política": "https://infocielo.com/politica-y-economia",
        "Sociedad": "https://infocielo.com/sociedad"
    }

    all_news = []
    for section_name, section_url in sections.items():
        print(f"Scrapeando sección: {section_name}")
        section_news = scrape_section(section_url, section_name)
        all_news.extend(section_news)

    # Guardar resultados en CSV
    df = pd.DataFrame(all_news)
    df.to_csv("output/noticias_infocielo.csv", index=False, encoding="utf-8-sig")
    print("Scraping completado. Datos guardados en 'noticias_infocielo.csv'.")

if __name__ == "__main__":
    try:
        main()
    finally:
        driver.quit()
