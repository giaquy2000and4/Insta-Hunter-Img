# 📥 Instagram Media Downloader

## 🌟 Features
- ✅ Tải ảnh + video từ profile Instagram
- ✅ Tải Reels/Video riêng biệt  
- ✅ Tải Stories (trước khi hết hạn 24h)
- ✅ Download song song (concurrent) - nhanh hơn 5x
- ✅ Error handling toàn diện
- ✅ Progress logging chi tiết
- ✅ Rate limiting tránh bị Instagram ban
- ✅ Skip file đã tải (resume support)

## 📋 Requirements
- Python 3.8+
- Instagram cookies (Netscape format)
- Kết nối internet

## 🚀 Installation

### 1. Clone repo
```bash
git clone <your-repo>
cd instagram-downloader
```

### 2. Cài đặt dependencies
```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Chuẩn bị cookie file
- Cài extension [Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
- Đăng nhập Instagram
- Export cookies → lưu file `.txt`

## 💻 Usage

### Chạy chương trình
```bash
python main.py
```

### Menu options
```
1. Tải toàn bộ ảnh + video (theo thứ tự)
   → Nhập số lượng media cần tải
   
2. Tải Reels / Video
   → Tải tất cả video từ profile
   
3. Tải Story
   → Tải story hiện tại (trước khi hết hạn)
   
4. Thoát
```

## 📁 Output Structure
```
instagram-downloader/
├── username/              # Profile media
│   ├── 1.jpg
│   ├── 2.mp4
│   └── ...
├── username_stories/      # Stories
│   ├── 1.jpg
│   ├── 2.mp4
│   └── ...
└── logs/
```

## ⚙️ Configuration

### Tùy chỉnh trong code:
```python
# profile_downloader.py
CONCURRENT_DOWNLOADS = 5    # Số file tải đồng thời
MAX_SCROLL_ATTEMPTS = 50    # Giới hạn scroll
SCROLL_WAIT = 2000          # Delay giữa mỗi scroll (ms)
```

## ⚠️ Notes
- Cookie sẽ hết hạn sau ~90 ngày
- Private account cần follow trước
- Tải quá nhanh có thể bị Instagram rate limit
- Respect Instagram's Terms of Service

## 🐛 Troubleshooting

### Cookie không hoạt động
```bash
# Xóa cache browser trước khi export lại
# Hoặc dùng chế độ ẩn danh
```

### Lỗi "Profile không tồn tại"
- Check username đúng chưa (không có @)
- Account có bị private/ban không

### Download chậm
- Tăng `CONCURRENT_DOWNLOADS` (max 10)
- Check tốc độ internet

## 📝 Changelog

### v2.0 (Optimized)
- ✅ Concurrent downloads (5x faster)
- ✅ Full error handling
- ✅ Progress logging
- ✅ Rate limiting protection
- ✅ Skip existing files
- ✅ Input validation
- ✅ Better cookie loader

### v1.0 (Original)
- Basic download functionality

## 📄 License
MIT License - Use at your own risk

## ⚡ Performance
- **Old version**: ~10 files/phút
- **New version**: ~50 files/phút (với 5 concurrent)

## 🤝 Contributing
Pull requests welcome!

---
**⚠️ Disclaimer**: Tool này chỉ dùng cho mục đích cá nhân và học tập. Hãy tôn trọng quyền riêng tư và bản quyền của người khác.