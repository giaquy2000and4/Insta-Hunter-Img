# profile_downloader.py
import asyncio
import random
import logging
from utils import ensure_dir, download_file
from tqdm.asyncio import tqdm

logger = logging.getLogger(__name__)

# Constants
SCROLL_WAIT = 2000  # ms
PAGE_LOAD_WAIT = 3000  # ms
MAX_SCROLL_ATTEMPTS = 50  # Tránh scroll vô hạn
CONCURRENT_DOWNLOADS = 5  # Số file tải đồng thời


async def extract_media(page):
    """Trích xuất tất cả media URLs từ page"""
    media = set()

    try:
        # Extract images
        imgs = await page.query_selector_all("img")
        for img in imgs:
            src = await img.get_attribute("src")
            if src and "scontent" in src:
                media.add(src)

        # Extract videos
        videos = await page.query_selector_all("video")
        for vid in videos:
            src = await vid.get_attribute("src")
            if src:
                media.add(src)

            # Check source tag
            src_tag = await vid.query_selector("source")
            if src_tag:
                s = await src_tag.get_attribute("src")
                if s:
                    media.add(s)

    except Exception as e:
        logger.error(f"❌ Lỗi khi extract media: {e}")

    return media


async def download_profile(page, username, amount):
    """Download media từ Instagram profile"""
    try:
        logger.info(f"🌐 Mở profile @{username}")

        # Navigate với timeout
        try:
            await page.goto(
                f"https://www.instagram.com/{username}/",
                wait_until="domcontentloaded",
                timeout=30000
            )
            await page.wait_for_timeout(PAGE_LOAD_WAIT)
        except Exception as e:
            logger.error(f"❌ Không thể truy cập profile @{username}: {e}")
            return

        # Check nếu profile không tồn tại
        not_found = await page.query_selector('text="Sorry, this page isn\'t available."')
        if not_found:
            logger.error(f"❌ Profile @{username} không tồn tại hoặc bị private!")
            return

        ensure_dir(username)

        collected = []
        last_len = 0
        scroll_count = 0

        logger.info("🔎 Đang quét bài đăng...")

        # Scroll để load thêm posts
        while len(collected) < amount and scroll_count < MAX_SCROLL_ATTEMPTS:
            # Scroll
            await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            await page.wait_for_timeout(SCROLL_WAIT)

            # Rate limiting - tránh bị Instagram ban
            await asyncio.sleep(random.uniform(0.3, 0.8))

            # Extract media
            found = await extract_media(page)
            for url in found:
                if url not in collected:
                    collected.append(url)

            # Check nếu không load thêm được
            if len(collected) == last_len:
                scroll_count += 1
                if scroll_count >= 3:  # Thử 3 lần không có gì mới → dừng
                    logger.info("⚠️  Không tìm thấy thêm media mới")
                    break
            else:
                scroll_count = 0

            last_len = len(collected)
            logger.info(f"📊 Đã tìm thấy {len(collected)} media...")

        if not collected:
            logger.warning(f"❌ Không tìm thấy media nào từ @{username}")
            return

        # Limit số lượng download
        to_download = collected[:amount]
        logger.info(f"📥 Bắt đầu tải {len(to_download)} media...")

        # Download với progress bar và concurrent
        success_count = 0

        # Chia nhỏ thành batches để tránh quá tải
        for i in range(0, len(to_download), CONCURRENT_DOWNLOADS):
            batch = to_download[i:i + CONCURRENT_DOWNLOADS]
            tasks = []

            for idx, url in enumerate(batch, start=i + 1):
                ext = "mp4" if ".mp4" in url else "jpg"
                path = f"{username}/{idx}.{ext}"
                tasks.append(download_file(page, url, path))

            # Download batch
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Count successes
            for j, result in enumerate(results):
                if result is True:
                    success_count += 1
                    logger.info(f"✅ [{success_count}/{len(to_download)}] Đã tải {i + j + 1}.{ext}")
                elif isinstance(result, Exception):
                    logger.warning(f"⚠️  Lỗi tải file {i + j + 1}: {result}")

            # Rate limiting giữa các batches
            await asyncio.sleep(random.uniform(0.5, 1.0))

        logger.info(f"🎉 Hoàn tất! Đã tải {success_count}/{len(to_download)} media vào folder '{username}/'")

    except Exception as e:
        logger.error(f"❌ Lỗi nghiêm trọng khi download profile: {e}")
        import traceback
        traceback.print_exc()