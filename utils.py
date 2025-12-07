# utils.py
import os
import logging

logger = logging.getLogger(__name__)


def ensure_dir(path):
    """Tạo thư mục nếu chưa tồn tại"""
    try:
        if not os.path.exists(path):
            os.makedirs(path)
            logger.info(f"📁 Đã tạo folder: {path}/")
    except Exception as e:
        logger.error(f"❌ Không thể tạo folder {path}: {e}")
        raise


async def download_file(page, url, path):
    """
    Download file từ URL và lưu vào path
    Returns True nếu thành công, raise Exception nếu lỗi
    """
    try:
        # Check nếu file đã tồn tại
        if os.path.exists(path):
            logger.debug(f"⏭ Bỏ qua {path} (đã tồn tại)")
            return True

        # Download
        resp = await page.request.get(url, timeout=30000)

        if resp.status != 200:
            raise Exception(f"HTTP {resp.status}")

        content = await resp.body()

        # Validate content
        if not content or len(content) < 100:  # File quá nhỏ → có thể lỗi
            raise Exception(f"File size quá nhỏ ({len(content)} bytes)")

        # Save file
        with open(path, "wb") as f:
            f.write(content)

        return True

    except Exception as e:
        logger.warning(f"⚠️  Lỗi download {os.path.basename(path)}: {e}")
        # Cleanup nếu file bị lỗi
        if os.path.exists(path):
            try:
                os.remove(path)
            except:
                pass
        raise