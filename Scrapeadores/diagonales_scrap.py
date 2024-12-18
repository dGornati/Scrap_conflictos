import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def configure_driver():
    """Configura el driver de Selenium."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def wait_for_element(driver, by, selector, timeout=10):
    """Espera dinámica para la presencia de un elemento."""
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, selector)))

def click_if_present(driver, selector):
    """Haz clic en un botón si está presente."""
    try:
        button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
        button.click()
        print("Botón 'No gracias' clickeado.")
    except Exception:
        print("Botón 'No gracias' no encontrado.")

def scrape_section(driver, section_url, max_pages=2):
    """Extrae enlaces de noticias y recorre la paginación."""
    driver.get(section_url)
    all_links = []

    for page_number in range(max_pages):
        print(f"\nCargando página {page_number + 1} de {section_url}...")
        time.sleep(5)  # Esperar 5 segundos para cargar contenido dinámico

        # Cerrar popup si aparece
        click_if_present(driver, ".dismiss")

        # Diagnóstico: Imprimir todos los enlaces <a> encontrados
        print("\nDiagnóstico de enlaces <a> encontrados en la página:")
        all_a_tags = driver.find_elements(By.TAG_NAME, "a")
        for tag in all_a_tags:
            print(f"Texto: {tag.text}, Href: {tag.get_attribute('href')}")

        # Extraer los enlaces de noticias usando un selector más general
        articles = driver.find_elements(By.CSS_SELECTOR, "a")
        links = [{"title": article.text, "href": article.get_attribute("href")} for article in articles if article.get_attribute("href")]

        # Filtrar enlaces relevantes
        valid_links = [
            link for link in links
            if link['href'].startswith('http') and (
                '/municipio/' in link['href'] or '/provincia/' in link['href']
            )
        ]

        print(f"Enlaces válidos en página {page_number + 1}:")
        for link in valid_links:
            print(f"Título: {link['title']}, Href: {link['href']}")

        print(f"Página {page_number + 1}: {len(valid_links)} enlaces válidos encontrados.")
        all_links.extend(valid_links)

        # Intentar ir a la siguiente página
        try:
            next_buttons = driver.find_elements(By.CSS_SELECTOR, "li.pagination-next a")
            if next_buttons:
                next_page_url = next_buttons[0].get_attribute("href")
                driver.get(next_page_url)
            else:
                print("No se encontró el botón para la siguiente página.")
                break
        except Exception:
            print("Error navegando a la siguiente página.")
            break

    # Eliminar duplicados por URL
    return list({link['href']: link for link in all_links}.values())

def scrape_article(driver, url):
    """Extrae datos de una noticia individual."""
    if not url or not url.startswith('http'):
        print(f"URL inválida: {url}")
        return None

    driver.get(url)
    try:
        click_if_present(driver, ".dismiss")

        # Intentar obtener el título
        try:
            title = wait_for_element(driver, By.CSS_SELECTOR, ".entry-header .jeg_post_title").text.strip()
        except Exception:
            print("Título no encontrado, intentando otro selector.")
            title = driver.title.strip()

        # Obtener la fecha
        try:
            date = wait_for_element(driver, By.CSS_SELECTOR, ".article-date").text.strip()
        except Exception:
            print("Fecha no encontrada, intentando obtener texto completo del meta.")
            try:
                date_meta = driver.find_element(By.CSS_SELECTOR, ".meta_left .jeg_meta_date").text.strip()
                date = date_meta
            except Exception:
                print("Fecha no encontrada, revisando HTML de la página.")
                print(driver.page_source[:500])  # Imprime los primeros 500 caracteres del HTML
                date = ""

        # Obtener el cuerpo del artículo
        body_elements = driver.find_elements(By.CSS_SELECTOR, ".content-inner")
        body = " ".join([element.text.strip() for element in body_elements])

        if not body:
            print("Cuerpo no encontrado, intentando selector alternativo.")
            try:
                body_elements_alt = driver.find_elements(By.CSS_SELECTOR, "p")
                body = " ".join([element.text.strip() for element in body_elements_alt])
            except Exception:
                print("Cuerpo no encontrado, revisando HTML de la página.")
                print(driver.page_source[:500])  # Imprime los primeros 500 caracteres del HTML
                body = ""

        return {"URL": url, "Título": title, "Fecha": date, "Cuerpo": body}
    except Exception as e:
        print(f"Error procesando {url}: {e}")
        return None

def main():
    sections = {
        "Provincia": "https://www.diagonales.com/provincia_c6213a18b5e6cc543af488b2a",
        "Municipios": "https://www.diagonales.com/municipio_c6213a18d5e6cc543af488c51"
    }
    all_news = []

    driver = configure_driver()

    for section_name, section_url in sections.items():
        print(f"\nScrapeando sección: {section_name}")
        links = scrape_section(driver, section_url)
        print(f"Se encontraron {len(links)} enlaces en la sección {section_name}.")

        for link in links:
            article_data = scrape_article(driver, link['href'])
            if article_data:
                article_data["Sección"] = section_name
                all_news.append(article_data)

    driver.quit()

    # Guardar resultados en CSV
    if all_news:
        df = pd.DataFrame(all_news)
        df.to_csv("output/noticias_diagonales.csv", index=False, encoding="utf-8-sig")
        print("\nScraping completado. Datos guardados en 'noticias_diagonales.csv'.")
    else:
        print("\nNo se encontraron noticias para guardar.")

if __name__ == "__main__":
    main()
