# main.py
import asyncio
import logging
from screeninfo import get_monitors
from playwright.async_api import async_playwright
from cookie_loader import choose_cookie_file, load_cookies
from profile_downloader import download_profile
from story_downloader import download_stories

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


async def main():
    try:
        # Load cookie
        logger.info("🔐 Đang tải cookie...")
        cookie_path = choose_cookie_file()
        if not cookie_path:
            logger.error("❌ Không chọn file cookie!")
            return

        cookies = load_cookies(cookie_path)
        if not cookies:
            logger.error("❌ Cookie file không hợp lệ hoặc trống!")
            return

        logger.info("✅ Cookie đã load thành công!")

        # Lấy kích thước màn hình
        monitor = get_monitors()[0]
        screen_width = monitor.width
        screen_height = monitor.height
        window_width = int(screen_width / 2)
        window_height = screen_height

        async with async_playwright() as pw:
            # Khởi chạy browser
            logger.info("🌐 Đang khởi động browser...")
            browser = await pw.chromium.launch(
                headless=False,
                args=[f"--window-size={window_width},{window_height}"]
            )

            context = await browser.new_context(
                viewport={"width": window_width, "height": window_height},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )

            await context.add_cookies(cookies)
            page = await context.new_page()

            # Main menu loop
            while True:
                print("\n" + "=" * 40)
                print(" 📥 Instagram Downloader Menu")
                print("=" * 40 + "\n")
                print("1  Tải toàn bộ ảnh + video (theo thứ tự)")
                print("2  Tải Reels / Video")
                print("3  Tải Story")
                print("4  Thoát\n")

                choice = input("👉 Chọn chức năng (1-4): ").strip()

                if choice == "4":
                    logger.info("👋 Thoát chương trình...")
                    break

                if choice not in ["1", "2", "3"]:
                    logger.warning("❌ Lựa chọn không hợp lệ!")
                    continue

                # Validate username
                username = input("👤 Username Instagram: ").strip()
                if not username or not username.replace("_", "").replace(".", "").isalnum():
                    logger.warning("❌ Username không hợp lệ! (chỉ chứa a-z, 0-9, _, .)")
                    continue

                try:
                    if choice == "1":
                        amount_str = input("📥 Số lượng media muốn tải: ").strip()
                        if not amount_str.isdigit() or int(amount_str) <= 0:
                            logger.warning("❌ Số lượng phải là số nguyên dương!")
                            continue
                        amount = int(amount_str)
                        await download_profile(page, username, amount, media_type="all")

                    elif choice == "2":
                        await download_profile(page, username, 999999, media_type="videos")

                    elif choice == "3":
                        await download_stories(page, username)

                except Exception as e:
                    logger.error(f"❌ Lỗi khi xử lý: {e}")
                    continue

            await browser.close()
            logger.info("✅ Đã đóng browser!")

    except KeyboardInterrupt:
        logger.info("\n⚠️  Người dùng dừng chương trình!")
    except Exception as e:
        logger.error(f"❌ Lỗi nghiêm trọng: {e}")


if __name__ == "__main__":
    asyncio.run(main())