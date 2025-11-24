import os
import sys
import django
import asyncio
from playwright.async_api import async_playwright
from asgiref.sync import sync_to_async

from load_django import *
from parser_app.models import Product


async def parse(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(url)

        title = (await page.inner_text("h1.main-title")).strip()
        comment_count_raw = (await page.inner_text("a.reviews-count span")).strip()
        comment_count = int(comment_count_raw) if comment_count_raw.isdigit() else 0
        product_code = (await page.inner_text("span.br-pr-code-val")).strip()
        price = int((await page.inner_text("div.main-price-block span")).replace(" ", ""))

        try:
            red_price = int((await page.inner_text("span.red-price")).replace(" ", ""))
        except:
            red_price = 0

        img_elements = await page.query_selector_all("img.br-main-img")
        images = [await img.get_attribute("src") for img in img_elements]

        spans = await page.query_selector_all("div.br-pr-chr-item span")
        texts = []
        for s in spans:
            text = (await s.inner_text()).strip()
            if text:
                text = " ".join(text.replace("\xa0", " ").split())
                texts.append(text)

        description = {}
        for i in range(0, len(texts), 2):
            key = texts[i]
            value = texts[i + 1] if i + 1 < len(texts) else ""
            description[key] = value

        color = description.get("Колір", "")
        memory = description.get("Вбудована пам'ять", "")
        art = description.get("Артикул", "")
        diagonal = description.get("Діагональ екрану", "")
        display = description.get("Роздільна здатність екрану", "")
        producer = description.get("Виробник", "")

        await sync_to_async(Product.objects.create)(
            title=title,
            producer=producer,
            comment_count=comment_count,
            product_code=product_code,
            price=price,
            red_price=red_price,
            images=images,
            color=color,
            memory=memory,
            art=art,
            diagonal=diagonal,
            display=display,
            description=description,
        )

        print("Save in db", title)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(parse("https://brain.com.ua/Mobilniy_telefon_Apple_iPhone_15_128GB_Black-p1044347.html"))
