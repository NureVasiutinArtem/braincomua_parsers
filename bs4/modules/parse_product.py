import os
import sys
import django
import requests
from bs4 import BeautifulSoup
from decimal import Decimal
from pprint import pprint
from load_django import *
from parser_app.models import *

url = "https://brain.com.ua/Mobilniy_telefon_Apple_iPhone_16_Pro_Max_256GB_Black_Titanium-p1145443.html"
headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/142.0.0.0 Mobile Safari/537.36"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# Collect all spans for characteristics
spans = soup.select("div.br-pr-chr-item span")
texts = []
for s in spans:
    text = s.get_text(strip=True)
    if text:
        text = " ".join(text.replace("\xa0", " ").split())
        texts.append(text)

# Build a description dictionary
description = {}
for i in range(0, len(texts), 2):
    key = texts[i]
    value = texts[i + 1] if i + 1 < len(texts) else ""
    description[key] = value

# Function to safely extract characteristics
def safe_text(label):
    """
    Try to get the value for a given characteristic label.
    Handles different exceptions with explanations.
    """
    try:
        parent = soup.find("span", string=label)
        if not parent:
            raise ValueError(f"'{label}' not found")  # Label missing

        sibling = parent.find_next_sibling("span")
        if not sibling:
            raise IndexError(f"Sibling span for '{label}' not found")  # Unexpected structure

        return " ".join(sibling.get_text(strip=True).replace("\xa0", " ").split())

    except IndexError:
        print(f"Problem: Unexpected structure in '{label}' (sibling span missing)")
        return None
    except AttributeError:
        print(f"Problem: Attribute error while processing '{label}'")
        return None
    except ValueError as ve:
        print(f"Problem: {ve}")
        return None
    except Exception as e:
        print(f"Problem: Unknown error while processing '{label}': {e}")
        return None

# Extract main product info
try:
    title = soup.select_one("h1.main-title").get_text(strip=True)
except AttributeError:
    print("Problem: Title not found")
    title = None

try:
    price_text = soup.select_one("div.br-pr-price.main-price-block span").get_text(strip=True)
    price = Decimal(price_text.replace(" ", "").replace("₴", ""))
except AttributeError:
    print("Problem: Price not found")
    price = None

try:
    red_price_tag = soup.select_one("span.red-price")
    red_price = Decimal(red_price_tag.get_text(strip=True).replace(" ", "").replace("₴", "")) if red_price_tag else None
except AttributeError:
    print("Problem: Red price not found")
    red_price = None

try:
    product_code = soup.select_one("span.br-pr-code-val").get_text(strip=True)
except AttributeError:
    print("Problem: Product code not found")
    product_code = None

# Images
try:
    imgs = soup.find_all("img", class_="br-main-img")
    images = [img.get("src") for img in imgs]
except Exception:
    print("Problem: Images not found")
    images = None

# Comment count
try:
    comment_count_tag = soup.select_one("a.scroll-to-element.reviews-count span")
    comment_count = int(comment_count_tag.get_text(strip=True)) if comment_count_tag else 0
except Exception:
    print("Problem: Comment count not found")
    comment_count = None

# Extract characteristics using safe_text
color = safe_text("Колір")
memory = safe_text("Вбудована пам'ять")
art = safe_text("Артикул")
diagonal = safe_text("Діагональ екрану")
display = safe_text("Роздільна здатність екрану")
producer = safe_text("Виробник")



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

# Save to DB
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
pprint(product)