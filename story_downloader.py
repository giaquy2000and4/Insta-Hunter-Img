# story_downloader.py
import asyncio
import random
import logging
from utils import ensure_dir, download_file

logger = logging.getLogger(__name__)

# Constants
STORY_WAIT = 3000  # ms
CONCURRENT_DOWNLOADS = 3


async def download_stories(page, username):
    """Download stories từ Instagram user"""
    try:
        logger.info(f"🌐 Truy cập story của @{username}")

        # Navigate với timeout
        try:
            await page.goto(
                f"https://www.instagram.com/stories/{username}/",
                wait_until="domcontentloaded",
                timeout=30000
            )
            await page.wait_for_timeout(STORY_WAIT)
        except Exception as e:
            logger.error(f"❌ Không thể truy cập story @{username}: {e}")
            return

        # Check nếu không có story
        no_story = await page.query_selector('text="No story available"')
        if no_story:
            logger.warning(f"⚠️  @{username} không có story hoặc story đã hết hạn!")
            return

        folder = f"{username}_stories"
        ensure_dir(folder)

        # Extract story items
        items = await page.query_selector_all("video, img")

        if not items:
            logger.warning(f"❌ Không tìm thấy story nào từ @{username}")
            return

        logger.info(f"📥 Tìm thấy {len(items)} story — bắt đầu tải...")

        # Prepare download list
        downloads = []
        for i, tag in enumerate(items, 1):
            src = await tag.get_attribute("src")
            if src and ("scontent" in src or "cdninstagram" in src):
                ext = "mp4" if ".mp4" in src or "video" in src else "jpg"
                downloads.append((i, src, ext))

        if not downloads:
            logger.warning("❌ Không có story hợp lệ để tải!")
            return

        # Download với concurrent
        success_count = 0

        for i in range(0, len(downloads), CONCURRENT_DOWNLOADS):
            batch = downloads[i:i + CONCURRENT_DOWNLOADS]
            tasks = []

            for idx, url, ext in batch:
                path = f"{folder}/{idx}.{ext}"
                tasks.append(download_file(page, url, path))

            # Download batch
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Count successes
            for j, result in enumerate(results):
                idx, _, ext = batch[j]
                if result is True:
                    success_count += 1
                    logger.info(f"✅ [{success_count}/{len(downloads)}] Story {idx}.{ext}")
                elif isinstance(result, Exception):
                    logger.warning(f"⚠️  Lỗi tải story {idx}: {result}")

            # Rate limiting
            await asyncio.sleep(random.uniform(0.3, 0.7))

        logger.info(f"🎉 Hoàn tất! Đã tải {success_count}/{len(downloads)} story vào folder '{folder}/'")

    except Exception as e:
        logger.error(f"❌ Lỗi nghiêm trọng khi download story: {e}")
        import traceback
        traceback.print_exc()