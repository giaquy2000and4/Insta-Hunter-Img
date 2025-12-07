# utils.py
import os

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

async def download_file(page, url, path):
    resp = await page.request.get(url)
    content = await resp.body()
    with open(path, "wb") as f:
        f.write(content)
