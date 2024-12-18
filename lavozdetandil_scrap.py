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

def close_banners():
    """Cierra los banners emergentes si están presentes."""
    try:
        # Cierra el banner del popup de video
        popup_video_button = driver.find_element(By.CSS_SELECTOR, ".boton-cerrar-popup-video")
        popup_video_button.click()
        time.sleep(1)
    except Exception:
        pass

    try:
        # Cierra el segundo banner
        close_button = driver.find_element(By.CSS_SELECTOR, "#close")
        close_button.click()
        time.sleep(1)
    except Exception:
        pass

def scrape_section(section_url, section_name):
    """Scrapea una sección específica y devuelve una lista de diccionarios con la información."""
    driver.get(section_url)
    time.sleep(3)

    # Cerrar los banners iniciales
    close_banners()

    # Extraer los enlaces de las noticias
    articles = driver.find_elements(By.CSS_SELECTOR, ".negro")
    article_links = [article.get_attribute('href') for article in articles]

    news_data = []
    for link in article_links:
        try:
            driver.get(link)
            time.sleep(2)

            # Cerrar banners emergentes al ingresar a cada noticia
            close_banners()

            # Extraer datos de la noticia
            title = driver.find_element(By.CSS_SELECTOR, ".titulo-amplia").text.strip()
            date = driver.find_element(By.CSS_SELECTOR, ".margin-bot-5").text.strip()
            body_elements = driver.find_elements(By.CSS_SELECTOR, ".detalle-noticia p")
            body = " ".join([element.text.strip() for element in body_elements])

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
        "Locales": "https://www.lavozdetandil.com.ar/locales.html",
        "La Región": "https://www.lavozdetandil.com.ar/la-region.html"
    }

    all_news = []
    for section_name, section_url in sections.items():
        print(f"Scrapeando sección: {section_name}")
        section_news = scrape_section(section_url, section_name)
        all_news.extend(section_news)

    # Guardar resultados en CSV
    df = pd.DataFrame(all_news)
    df.to_csv("output/noticias_lavozdetandil.csv", index=False, encoding="utf-8-sig")
    print("Scraping completado. Datos guardados en 'noticias_lavozdetandil.csv'.")

if __name__ == "__main__":
    try:
        main()
    finally:
        driver.quit()
