import os
import sys
import django
import requests
from bs4 import BeautifulSoup
from decimal import Decimal
import pprint
from load_django import *
from parser_app.models import Product


# def parse_product(url: str):
url = "https://brain.com.ua/Mobilniy_telefon_Apple_iPhone_16_Pro_Max_256GB_Black_Titanium-p1145443.html"
headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/142.0.0.0 Mobile Safari/537.36"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")


spans = soup.select("div.br-pr-chr-item span")

texts = []
for s in spans:
    text = s.get_text(strip=True)
    if text:
        text = " ".join(text.replace("\xa0", " ").split())
        texts.append(text)

description = {}
for i in range(0, len(texts), 2):
    key = texts[i]
    value = texts[i+1] if i+1 < len(texts) else ""
    description[key] = value

title = soup.select_one("h1.main-title").get_text(strip=True)

price_text = soup.select_one("div.br-pr-price.main-price-block span").get_text(strip=True)
price = Decimal(price_text.replace(" ", "").replace("₴", ""))

red_price_tag = soup.select_one("span.red-price")
if red_price_tag:
    red_price = Decimal(red_price_tag.get_text(strip=True).replace(" ", "").replace("₴", ""))
else:
    red_price = None

product_code = soup.select_one("span.br-pr-code-val").get_text(strip=True)


imgs = soup.find_all("img", class_="br-main-img")
images = [img.get("src") for img in imgs]

comment_count_tag = soup.select_one("a.scroll-to-element.reviews-count span")
comment_count = int(comment_count_tag.get_text(strip=True)) if comment_count_tag else 0

color = description.get("Колір", "")
memory = description.get("Вбудована пам'ять", "")
art = description.get("Артикул", "")
diagonal = description.get("Діагональ екрану", "")
display = description.get("Роздільна здатність екрану", "")
producer = description.get("Виробник", "")

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

# return product
print(f"Save in db: {product.title} (created={created}) {producer}" )
pprint.pprint(product)