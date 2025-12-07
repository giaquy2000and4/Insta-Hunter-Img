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


async def click_posts_to_load_videos(page):
    """Click vào từng post để load video URLs"""
    video_urls = []

    try:
        # Tìm tất cả các post links
        posts = await page.query_selector_all('article a[href*="/p/"], article a[href*="/reel/"]')

        for i, post in enumerate(posts[:50]):  # Giới hạn 50 posts để tránh quá lâu
            try:
                href = await post.get_attribute("href")
                if not href:
                    continue

                # Click để mở post
                await post.click()
                await page.wait_for_timeout(2000)

                # Extract video từ modal
                videos = await page.query_selector_all("video")
                for vid in videos:
                    src = await vid.get_attribute("src")
                    if src:
                        video_urls.append(src)

                # Đóng modal
                close_btn = await page.query_selector('svg[aria-label="Close"]')
                if close_btn:
                    await close_btn.click()
                    await page.wait_for_timeout(500)

            except Exception as e:
                logger.debug(f"Lỗi khi click post {i}: {e}")
                continue

    except Exception as e:
        logger.warning(f"⚠️  Lỗi khi click posts: {e}")

    return video_urls


async def download_profile(page, username, amount, media_type="all"):
    """
    Download media từ Instagram profile
    media_type: "all" | "images" | "videos"
    """
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

        # Tạo folder structure
        base_dir = username
        ensure_dir(base_dir)
        ensure_dir(f"{base_dir}/PIC")
        ensure_dir(f"{base_dir}/REEL")

        collected_images = []
        collected_videos = []
        last_len = 0
        scroll_count = 0

        logger.info("🔎 Đang quét bài đăng...")

        # Scroll để load thêm posts
        while (len(collected_images) + len(collected_videos)) < amount and scroll_count < MAX_SCROLL_ATTEMPTS:
            # Scroll
            await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            await page.wait_for_timeout(SCROLL_WAIT)

            # Rate limiting
            await asyncio.sleep(random.uniform(0.3, 0.8))

            # Extract images từ thumbnails
            found = await extract_media(page)
            for url in found:
                if url not in collected_images and url not in collected_videos:
                    if ".mp4" in url or "video" in url:
                        collected_videos.append(url)
                    else:
                        collected_images.append(url)

            current_len = len(collected_images) + len(collected_videos)

            # Check nếu không load thêm được
            if current_len == last_len:
                scroll_count += 1
                if scroll_count >= 3:
                    logger.info("⚠️  Không tìm thấy thêm media mới")
                    break
            else:
                scroll_count = 0

            last_len = current_len
            logger.info(f"📊 Đã tìm thấy {len(collected_images)} ảnh, {len(collected_videos)} video...")

        # Click vào posts để load video URLs thực sự
        if media_type in ["all", "videos"]:
            logger.info("🎬 Đang load video URLs (click từng post)...")
            real_video_urls = await click_posts_to_load_videos(page)

            # Merge video URLs
            for url in real_video_urls:
                if url not in collected_videos:
                    collected_videos.append(url)

            logger.info(f"✅ Đã load {len(collected_videos)} video URLs")

        # Prepare download lists
        images_to_download = collected_images[:amount] if media_type in ["all", "images"] else []
        videos_to_download = collected_videos[:amount] if media_type in ["all", "videos"] else []

        if not images_to_download and not videos_to_download:
            logger.warning(f"❌ Không tìm thấy media nào từ @{username}")
            return

        # Download images
        if images_to_download:
            logger.info(f"📥 Bắt đầu tải {len(images_to_download)} ảnh...")
            await download_batch(page, images_to_download, f"{base_dir}/PIC", "jpg")

        # Download videos
        if videos_to_download:
            logger.info(f"📥 Bắt đầu tải {len(videos_to_download)} video...")
            await download_batch(page, videos_to_download, f"{base_dir}/REEL", "mp4")

        logger.info(f"🎉 Hoàn tất! Đã tải media vào folder '{base_dir}/'")

    except Exception as e:
        logger.error(f"❌ Lỗi nghiêm trọng khi download profile: {e}")
        import traceback
        traceback.print_exc()


async def download_batch(page, urls, folder, extension):
    """Download một batch media vào folder"""
    success_count = 0

    for i in range(0, len(urls), CONCURRENT_DOWNLOADS):
        batch = urls[i:i + CONCURRENT_DOWNLOADS]
        tasks = []

        for idx, url in enumerate(batch, start=i + 1):
            path = f"{folder}/{idx}.{extension}"
            tasks.append(download_file(page, url, path))

        # Download batch
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Count successes
        for j, result in enumerate(results):
            if result is True:
                success_count += 1
                logger.info(f"✅ [{success_count}/{len(urls)}] {folder}/{i + j + 1}.{extension}")
            elif isinstance(result, Exception):
                logger.warning(f"⚠️  Lỗi tải {i + j + 1}.{extension}: {result}")

        # Rate limiting
        await asyncio.sleep(random.uniform(0.5, 1.0))

    return success_count