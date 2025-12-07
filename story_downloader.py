# story_downloader.py
from utils import ensure_dir, download_file

async def download_stories(page, username):
    print(f"🌐 Truy cập story của @{username}")
    await page.goto(f"https://www.instagram.com/stories/{username}/")
    await page.wait_for_timeout(3000)

    ensure_dir(f"{username}_stories")

    items = await page.query_selector_all("video, img")

    print(f"📥 Có {len(items)} story — tải xuống...")

    for i, tag in enumerate(items, 1):
        src = await tag.get_attribute("src")
        if not src:
            continue

        ext = "mp4" if ".mp4" in src else "jpg"
        await download_file(page, src, f"{username}_stories/{i}.{ext}")
        print(f"⬇ Story {i}")

    print("🎉 Tải story hoàn tất!")
