import subprocess
import os
import sys

def install_requirements(script_path):
    """Genera un requirements.txt y lo instala antes de ejecutar el script."""
    temp_req_file = "temp_requirements.txt"
    try:
        # Generar el requirements.txt temporal
        subprocess.run([sys.executable, "-m", "pip", "install", "pipreqs"], check=True)
        subprocess.run(["pipreqs", os.path.dirname(script_path), "--force", "--savepath", temp_req_file], check=True)
        
        # Instalar las dependencias si el archivo no está vacío
        if os.path.exists(temp_req_file) and os.path.getsize(temp_req_file) > 0:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", temp_req_file], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies for {script_path}: {e}")
    finally:
        # Eliminar el archivo temporal
        if os.path.exists(temp_req_file):
            os.remove(temp_req_file)

scripts = [
    'Scrapeadores/apify_scrap.py',
    'Scrapeadores/ate_scrap.py', 
    'Scrapeadores/cuatrovientos_scrap.py',
    'Scrapeadores/diagonales_scrap.py',
    'Scrapeadores/dib_scrap.py',
    'Scrapeadores/editorplatense_scrap.py',
    'Scrapeadores/elsol_scrap.py',
    'Scrapeadores/eltermometro_scrap.py',
    'Scrapeadores/infocielo_scrap.py',
    'Scrapeadores/lacapitalmdp_scrap.py',
    'Scrapeadores/lavozdetandil_scrap.py',
    'Scrapeadores/lavozdezarate_scrap.py',
    'Scrapeadores/popular_scrap.py',
    'Scrapeadores/quedigital_scrap.py',
    'merge_diario.py'
]

for script in scripts:
    print(f"Processing {script}...")
    install_requirements(script)
    
    result = subprocess.run([sys.executable, script], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running {script}:")
        print(result.stderr)
    else:
        print(f"Successfully ran {script}:")
        print(result.stdout)
