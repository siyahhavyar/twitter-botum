# file: multi_site_generator.py
import asyncio
import time
import os
from playwright.async_api import async_playwright

# senin mevcut post_to_twitter fonksiyonunu import et
# from my_twitter_bot import post_to_twitter

PROMPT = "A dramatic, ultra-detailed fantasy landscape, golden light, cinematic, 4k"

# her site için handler bir async fonksiyon olacak.
# handler -> (success:bool, image_path:str or None, error_msg:str or None)

async def handler_raphael(page, prompt):
    try:
        await page.goto("https://raphaelai.org/", timeout=60000)
        # selectorlar örnek; gerçek sayfa için inspeck yapıp güncelle
        await page.fill("textarea[placeholder*='Describe']", prompt)
        await page.click("button:has-text('Generate')")
        # bekle ve image elementini yakala
        await page.wait_for_selector("img.result-image", timeout=120000)
        src = await page.get_attribute("img.result-image", "src")
        # doğrudan base64 veya veri URL ise indir
        if src.startswith("data:image"):
            header, b64 = src.split(",", 1)
            import base64
            data = base64.b64decode(b64)
            fn = f"out_raphael_{int(time.time())}.png"
            with open(fn, "wb") as f: f.write(data)
            return True, fn, None
        else:
            # normal URL -> download
            fn = f"out_raphael_{int(time.time())}.png"
            await page.request.get(src).then(lambda r: open(fn,'wb').write(r.body()))
            return True, fn, None
    except Exception as e:
        return False, None, str(e)

async def handler_deepai(page, prompt):
    try:
        await page.goto("https://deepai.org/machine-learning-model/text2img", timeout=60000)
        await page.fill("textarea#text-prompt", prompt)
        await page.click("button:has-text('Submit')")
        await page.wait_for_selector("img", timeout=120000)
        # more robust selector required
        img = await page.query_selector("img")
        src = await img.get_attribute("src")
        # download as above...
        if src.startswith("data:image"):
            import base64
            header, b64 = src.split(",",1)
            data = base64.b64decode(b64)
            fn = f"out_deepai_{int(time.time())}.png"
            with open(fn, "wb") as f: f.write(data)
            return True, fn, None
        else:
            fn = f"out_deepai_{int(time.time())}.png"
            await page.request.get(src).then(lambda r: open(fn,'wb').write(r.body()))
            return True, fn, None
    except Exception as e:
        return False, None, str(e)

# mapping
SITE_HANDLERS = [
    ("raphaelai", handler_raphael),
    ("deepai", handler_deepai),
    # ... diğer handler fonksiyonlarını buraya ekle
]

async def try_sites_sequential(prompt, max_sites=None):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        for name, handler in SITE_HANDLERS[:max_sites]:
            print("Deniyor:", name)
            ok, img_path, err = await handler(page, prompt)
            if ok and img_path:
                print("Başarılı:", name, img_path)
                await browser.close()
                return img_path, name
            else:
                print("Başarısız:", name, err)
                # bekle / log vs
                await asyncio.sleep(1)
        await browser.close()
        return None, None

if __name__ == "__main__":
    img, site = asyncio.run(try_sites_sequential(PROMPT, max_sites=10))
    if img:
        print("Görsel alındı:", img, "from", site)
        # post_to_twitter kodunu çağır
        # post_to_twitter(open(img,'rb').read(), "caption here")
    else:
        print("Hiçbir site başarılı olmadı.")
