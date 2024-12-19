import subprocess

scripts = ['Scrapeadores/apify_scrap.py',
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
           'merge_diario.py']

for script in scripts:
    result = subprocess.run(['python', script], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running {script}:")
        print(result.stderr)
    else:
        print(f"Successfully ran {script}:")
        print(result.stdout)
