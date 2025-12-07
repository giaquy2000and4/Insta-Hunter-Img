# main.py
import asyncio
from playwright.async_api import async_playwright
from cookie_loader import choose_cookie_file, load_cookies
from profile_downloader import download_profile
from story_downloader import download_stories

async def main():
    cookie_path = choose_cookie_file()
    cookies = load_cookies(cookie_path)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        context = await browser.new_context()
        await context.add_cookies(cookies)

        page = await context.new_page()

        while True:
            print("\n===========================")
            print(" Instagram Downloader Menu")
            print("===========================\n")
            print("1️⃣  Tải toàn bộ ảnh + video")
            print("2️⃣  Tải Reels / Video riêng")
            print("3️⃣  Tải Story")
            print("4️⃣  Thoát\n")

            choice = input("👉 Chọn chức năng: ")

            username = input("👤 Username Instagram: ")

            if choice == "1":
                amount = int(input("📥 Số lượng media muốn tải: "))
                await download_profile(page, username, amount)

            elif choice == "2":
                await download_profile(page, username, 9999)

            elif choice == "3":
                await download_stories(page, username)

            elif choice == "4":
                break

            else:
                print("❌ Lựa chọn không hợp lệ!")

        await browser.close()


asyncio.run(main())
