# 📱 Facebook Group Post Scraper

Tool tự động lấy tất cả link bài viết từ Facebook group trong khoảng thời gian chỉ định, giải quyết vấn đề Facebook feed không hiển thị đầy đủ bài viết mới.

## ✨ Tính năng

- 🎯 **Lấy đầy đủ posts**: Không bỏ sót bài viết như Facebook feed
- ⏰ **Lọc theo thời gian**: Tùy chỉnh lấy posts trong N ngày qua
- 💾 **Lưu kết quả**: Xuất ra file JSON và TXT
- 🔐 **Lưu session**: Không cần login lại mỗi lần chạy
- 🎨 **Giao diện đẹp**: CLI có màu sắc, dễ theo dõi
- 📊 **Chi tiết**: Hiển thị thời gian và preview nội dung post

## 📋 Yêu cầu

- Python 3.8+
- Browser Chromium (tự động cài đặt qua Playwright)
- Kết nối Internet

## 🚀 Cài đặt

### Linux/Mac:

```bash
# Clone hoặc download project
cd lay-link-bai-viet-moi-facebook

# Chạy script setup (tự động cài đặt mọi thứ)
chmod +x setup.sh
./setup.sh
```

### Windows:

```cmd
# Clone hoặc download project
cd lay-link-bai-viet-moi-facebook

# Chạy script setup
setup.bat
```

### Hoặc cài đặt thủ công:

```bash
# Tạo virtual environment
python3 -m venv venv

# Kích hoạt virtual environment
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Cài đặt dependencies
pip install -r requirements.txt

# Cài đặt Playwright browsers
playwright install chromium
```

## 💡 Cách sử dụng

### Chạy tool:

```bash
# Kích hoạt virtual environment (nếu chưa)
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate  # Windows

# Chạy tool
python facebook_group_scraper.py
```

### Quy trình sử dụng:

1. **Nhập link Facebook group** khi được hỏi
   - VD: `https://www.facebook.com/groups/123456789`

2. **Chọn số ngày** muốn lấy posts
   - Mặc định: 7 ngày (1 tuần)
   - Có thể nhập số khác (VD: 14, 30)

3. **Chọn chế độ browser**
   - `n` (mặc định): Hiện browser - Dễ theo dõi và debug
   - `y`: Ẩn browser - Chạy nhanh hơn

4. **Login Facebook** (chỉ lần đầu tiên)
   - Browser sẽ mở Facebook
   - Đăng nhập tài khoản của bạn
   - Nhấn Enter trong terminal sau khi login xong
   - Session sẽ được lưu lại, không cần login lại lần sau

5. **Đợi tool chạy**
   - Tool sẽ tự động:
     - Truy cập group
     - Scroll và load tất cả posts
     - Extract links và thông tin
     - Lưu kết quả

6. **Xem kết quả**
   - Hiển thị trên terminal
   - Lưu trong thư mục `output/`
     - `posts_YYYYMMDD_HHMMSS.json` - File JSON đầy đủ thông tin
     - `posts_YYYYMMDD_HHMMSS_links.txt` - File text chỉ có links

## 📁 Cấu trúc thư mục

```
lay-link-bai-viet-moi-facebook/
├── facebook_group_scraper.py    # Main script
├── requirements.txt             # Python dependencies
├── setup.sh                     # Setup script cho Linux/Mac
├── setup.bat                    # Setup script cho Windows
├── README.md                    # File này
├── .gitignore                   # Git ignore rules
├── browser_data/                # Lưu cookies/session (tự tạo)
├── output/                      # Kết quả scraping (tự tạo)
│   ├── posts_20250113_143022.json
│   └── posts_20250113_143022_links.txt
└── venv/                        # Virtual environment (tự tạo)
```

## 📄 Format kết quả

### File JSON (`posts_*.json`):

```json
[
  {
    "link": "https://www.facebook.com/groups/123456789/posts/987654321",
    "time": "2025-01-13T14:30:22.123456",
    "time_relative": "2 giờ trước",
    "preview": "Nội dung preview của bài viết..."
  },
  ...
]
```

### File TXT (`posts_*_links.txt`):

```
https://www.facebook.com/groups/123456789/posts/987654321
https://www.facebook.com/groups/123456789/posts/987654322
https://www.facebook.com/groups/123456789/posts/987654323
...
```

## ⚠️ Lưu ý quan trọng

1. **Tài khoản Facebook**: Cần tài khoản Facebook đã tham gia group muốn scrape

2. **Rate limiting**: Facebook có thể chặn nếu:
   - Scrape quá nhiều/quá nhanh
   - Dùng nhiều tài khoản khác nhau
   - Chạy quá thường xuyên

   **Khuyến nghị**:
   - Chạy tối đa 1-2 lần/ngày cho mỗi group
   - Đợi vài phút giữa các lần chạy
   - Sử dụng tài khoản thật, không phải tài khoản ảo

3. **Privacy**:
   - Tool chỉ lấy posts từ groups bạn đã tham gia
   - Không thu thập thông tin cá nhân
   - Chỉ lấy link và metadata công khai

4. **Session cookies**:
   - Cookies được lưu trong `browser_data/`
   - Không share thư mục này với người khác
   - Có thể xóa để login lại

## 🔧 Troubleshooting

### Không tìm thấy posts:

- Kiểm tra lại URL group
- Đảm bảo đã login và là thành viên group
- Thử chạy lại với chế độ hiện browser (`n`) để debug

### Browser không mở:

```bash
# Cài lại Playwright browsers
playwright install chromium
```

### Lỗi khi scroll:

- Tăng timeout trong code
- Chạy với chế độ hiện browser để quan sát
- Kiểm tra kết nối Internet

### Không parse được thời gian:

- Facebook dùng nhiều format thời gian khác nhau
- Tool hỗ trợ cả tiếng Việt và tiếng Anh
- Nếu không parse được, sẽ mặc định là thời gian hiện tại

## 🛠️ Tùy chỉnh

### Thay đổi số lần scroll:

Trong `facebook_group_scraper.py`, dòng 278:

```python
await self.scroll_and_load_posts(max_scrolls=50)  # Thay đổi số 50
```

### Thay đổi timeout:

Dòng 270:

```python
await self.page.goto(group_url, wait_until='networkidle', timeout=60000)  # 60s
```

### Thêm selectors mới:

Nếu Facebook thay đổi HTML, update selectors ở dòng 186:

```python
selectors = [
    'div[role="article"]',
    'div.x1yztbdb',
    '[data-pagelet^="FeedUnit"]',
    # Thêm selector mới ở đây
]
```

## 📝 TODO / Cải tiến

- [ ] Thêm export format CSV, Excel
- [ ] Lưu ảnh/video từ posts
- [ ] Lấy comments và reactions
- [ ] Hỗ trợ nhiều groups cùng lúc
- [ ] GUI interface
- [ ] Docker support
- [ ] Lọc theo keywords
- [ ] Scheduled scraping

## 🤝 Đóng góp

Mọi đóng góp đều được chào đón! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## ⚖️ Disclaimer

Tool này chỉ dành cho mục đích cá nhân và học tập. Vui lòng:
- Tuân thủ Terms of Service của Facebook
- Tôn trọng privacy của người dùng
- Sử dụng có trách nhiệm
- Không spam hay abuse

Tác giả không chịu trách nhiệm về việc sử dụng tool không đúng mục đích.

## 📧 Liên hệ

Nếu có vấn đề hoặc câu hỏi, vui lòng tạo Issue trên GitHub.

---

Made with ❤️ by Claude Code

**Happy Scraping! 🚀**
