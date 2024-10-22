from selenium import webdriver
from selenium.webdriver.chrome.service import Service  # Importa Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def buscar_empresa(nombre_empresa, fecha_desde="08/11/2023", fecha_hasta="30/06/2024"):
    # Ruta al ChromeDriver (ajusta esta ruta si es necesario)
    service = Service('/usr/local/bin/chrome-mac-x64')

    # Inicializa el navegador Chrome con la nueva clase Service
    driver = webdriver.Chrome(service=service)

    # Abre la página de búsqueda de la CNV
    driver.get("https://www.cnv.gov.ar/SitioWeb/Empresas")

    # Espera a que el input de nombre de empresa esté presente
    buscador = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "nombreempresa"))
    )

    # Ingresa el nombre de la empresa
    buscador.send_keys(nombre_empresa)

    # Ingresa la fecha desde
    fecha_desde_input = driver.find_element(By.ID, "desde")
    fecha_desde_input.clear()  # Limpia el input por si tiene valores previos
    fecha_desde_input.send_keys(fecha_desde)

    # Ingresa la fecha hasta
    fecha_hasta_input = driver.find_element(By.ID, "hasta")
    fecha_hasta_input.clear()
    fecha_hasta_input.send_keys(fecha_hasta)

    # Hacer clic en el botón de "BUSCAR"
    boton_buscar = driver.find_element(By.ID, "ancla1")  # Selector por ID
    boton_buscar.click()

    # Esperar a que la página se recargue
    time.sleep(5)

    # Obtener la URL actual (con el ID de la empresa y fechas)
    url_actual = driver.current_url
    print(f"Navegando a: {url_actual}")

    # Accede a la URL con los parámetros correctos
    driver.get(url_actual)

    # Espera a que el dropdown "ESTADOS CONTABLES" esté presente y haz clic
    try:
        estados_contables = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'ESTADOS CONTABLES')]"))
        )
        estados_contables.click()
        time.sleep(2)  # Espera para que se despliegue el contenido

        # Buscar todos los enlaces a PDFs dentro de "ESTADOS CONTABLES"
        documentos = driver.find_elements(By.CLASS_NAME, "btn-xs")
        for doc in documentos:
            enlace = doc.get_attribute("href")
            print(f"Documento PDF encontrado: {enlace}")

    except Exception as e:
        print(f"Error al buscar los documentos: {e}")

    finally:
        # Cierra el navegador
        driver.quit()

# Prueba la función con una empresa
buscar_empresa("YPF")