from apify_client import ApifyClient
import pandas as pd
from datetime import datetime

# Inicializar el cliente de Apify
apify_client = ApifyClient('apify_api_MerASlR9HihdmDHyM9E75rmnOAv1Fi4qhDjM')

# Ejecutar el actor y obtener los resultados
actor_call = apify_client.actor('endearing_pigeon/article-extractor-BsAs').call()

# Obtener los datos del dataset
dataset_items = apify_client.dataset(actor_call['defaultDatasetId']).list_items().items

# Crear un DataFrame con los datos
current_date = datetime.now().strftime('%d/%m/%Y')
df = pd.DataFrame(dataset_items)

# Seleccionar y renombrar las columnas, además de agregar la columna Fecha
noticias = df[['title', 'text', 'url']].copy()
noticias.columns = ['Título', 'Cuerpo', 'URL']  # Renombrar columnas
noticias['Fecha'] = current_date  # Agregar la columna Fecha

# Guardar el resultado en un archivo CSV
noticias.to_csv("output/noticias_apify.csv", index=False, encoding="utf-8-sig")


