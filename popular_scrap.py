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

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def wait_for_element(driver, by, selector, timeout=5):
    """Espera dinámica para la presencia de un elemento."""
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, selector)))

def scrape_section(section_url):
    """Extrae los enlaces de las noticias de una sección específica."""
    driver.get(section_url)
    wait_for_element(driver, By.CSS_SELECTOR, ".title-item a")  # Esperar a que los enlaces estén presentes
    articles = driver.find_elements(By.CSS_SELECTOR, ".title-item a")
    article_links = list(set([article.get_attribute('href') for article in articles]))
    return article_links[:30]  # Limitar a 30 noticias

def scrape_article(link):
    """Extrae los datos de una noticia específica."""
    driver.get(link)
    try:
        wait_for_element(driver, By.CSS_SELECTOR, "#article-post > header > div.row > div > h1")
        title = driver.find_element(By.CSS_SELECTOR, "#article-post > header > div.row > div > h1").text.strip()
        date = driver.find_element(By.CSS_SELECTOR, "time").text.strip()
        body_elements = driver.find_elements(By.CSS_SELECTOR, "#article-post p")
        body = " ".join([element.text.strip() for element in body_elements])
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
        for i, link in enumerate(links):
            print(f"Procesando {i + 1}/{len(links)}: {link}")
            article_data = scrape_article(link)
            if article_data:
                article_data["Sección"] = section_name
                all_news.append(article_data)

    driver.quit()

    # Guardar resultados
    if all_news:
        df = pd.DataFrame(all_news)
        df.to_csv("output/noticias_diario_popular.csv", index=False, encoding="utf-8-sig")
        print("Scraping completado. Datos guardados en 'noticias_diario_popular.csv'.")
    else:
        print("No se encontraron noticias para guardar.")

if __name__ == "__main__":
    main()
