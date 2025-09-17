'''Este modulo se encarga de extraer informacion de pordutos desde el sitio web
de sephora utilizando selenium Webdriver. incluye funciones para inicilizar el navegador,
esperar elementos y realizar scraping de datos relevantes'''

import os 
from time import sleep
import csv
import requests
from PIL import Image
import io
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

headers = {
    "user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
}

def hacer_scrolling(driver,steep=500, pause=0.5,
                      max_cycle=700,max_no_growth=6):
    '''Esta funcion fue diseñada para hacer 
    scrolling suave a la pagania de shepora'''
    last_height = driver.execute_script('return document.body.scrollHeight')
    no_growth= 0
    for _ in range(max_cycle):
        for _ in range(10):
            driver.execute_script(f'window.scrollBy(0,{steep})')
            sleep(pause)
        new_height = driver.execute_script('return document.body.scrollHeight')
        if new_height == last_height:
            no_growth += 1
            if no_growth == max_no_growth:
                break
        else:
            no_growth = 0
            last_height = new_height
            try:
                show_more_product = WebDriverWait(driver,10).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[@class="css-wmvz6v e15t7owz0"]'))
                )
                driver.execute_script('arguments[0].click();',show_more_product)
            except Exception as e:
                print(f'Existe:{e}')

def cerrar_disclaimer(driver):
    """Cierra las ventanas emergentes (popups) de Sephora.
    Parámetros:
    driver (webdriver): Instancia activa del navegador Selenium."""
    for _ in range(0,2):
        try:
            close = WebDriverWait(driver, 10).until(
                              EC.element_to_be_clickable((By.XPATH,'//button[@data-at="modal_close" or @data-at="close_button"]'))
            )
            close.click()
            sleep(5)
        except Exception as e:
            print(f'no se encontro disclaimer:{e}')
            



opts =Options()
opts.add_argument("""user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)
                  AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36""")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
URL= 'https://www.sephora.com/search?keyword=blush'
driver.get(URL)
sleep(0.3)
cerrar_disclaimer(driver)

hacer_scrolling(driver)

with open('sephora.csv', 'w', encoding='UTF-8', newline="") as archivo:
    writer = csv.writer(archivo)
    writer.writerow(["brand", "product_name", "shades", "price", "size", "rating", "reviews_count", "product_url", "image_path"])
# pylint: disable=invalid-name


    links_productos = WebDriverWait(driver,10).until(
    EC.presence_of_all_elements_located((By.XPATH, ('//a[@class="css-11s14hs"]'))))
    print(f'encontre:{len(links_productos)}')
    links_paginas = []
    for tag_a in links_productos:
        links_paginas.append(tag_a.get_attribute("href"))
    i=0
    os.makedirs('./imagenes/', exist_ok=True)
    for link in links_paginas:
        driver.get(link)
        cerrar_disclaimer(driver)
        button = driver.find_element(By.XPATH, './/button[@data-at="list_btn"]')
        button.click()
        sleep(3)
        hacer_scrolling(driver)
        brand = driver.find_element(By.XPATH, './/a[@data-at="brand_name"]').text
        print(brand)
        product_name = driver.find_element(By.XPATH, './/span[@data-at="product_name"]').text
        print(product_name)
        shades_elements = driver.find_elements(By.XPATH, './/div[@data-at="color_swatch_name"]')
        shades = [s.text for s in shades_elements ]
        price = driver.find_element(By.XPATH, './/span[@class="css-18jtttk"]/b').text
        print(price)
        size = driver.find_element(By.XPATH,
                                        './/div[@class="css-1wc0aja e15t7owz0"]/div/span').text
        print(size)
        try:
            rating = driver.find_element(By.XPATH, './/div[@class="css-b75h2m e15t7owz0"]/span').text
            print(rating)
            reviews_count = driver.find_element(By.XPATH,
                                                './/div[@class="css-7fwc8e e15t7owz0"]/span').text
            print(reviews_count)                                  
        except:
            rating, reviews_count= None, None


        imagen_url = driver.find_element(By.XPATH,'//picture[@class="css-yq9732"]/img')
        imagen_url = imagen_url.get_attribute('src')
        try:
            imagen_content = requests.get(url=imagen_url,headers=headers, timeout= 2).content
        except Exception as e:
            print('Error al descargar imagen{e}')
            continue
        try:
            image_file = io.BytesIO(imagen_content)
            imagen = Image.open(image_file).convert("RGB")
            path = './imagenes/' + str(i) + '.jpg'
            with open(path,'wb') as f:
                imagen.save(f,'JPEG', quality=85)
        except Exception as e:
            print('ERROR')
        i+=1
        writer.writerow([brand, product_name, ', '.join(shades), price, size, rating, reviews_count, path])
        