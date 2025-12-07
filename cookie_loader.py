# cookie_loader.py
import os
import logging

logger = logging.getLogger(__name__)


def choose_cookie_file():
    """Cho phép nhập path thủ công hoặc chọn file qua dialog"""
    print("\n🔐 Chọn cookie file (.txt Netscape)")
    print("Option 1: Nhập path file cookie")
    print("Option 2: Nhấn Enter để mở hộp thoại chọn file")

    choice = input("\n👉 Nhập path hoặc Enter: ").strip()

    if choice:
        if os.path.exists(choice):
            return choice
        else:
            logger.error(f"❌ File không tồn tại: {choice}")
            return None

    # Fallback to file dialog
    try:
        from tkinter import Tk, filedialog
        Tk().withdraw()
        return filedialog.askopenfilename(
            title="Chọn cookie file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
    except ImportError:
        logger.error("❌ Tkinter không khả dụng! Vui lòng nhập path thủ công.")
        return None
    except Exception as e:
        logger.error(f"❌ Lỗi khi mở file dialog: {e}")
        return None


def load_cookies(path):
    """Load cookies từ Netscape format"""
    cookies = []

    try:
        with open(path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()

                # Skip comments và empty lines
                if not line or line.startswith("#"):
                    continue

                if line.startswith(".instagram.com"):
                    parts = line.split("\t")
                    if len(parts) >= 7:
                        cookies.append({
                            "name": parts[5],
                            "value": parts[6].strip(),
                            "domain": ".instagram.com",
                            "path": "/",
                        })
                    else:
                        logger.warning(f"⚠️  Dòng {line_num} không đúng format (thiếu field)")

        logger.info(f"✅ Đã load {len(cookies)} cookies từ {os.path.basename(path)}")
        return cookies

    except FileNotFoundError:
        logger.error(f"❌ Không tìm thấy file: {path}")
        return []
    except Exception as e:
        logger.error(f"❌ Lỗi khi đọc cookie file: {e}")
        return []