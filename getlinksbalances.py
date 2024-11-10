from playwright.sync_api import sync_playwright

def get_balance_links(cuit_number, start_year=2022):
    url = f"https://www.cnv.gov.ar/SitioWeb/Empresas/Empresa/{cuit_number}?fdesde=31/12/{start_year}"
    balance_links = {
        "2022": {"Q1": None, "Q2": None, "Q3": None, "Q4": None, "Annual": None},
        "2023": {"Q1": None, "Q2": None, "Q3": None, "Q4": None, "Annual": None},
        "2024": {"Q1": None, "Q2": None, "Q3": None, "Q4": None, "Annual": None},
    }

    with sync_playwright() as p:
        # Iniciar el navegador en modo headless
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Navegar a la URL
        page.goto(url)
        print("Página cargada:", url)
        
        # Expande "Información Financiera" usando un selector específico
        try:
            info_financiera_button = page.get_by_role("button", name="Información Financiera")
            info_financiera_button.click()
            page.wait_for_timeout(1000)  # Esperar un momento para que se expanda completamente
            print("Información Financiera expandido")
        except Exception as e:
            print("Error al hacer clic en 'Información Financiera':", e)
            return []
        
        # Expande "Estados Contables" usando un selector más específico
        try:
            estados_contables_button = page.locator("#heading32_1 a")  # Cambia según el ID/clase exacto del botón
            estados_contables_button.scroll_into_view_if_needed()
            estados_contables_button.click(timeout=60000)
            page.wait_for_timeout(3000)  # Esperar más tiempo para que la tabla se cargue
            print("Estados Contables expandido")
        except Exception as e:
            print("Error al hacer clic en 'Estados Contables':", e)
            return []
        
        # Extraer los enlaces de los balances seleccionados
        rows = page.query_selector_all("tr")
        print(f"Número de filas encontradas en la tabla: {len(rows)}")

        for row in rows:
            cells = row.query_selector_all("td")
            if len(cells) > 2:
                description = cells[2].inner_text().strip()
                date_text = cells[0].inner_text().strip()
                
                # Identificar el año y la fecha de cierre
                if "FECHA CIERRE" in description and "NIIF" in description:
                    link_tag = row.query_selector("a[href*='publicview']")
                    if link_tag:
                        href = link_tag.get_attribute("href")
                        if "CONSOLIDADO" in description or "INDIVIDUAL" in description:
                            # Usamos solo el mes para identificar el trimestre
                            if "-03-" in description:
                                quarter = "Q1"
                            elif "-06-" in description:
                                quarter = "Q2"
                            elif "-09-" in description:
                                quarter = "Q3"
                            elif "-12-" in description:
                                quarter = "Q4"
                                if "PERIODICIDAD: 1" in description:
                                    quarter = "Annual"
                            else:
                                continue  # No es una fecha de cierre que necesitamos

                            # Extraer el año de la fecha
                            year = date_text.split()[-1]
                            if year in balance_links and balance_links[year][quarter] is None:
                                balance_links[year][quarter] = href
                                print(f"Enlace encontrado para {year} {quarter}: {href}")
        
        browser.close()
        print("Enlaces de balances seleccionados:", balance_links)
        return balance_links

# Ejemplo de uso:
cuit_number = "30503087967"  # Reemplaza con el CUIT deseado
balance_links = get_balance_links(cuit_number)

# Mostrar los enlaces de los balances consolidados y trimestrales
for year, quarters in balance_links.items():
    print(f"Año {year}:")
    for quarter, link in quarters.items():
        if link:
            print(f"  {quarter}: {link}")
        else:
            print(f"  {quarter}: No disponible")