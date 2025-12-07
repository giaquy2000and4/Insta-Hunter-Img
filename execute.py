import asyncio
from playwright.async_api import async_playwright
from tkinter import Tk, filedialog
import os


def choose_cookie_file():
    print("🔐 Choose cookie file (.txt Netscape format)")
    Tk().withdraw()
    return filedialog.askopenfilename()


def load_cookies(path):
    cookies = []
    with open(path, "r") as f:
        for line in f:
            if line.startswith(".instagram.com"):
                parts = line.split("\t")
                if len(parts) >= 7:
                    cookies.append({
                        "name": parts[5],
                        "value": parts[6].strip(),
                        "domain": ".instagram.com",
                        "path": "/",
                    })
    return cookies


async def main():
    cookie_path = choose_cookie_file()
    username = input("👤 Enter Instagram username: ").strip()
    amount = int(input("🖼️ Number of images to download: ").strip())

    cookies = load_cookies(cookie_path)

    async with async_playwright() as pw:
        print("🚀 Launching browser...")
        browser = await pw.chromium.launch(headless=False)
        context = await browser.new_context()

        print("🍪 Loading cookies...")
        await context.add_cookies(cookies)

        page = await context.new_page()
        print(f"🌐 Opening profile: {username}")
        await page.goto(f"https://www.instagram.com/{username}/")

        await page.wait_for_timeout(3000)

        os.makedirs(username, exist_ok=True)

        print("🔎 Scanning images...")
        images = set()
        last_len = 0

        while len(images) < amount:
            await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            await page.wait_for_timeout(2000)

            pictures = await page.query_selector_all("img")

            for pic in pictures:
                src = await pic.get_attribute("src")
                if src and "scontent" in src:
                    images.add(src)
                if len(images) >= amount:
                    break

            if len(images) == last_len:
                break
            last_len = len(images)

        print(f"📥 Found {len(images)} images, downloading...")

        images = list(images)[:amount]
        for i, url in enumerate(images, 1):
            resp = await page.request.get(url)
            with open(f"{username}/{i}.jpg", "wb") as f:
                f.write(await resp.body())
            print(f"⬇ Downloaded {i}/{amount}")

        print("🎉 Done!")
        await browser.close()


asyncio.run(main())
