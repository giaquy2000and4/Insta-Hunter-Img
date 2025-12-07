# profile_downloader.py
from utils import ensure_dir, download_file
import asyncio

async def extract_media(page):
    media = set()

    imgs = await page.query_selector_all("img")
    for img in imgs:
        src = await img.get_attribute("src")
        if src and "scontent" in src:
            media.add(src)

    videos = await page.query_selector_all("video")
    for vid in videos:
        src = await vid.get_attribute("src")
        if src:
            media.add(src)

        src_tag = await vid.query_selector("source")
        if src_tag:
            s = await src_tag.get_attribute("src")
            if s:
                media.add(s)

    return media


async def download_profile(page, username, amount):
    print(f"🌐 Mở profile @{username}")
    await page.goto(f"https://www.instagram.com/{username}/")
    await page.wait_for_timeout(3000)

    ensure_dir(username)

    collected = []
    last_len = 0

    print("🔎 Đang quét bài đăng (post + reels + video)...")

    while len(collected) < amount:
        await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
        await page.wait_for_timeout(2000)

        found = await extract_media(page)
        for url in found:
            if url not in collected:
                collected.append(url)

        if len(collected) == last_len:
            break
        last_len = len(collected)

    print(f"📥 Tìm thấy {len(collected)} media — bắt đầu tải...")

    for i, url in enumerate(collected[:amount], 1):
        ext = "mp4" if ".mp4" in url else "jpg"
        await download_file(page, url, f"{username}/{i}.{ext}")
        print(f"⬇ {i}/{amount}")

    print("🎉 Tải profile hoàn tất!")
