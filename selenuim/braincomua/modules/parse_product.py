import os
import sys
import django
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from load_django import *

from parser_app.models import Product

url = "https://brain.com.ua/Mobilniy_telefon_Apple_iPhone_15_128GB_Black-p1044347.html"
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(), options=options)
driver.get(url)
driver.implicitly_wait(10)

try:
    button = driver.find_element(By.XPATH, "//button[contains(@class,'br-prs-button') and span[text()='Всі характеристики']]")
    driver.execute_script("arguments[0].click();", button)
    sleep(1)
except:
    pass

spans = driver.find_elements(By.CSS_SELECTOR, "div.br-pr-chr-item span")
texts = [s.text.strip().replace("\xa0", " ") for s in spans if s.text.strip()]
description = {texts[i]: texts[i+1] if i+1 < len(texts) else "" for i in range(0, len(texts), 2)}

title = driver.find_element(By.CSS_SELECTOR, "h1.main-title").text.strip()
color = description.get("Колір", "")
memory = description.get("Вбудована пам'ять", "")
art = description.get("Артикул", "")
diagonal = description.get("Діагональ екрану", "")
display = description.get("Роздільна здатність екрану", "")
producer = description.get("Виробник", "")

price = int(driver.find_element(By.CSS_SELECTOR, "div.br-pr-price.main-price-block span").text.strip().replace(" ", ""))
try:
    red_price = driver.find_element(By.CSS_SELECTOR, "span.red-price").text.strip()
except:
    red_price = None

try:
    comment_count_elem = driver.find_element(By.XPATH, "//a[@class='scroll-to-element reviews-count']/span")
    comment_count = comment_count_elem.get_attribute("textContent")
except:
    comment_count = 0

imgs = driver.find_elements(By.CSS_SELECTOR, "img.br-main-img")
images = [img.get_attribute("src") for img in imgs]

current_product = driver.execute_script("return window.CURRENT_PRODUCT;")

product_code = current_product["ProductCode"]

driver.quit()

product, created = Product.objects.get_or_create(
    product_code=product_code,
    title=title,
    price=price,
    red_price = red_price,
    color=color,
    memory=memory,
    art=art,
    diagonal=diagonal,
    display=display,
    producer=producer,
    images = images,
    comment_count = comment_count,
    description = description

)

print(f"Save in db: {product.title} (created={created}) {producer}" )
