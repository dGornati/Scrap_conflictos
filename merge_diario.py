import os
import pandas as pd
from datetime import datetime, timedelta

# Definir las rutas de las carpetas
input_folder = "output"
output_folder = "conflictos_diarios"

# Obtener la fecha actual en formato "YYYY-MM-DD"
current_date = datetime.now().strftime("%Y-%m-%d")
# Obtener la fecha del día anterior en formato "YYYY-MM-DD"
previous_date = (datetime.now() - timedelta(1)).strftime("%Y-%m-%d")

# Nombre del archivo de salida
output_file = os.path.join(output_folder, f"{current_date}_buenos_aires.csv")
# Nombre del archivo del día anterior
previous_file = os.path.join(output_folder, f"{previous_date}_buenos_aires.csv")

# Crear la carpeta de salida si no existe
os.makedirs(output_folder, exist_ok=True)

# Listar todos los archivos CSV en la carpeta "output"
csv_files = [file for file in os.listdir(input_folder) if file.endswith(".csv")]

# Leer y combinar todos los archivos CSV
dataframes = []
for csv_file in csv_files:
    file_path = os.path.join(input_folder, csv_file)
    df = pd.read_csv(file_path)
    dataframes.append(df)

# Concatenar todos los DataFrames
if dataframes:
    combined_df = pd.concat(dataframes, ignore_index=True)
    
    # Leer el archivo del día anterior si existe
    if os.path.exists(previous_file):
        previous_df = pd.read_csv(previous_file)
        # Eliminar las filas que ya existen en el archivo del día anterior
        combined_df = combined_df[~combined_df.isin(previous_df.to_dict('list')).all(axis=1)]
    
    # Seleccionar solo las columnas deseadas
    combined_df = combined_df[['Título', 'Fecha', 'Cuerpo', 'URL']]
    
    # Eliminar duplicados
    combined_df.drop_duplicates(inplace=True)
    
    # Guardar el DataFrame combinado en el archivo de salida
    combined_df.to_csv(output_file, index=False, encoding="utf-8")
    print(f"Archivo combinado guardado en: {output_file}")
else:
    print("No se encontraron archivos CSV en la carpeta 'output'.")