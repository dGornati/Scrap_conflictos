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

def close_popup():
    """Cierra el popup si aparece."""
    try:
        close_button = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".popmake-close")))
        close_button.click()
        print("Popup cerrado.")
    except Exception:
        print("No se encontró popup para cerrar.")

def scrape_section(section_url):
    """Extrae los enlaces de noticias de una sección específica."""
    driver.get(section_url)
    close_popup()

    # Esperar a que los artículos estén presentes
    wait_for_element(driver, By.CSS_SELECTOR, ".td-module-title a")

    # Obtener enlaces únicos
    articles = driver.find_elements(By.CSS_SELECTOR, ".td-module-title a")
    article_links = list(set([article.get_attribute("href") for article in articles if article.get_attribute("href")]))

    print(f"Enlaces extraídos de {section_url}: {len(article_links)}")
    return article_links

def scrape_article(link):
    """Extrae los datos de una noticia específica."""
    driver.get(link)
    try:
        wait_for_element(driver, By.CSS_SELECTOR, ".td-pb-padding-side .entry-title")
        title = driver.find_element(By.CSS_SELECTOR, ".td-pb-padding-side .entry-title").text.strip()
        date = driver.find_element(By.CSS_SELECTOR, ".td-pb-padding-side .td-module-date").text.strip()
        body_elements = driver.find_elements(By.CSS_SELECTOR, "p")
        body = " ".join([element.text.strip() for element in body_elements if element.text.strip()])
        return {"Título": title, "Fecha": date, "Cuerpo": body, "URL": link}
    except Exception as e:
        print(f"Error procesando {link}: {e}")
        return None

def main():
    sections = [
        "https://www.diariolavozdezarate.com/category/la-ciudad/",
        "https://www.diariolavozdezarate.com/category/sociedad/",
        "https://www.diariolavozdezarate.com/category/politica/"
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
        df.to_csv("output/noticias_lavozdezarate.csv", index=False, encoding="utf-8-sig")
        print("Scraping completado. Datos guardados en 'noticias_lavozdezarate.csv'.")
    else:
        print("No se encontraron noticias para guardar.")

if __name__ == "__main__":
    main()
