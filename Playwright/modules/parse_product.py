import os
import sys
import django
import asyncio
from playwright.async_api import async_playwright, Error as PlaywrightError
from asgiref.sync import sync_to_async
from load_django import *
from parser_app.models import Product


# Custom exception to mimic Selenium's NoSuchElementException
class NoSuchElementException(Exception):
    pass


async def parse(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(url)

        # TITLE
        try:
            title = (await page.inner_text("//h1[contains(@class,'main-title')]")).strip()
        except:
            title = None

        # COMMENT COUNT
        try:
            comment_count_raw = (await page.inner_text("//a[contains(@class,'reviews-count')]//span")).strip()
            comment_count = int(comment_count_raw) if comment_count_raw.isdigit() else 0
        except:
            comment_count = 0

        # PRODUCT CODE
        try:
            product_code = (await page.inner_text("//span[contains(@class,'br-pr-code-val')]")).strip()
        except:
            product_code = None

        # PRICE
        try:
            price_raw = await page.inner_text("(//div[contains(@class,'main-price-block')]//span)[1]")
            price = int(price_raw.replace(" ", ""))
        except:
            price = None

        # RED PRICE
        try:
            red_price_raw = await page.inner_text("//span[contains(@class,'red-price')]")
            red_price = int(red_price_raw.replace(" ", ""))
        except:
            red_price = None

        # IMAGES
        images = []
        try:
            img_elements = await page.query_selector_all("//img[contains(@class,'br-main-img')]")
            for img in img_elements:
                src = await img.get_attribute("src")
                if src:
                    images.append(src)
        except:
            pass

        # DESCRIPTION (generic)
        description = {}
        try:
            spans = await page.query_selector_all("//div[contains(@class,'br-pr-chr-item')]//span")
            texts = []
            for s in spans:
                t = (await s.inner_text()).strip()
                if t:
                    t = t.replace("\xa0", " ")
                    t = " ".join(t.split())
                    texts.append(t)

            for i in range(0, len(texts), 2):
                key = texts[i]
                value = texts[i+1] if i + 1 < len(texts) else ""
                description[key] = value

        except:
            pass

        def normalize_apostrophes(text: str) -> str:
            if not text:
                return text
            return text.replace("’", "'").replace("ʼ", "'").replace("‘", "'")

        async def safe_text(page, label: str):
            label = normalize_apostrophes(label)
            try:
                parent_xpath = f"xpath=//span[contains(normalize-space(), '{label}')]/.."
                parent = page.locator(parent_xpath)

                if not await parent.count():
                    print(f"Problem: '{label}' parent not found")
                    return None

                value_xpath = f"xpath=.//span[not(contains(normalize-space(), '{label}'))]"
                value = parent.locator(value_xpath).first

                if not await value.count():
                    print(f"Problem: '{label}' value not found")
                    return None

                return (await value.inner_text()).strip()
            except Exception as e:
                print(f"Error processing '{label}': {e}")
                return None

        color = await safe_text(page, "Колір")
        producer = await safe_text(page, "Виробник")
        art = await safe_text(page, "Артикул")
        diagonal = await safe_text(page, "Діагональ екрану")
        display = await safe_text(page, "Роздільна здатність екрану")
        memory = await safe_text(page, "Вбудована пам’ять") or await safe_text(page, "Вбудована пам")

        # SAVE TO DB
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

        print("Saved to DB:", title)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(parse("https://brain.com.ua/Mobilniy_telefon_Apple_iPhone_15_128GB_Black-p1044347.html"))
