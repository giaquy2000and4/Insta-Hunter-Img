# main.py
import asyncio
from screeninfo import get_monitors
from playwright.async_api import async_playwright
from cookie_loader import choose_cookie_file, load_cookies
from profile_downloader import download_profile
from story_downloader import download_stories


async def main():
    # Load cookie
    cookie_path = choose_cookie_file()
    cookies = load_cookies(cookie_path)

    # === LẤY KÍCH THƯỚC MÀN HÌNH KHÔNG DÙNG TKINTER ===
    monitor = get_monitors()[0]
    screen_width = monitor.width
    screen_height = monitor.height

    # 1/2 chiều rộng
    window_width = int(screen_width / 2)
    window_height = screen_height

    async with async_playwright() as pw:

        # === KHỞI CHẠY BROWSER ===
        browser = await pw.chromium.launch(
            headless=False,
            args=[f"--window-size={window_width},{window_height}"]
        )

        context = await browser.new_context(
            viewport={"width": window_width, "height": window_height}
        )

        await context.add_cookies(cookies)
        page = await context.new_page()

        while True:
            print("\n===========================")
            print(" 📥 Instagram Downloader Menu")
            print("===========================\n")
            print("1  Tải toàn bộ ảnh + video (theo thứ tự)")
            print("2  Tải Reels / Video")
            print("3  Tải Story")
            print("4  Thoát\n")

            choice = input("👉 Chọn chức năng: ")

            if choice == "4":
                print("👋 Thoát chương trình...")
                break

            username = input("👤 Username Instagram: ")

            if choice == "1":
                amount = int(input("📥 Số lượng media muốn tải: "))
                await download_profile(page, username, amount)

            elif choice == "2":
                await download_profile(page, username, 999999)

            elif choice == "3":
                await download_stories(page, username)

            else:
                print("❌ Lựa chọn không hợp lệ!")

        await browser.close()


asyncio.run(main())
