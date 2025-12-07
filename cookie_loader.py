# cookie_loader.py
from tkinter import Tk, filedialog

def choose_cookie_file():
    print("🔐 Choose cookie file (.txt Netscape)")
    Tk().withdraw()
    return filedialog.askopenfilename()


def load_cookies(path):
    cookies = []
    with open(path, "r") as f:
        for line in f:
            if line.startswith(".instagram.com"):
                parts = line.split("\t")
                if len(parts) >= 7:
                    cookies.append({
                        "name": parts[5],
                        "value": parts[6].strip(),
                        "domain": ".instagram.com",
                        "path": "/",
                    })
    return cookies
