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

def scroll_to_load_all():
    """Scroll hacia el final de la página para cargar todo el contenido."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Espera para cargar contenido dinámico
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def scrape_links():
    """Extrae los enlaces de noticias desde la página principal."""
    url = "https://eltermometroweb.com/"
    driver.get(url)
    scroll_to_load_all()

    # Extraer los enlaces de noticias
    wait_for_element(driver, By.CSS_SELECTOR, ".jeg_post_title a")
    articles = driver.find_elements(By.CSS_SELECTOR, ".jeg_post_title a")
    article_links = list(set([article.get_attribute("href") for article in articles if article.get_attribute("href")]))

    print(f"Enlaces únicos extraídos: {len(article_links)}")
    return article_links

def scrape_article(link):
    """Extrae los datos de una noticia específica."""
    driver.get(link)
    try:
        wait_for_element(driver, By.CSS_SELECTOR, ".entry-header .jeg_post_title")
        title = driver.find_element(By.CSS_SELECTOR, ".entry-header .jeg_post_title").text.strip()
        date = driver.find_element(By.CSS_SELECTOR, ".meta_left .jeg_meta_date a").text.strip()
        body_elements = driver.find_elements(By.CSS_SELECTOR, ".content-inner")
        body = " ".join([element.text.strip() for element in body_elements if element.text.strip()])
        return {"Título": title, "Fecha": date, "Cuerpo": body, "URL": link}
    except Exception as e:
        print(f"Error procesando {link}: {e}")
        return None

def main():
    print("Scrapeando El Termómetro...")
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
        df.to_csv("output/noticias_eltermometro.csv", index=False, encoding="utf-8-sig")
        print("Scraping completado. Datos guardados en 'noticias_eltermometro.csv'.")
    else:
        print("No se encontraron noticias para guardar.")

if __name__ == "__main__":
    main()
