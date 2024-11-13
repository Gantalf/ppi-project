import os
import re
from datetime import datetime
from playwright.sync_api import sync_playwright

def determine_quarter(date):
    if date.month in [1, 2, 3]:
        return "Q1"
    elif date.month in [4, 5, 6]:
        return "Q2"
    elif date.month in [7, 8, 9]:
        return "Q3"
    elif date.month in [10, 11, 12]:
        return "Q4"

def get_balance_links(cuit_number, start_year=2022):
    url = f"https://www.cnv.gov.ar/SitioWeb/Empresas/Empresa/{cuit_number}?fdesde=31/12/{start_year}"
    balance_links = {}

    fecha_cierre_regex = re.compile(r"FECHA CIERRE: (\d{4}-\d{2}-\d{2})")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        page.goto(url)
        print("Página cargada:", url)
        
        # Expande "Información Financiera"
        try:
            info_financiera_button = page.get_by_role("button", name="Información Financiera")
            info_financiera_button.click()
            page.wait_for_timeout(1000)
            print("Información Financiera expandido")
        except Exception as e:
            print("Error al hacer clic en 'Información Financiera':", e)
            return {}
        
        # Expande "Estados Contables"
        try:
            estados_contables_button = page.locator("#heading32_1 a")
            estados_contables_button.scroll_into_view_if_needed()
            estados_contables_button.click(timeout=60000)
            page.wait_for_timeout(3000)
            print("Estados Contables expandido")
        except Exception as e:
            print("Error al hacer clic en 'Estados Contables':", e)
            return {}
        
        # Extraer los enlaces de los balances seleccionados
        rows = page.query_selector_all("tr")
        print(f"Número de filas encontradas en la tabla: {len(rows)}")

        for row in rows:
            try:
                cells = row.query_selector_all("td")
                if not cells or len(cells) < 3:
                    continue

                descripcion_text = cells[2].inner_text().strip()

                # Filtrar solo las descripciones que contienen "BALANCE"
                if "BALANCE" not in descripcion_text.upper():
                    print(f"Descripción ignorada (no es un balance): '{descripcion_text}'")
                    continue

                # Extraer la fecha de cierre de la descripción
                fecha_cierre_match = fecha_cierre_regex.search(descripcion_text)

                if fecha_cierre_match:
                    fecha_cierre_str = fecha_cierre_match.group(1)
                    
                    # Convertir la fecha de cierre a un objeto datetime
                    cierre_date = datetime.strptime(fecha_cierre_str, "%Y-%m-%d")
                    
                    # Obtener el año y el trimestre en base a la fecha de cierre
                    year = cierre_date.year
                    quarter = determine_quarter(cierre_date)
                    
                    # Asignar el enlace al trimestre y año correspondiente en balance_links
                    if str(year) not in balance_links:
                        balance_links[str(year)] = {"Q1": None, "Q2": None, "Q3": None, "Q4": None, "Annual": None}

                    if balance_links[str(year)].get(quarter) is None:
                        link_tag = row.query_selector("a[href*='publicview']")
                        if link_tag:
                            href = link_tag.get_attribute("href")
                            balance_links[str(year)][quarter] = href
                            print(f"Enlace encontrado para {year} {quarter}: {href}")
                else:
                    print(f"No se encontró una fecha de cierre en la descripción: '{descripcion_text}'")
            except Exception as e:
                print(f"Error al procesar una fila: {e}")
        
        browser.close()
        return balance_links

def get_pdf_from_balance_page(balance_links, name_company):
    pdf_links = {}
    download_directory = "./downloads"  # Carpeta para guardar los archivos descargados
    os.makedirs(download_directory, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(accept_downloads=True)  # Acepta automáticamente las descargas
        
        for year, quarters in balance_links.items():
            pdf_links[year] = {}
            for quarter, link in quarters.items():
                if link is None:
                    continue
                
                page = context.new_page()
                try:
                    page.goto(link)
                    page.wait_for_timeout(2000)
                    print(f"Navegando a la página del balance {year} {quarter}: {link}")
                    
                    # Cierra el modal si está abierto
                    modal = page.query_selector("div#myModal[aria-hidden='false']")
                    if modal:
                        close_button = modal.query_selector("button.close")
                        if close_button:
                            close_button.click()
                            page.wait_for_timeout(1000)
                            print("Modal cerrado.")

                    adjuntos_dropdown = page.query_selector("text=Adjuntos")
                    if adjuntos_dropdown:
                        adjuntos_dropdown.click()
                        page.wait_for_timeout(1000)
                        
                        with page.expect_download() as download_info:
                            download_button = page.query_selector(".icon-cloud-download")
                            if download_button:
                                download_button.click()
                                print(f"Descarga iniciada para {year} {quarter}")
                            else:
                                print(f"No se encontró el botón de descarga para {year} {quarter}")
                        download = download_info.value
                        
                        file_path = os.path.join(download_directory, f"{name_company}_{year}_{quarter}_Balance.pdf")
                        download.save_as(file_path)
                        print(f"Archivo descargado y guardado en: {file_path}")
                        
                        pdf_links[year][quarter] = file_path
                    
                    else:
                        print(f"No se encontró la sección 'Adjuntos' en {year} {quarter}. Cerrando pestaña y continuando.")
                        page.close()
                        continue  # Salta al siguiente enlace
                
                except Exception as e:
                    print(f"Error al procesar el enlace para {year} {quarter}: {e}")
                
                finally:
                    if not page.is_closed():
                        page.close()
        
        browser.close()
        return pdf_links


# Ejemplo de uso:
cuit_number = "30503087967"  # Reemplaza con el CUIT deseado
balance_links = get_balance_links(cuit_number)

pdf_links = get_pdf_from_balance_page(balance_links)

# Mostrar las rutas de los archivos PDF de los balances seleccionados
for period, path in pdf_links.items():
    print(f"{period}: {path}")
