import os
import sys
import django
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from pprint import pprint
from load_django import *
from parser_app.models import Product

def safe_text(driver, label):
    try:
        # Find parent div containing the label span
        parent = driver.find_element(
            By.XPATH,
            f"//span[contains(normalize-space(text()), '{label}')]/.."
        )
        # Find the first span that is not the label itself
        value_span = parent.find_element(
            By.XPATH,
            f".//span[not(contains(normalize-space(text()), '{label}'))]"
        )
        return value_span.text.strip()
    except NoSuchElementException:
        print(f"Problem: '{label}' field not found (NoSuchElementException)")
        return None
    except WebDriverException:
        print(f"Problem: WebDriver exception while processing '{label}'")
        return None
    except AttributeError:
        print(f"Problem: Attribute error while processing '{label}'")
        return None
    except IndexError:
        print(f"Problem: Sibling span for '{label}' not found")
        return None


url = "https://brain.com.ua/Mobilniy_telefon_Apple_iPhone_15_128GB_Black-p1044347.html"

options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(), options=options)
driver.get(url)
driver.implicitly_wait(10)

# Click "All characteristics" button if exists
try:
    button = driver.find_element(
        By.XPATH, "//button[contains(@class,'br-prs-button') and span[text()='Всі характеристики']]"
    )
    driver.execute_script("arguments[0].click();", button)
    sleep(1)
except NoSuchElementException:
    print("Problem: 'All characteristics' button not found")
except WebDriverException:
    print("Problem: WebDriver exception while clicking 'All characteristics' button")

# TITLE
try:
    title = driver.find_element(By.XPATH, "//h1[contains(@class,'main-title')]").text.strip()
except NoSuchElementException:
    title = ""
    print("Problem: Page title not found")
except AttributeError:
    title = ""
    print("Problem: Attribute error while retrieving title")

# COMMENT COUNT
try:
    comment_count_elem = driver.find_element(By.XPATH, "//a[@class='scroll-to-element reviews-count']/span")
    comment_count = int(comment_count_elem.text.strip()) if comment_count_elem.text.strip().isdigit() else 0
except NoSuchElementException:
    comment_count = None
    print("Problem: Comments count not found")
except ValueError:
    comment_count = None
    print("Problem: Comments count is not a number")
except AttributeError:
    comment_count = None
    print("Problem: Attribute error while retrieving comments count")

# PRODUCT CODE
try:
    product_code_elem = driver.execute_script("return window.CURRENT_PRODUCT.ProductCode;")
    product_code = str(product_code_elem).strip()
except KeyError:
    product_code = None
    print("Problem: Product code not found in CURRENT_PRODUCT")
except AttributeError:
    product_code = None
    print("Problem: Attribute error while retrieving product code")

# PRICE
try:
    price_raw = driver.find_element(By.XPATH, "//div[contains(@class,'main-price-block')]//span").text.strip()
    price = int(price_raw.replace(" ", ""))
except NoSuchElementException:
    price = None
    print("Problem: Price not found")
except ValueError:
    price = None
    print("Problem: Price is not a valid number")
except AttributeError:
    price = None
    print("Problem: Attribute error while retrieving price")

# RED PRICE
try:
    red_price_raw = driver.find_element(By.XPATH, "//span[contains(@class,'red-price')]").text.strip()
    red_price = int(red_price_raw.replace(" ", ""))
except NoSuchElementException:
    red_price = None
    print("Problem: Red price not found")
except ValueError:
    red_price = None
    print("Problem: Red price is not a valid number")
except AttributeError:
    red_price = None
    print("Problem: Attribute error while retrieving red price")

# IMAGES
images = []
try:
    img_elements = driver.find_elements(By.XPATH, "//img[contains(@class,'br-main-img')]")
    for img in img_elements:
        src = img.get_attribute("src")
        if src:
            images.append(src)
except NoSuchElementException:
    print("Problem: Images not found")
except AttributeError:
    print("Problem: Attribute error while retrieving images")

description = {}

description_elements = driver.find_elements(By.XPATH, '//div[@class="br-pr-chr-item"]//span')

texts = [el.text.strip() for el in description_elements if el.text.strip()]

for i in range(0, len(texts), 2):
    key = texts[i]
    value = texts[i + 1] if i + 1 < len(texts) else ""
    description[key] = value

print()
pprint(description)
print()

# DESCRIPTION and specific fields
color = safe_text(driver, "Колір")
producer = safe_text(driver, "Виробник")
art = safe_text(driver, "Артикул")
diagonal = safe_text(driver, "Діагональ екрану")
display = safe_text(driver, "Роздільна здатність екрану")
memory = safe_text(driver, "Вбудована пам")


data = {
    "product_code": product_code,
    "title": title,
    "price": price,
    "red_price": red_price,
    "color": color,
    "memory": memory,
    "art": art,
    "diagonal": diagonal,
    "display": display,
    "producer": producer,
    "images": images,
    "comment_count": comment_count,
    
}

pprint(data)

# Create or get product in Django
product, created = Product.objects.get_or_create(
    product_code=product_code,
    title=title,
    price=price,
    red_price=red_price,
    color=color,
    memory=memory,
    art=art,
    diagonal=diagonal,
    display=display,
    producer=producer,
    images=images,
    comment_count=comment_count,
    description=description

)


print(f"Save in db: {product.title} (created={created}) {producer}")

driver.quit()
