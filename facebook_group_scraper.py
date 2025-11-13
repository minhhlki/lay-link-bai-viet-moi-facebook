#!/usr/bin/env python3
"""
Facebook Group Post Scraper
Lấy tất cả links bài viết từ Facebook group trong tuần qua
"""

import asyncio
import re
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Set
from playwright.async_api import async_playwright, Page, Browser
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)


class FacebookGroupScraper:
    def __init__(self, headless: bool = False, user_data_dir: str = None):
        """
        Initialize the scraper

        Args:
            headless: Chạy browser ẩn (True) hoặc hiện (False)
            user_data_dir: Thư mục lưu cookies/session để không phải login lại
        """
        self.headless = headless
        self.user_data_dir = user_data_dir or "./browser_data"
        self.browser: Browser = None
        self.page: Page = None
        self.context = None
        self.playwright = None

    async def init_browser(self):
        """Khởi tạo browser với Playwright"""
        print(f"{Fore.CYAN}🚀 Đang khởi động browser...")

        try:
            self.playwright = await async_playwright().start()

            # Sử dụng persistent context để lưu cookies/session
            self.context = await self.playwright.chromium.launch_persistent_context(
                self.user_data_dir,
                headless=self.headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                ],
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            self.page = await self.context.new_page()
            print(f"{Fore.GREEN}✓ Browser đã sẵn sàng")

        except Exception as e:
            error_msg = str(e)

            # Check for missing dependencies error
            if "missing dependencies" in error_msg.lower():
                print(f"\n{Fore.RED}✗ Lỗi: Thiếu system dependencies để chạy browser")
                print(f"\n{Fore.YELLOW}Giải pháp:")
                print(f"{Fore.YELLOW}1. Chạy lệnh sau (cần sudo):")
                print(f"{Fore.WHITE}   sudo playwright install-deps")
                print(f"\n{Fore.YELLOW}2. Hoặc cài thủ công:")
                print(f"{Fore.WHITE}   sudo apt-get install libnss3 libnspr4 libgbm1")
                print(f"\n{Fore.YELLOW}3. Nếu không có sudo access (VD: trên JupyterLab):")
                print(f"{Fore.WHITE}   - Thử chạy với headless=False (chọn 'n' khi hỏi)")
                print(f"{Fore.WHITE}   - Hoặc liên hệ admin để cài dependencies")

            raise

    async def check_login_status(self) -> bool:
        """Kiểm tra xem đã login Facebook chưa"""
        try:
            # Kiểm tra xem có cookie Facebook không
            cookies = await self.context.cookies()
            fb_cookies = [c for c in cookies if 'facebook.com' in c.get('domain', '')]

            if fb_cookies:
                print(f"{Fore.GREEN}✓ Đã có session Facebook")
                return True
            else:
                print(f"{Fore.YELLOW}⚠ Chưa login Facebook")
                return False
        except:
            return False

    async def wait_for_login(self):
        """Đợi user login thủ công"""
        print(f"\n{Fore.YELLOW}{'='*60}")
        print(f"{Fore.YELLOW}📝 Vui lòng login Facebook trong cửa sổ browser")
        print(f"{Fore.YELLOW}   Sau khi login xong, nhấn Enter để tiếp tục...")
        print(f"{Fore.YELLOW}{'='*60}\n")

        # Mở Facebook để login
        await self.page.goto('https://www.facebook.com/', wait_until='networkidle')

        # Đợi user nhấn Enter
        input(f"{Fore.CYAN}> Nhấn Enter sau khi login xong: ")
        print(f"{Fore.GREEN}✓ Tiếp tục...")

    def parse_relative_time(self, time_text: str) -> datetime:
        """
        Parse thời gian tương đối từ Facebook (VD: "2h", "5 phút", "3 ngày")

        Args:
            time_text: Text thời gian từ Facebook

        Returns:
            datetime object
        """
        now = datetime.now()
        time_text = time_text.lower().strip()

        # Pattern cho các định dạng thời gian
        patterns = {
            r'(\d+)\s*giây': ('seconds', 1),
            r'(\d+)\s*phút': ('minutes', 1),
            r'(\d+)\s*giờ': ('hours', 1),
            r'(\d+)\s*h': ('hours', 1),
            r'(\d+)\s*ngày': ('days', 1),
            r'(\d+)\s*tuần': ('weeks', 1),
            r'(\d+)\s*tháng': ('months', 30),
            r'(\d+)\s*năm': ('years', 365),
        }

        for pattern, (unit, multiplier) in patterns.items():
            match = re.search(pattern, time_text)
            if match:
                value = int(match.group(1))
                if unit in ['seconds', 'minutes', 'hours', 'days', 'weeks']:
                    delta = timedelta(**{unit: value})
                else:
                    # Cho tháng và năm, convert sang days
                    delta = timedelta(days=value * multiplier)
                return now - delta

        # Nếu chỉ có "vài giây" hoặc "Vừa xong"
        if any(x in time_text for x in ['vừa xong', 'just now', 'vài giây']):
            return now

        # Không parse được, trả về thời gian hiện tại
        return now

    async def scroll_and_load_posts(self, max_scrolls: int = 50):
        """
        Scroll xuống để load thêm posts

        Args:
            max_scrolls: Số lần scroll tối đa
        """
        print(f"{Fore.CYAN}📜 Đang scroll và load posts...")

        last_height = await self.page.evaluate('document.body.scrollHeight')
        scroll_count = 0
        no_change_count = 0

        while scroll_count < max_scrolls:
            # Scroll xuống cuối
            await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')

            # Đợi load
            await asyncio.sleep(2)

            # Kiểm tra height mới
            new_height = await self.page.evaluate('document.body.scrollHeight')

            if new_height == last_height:
                no_change_count += 1
                if no_change_count >= 3:
                    print(f"{Fore.GREEN}✓ Đã load hết posts")
                    break
            else:
                no_change_count = 0

            last_height = new_height
            scroll_count += 1
            print(f"{Fore.CYAN}   Scroll {scroll_count}/{max_scrolls}...", end='\r')

        print()  # New line

    async def extract_post_links(self, days: int = 7) -> List[dict]:
        """
        Extract tất cả post links trong khoảng thời gian

        Args:
            days: Số ngày lấy posts (mặc định 7 ngày)

        Returns:
            List các posts với link và metadata
        """
        print(f"{Fore.CYAN}🔍 Đang extract post links...")

        cutoff_date = datetime.now() - timedelta(days=days)
        posts = []
        seen_links = set()

        # Lấy tất cả post elements
        # Facebook dùng nhiều selector khác nhau, thử nhiều cách
        selectors = [
            'div[role="article"]',
            'div.x1yztbdb',  # Facebook's class cho posts
            '[data-pagelet^="FeedUnit"]',
        ]

        post_elements = []
        for selector in selectors:
            elements = await self.page.query_selector_all(selector)
            if elements:
                post_elements = elements
                print(f"{Fore.GREEN}✓ Tìm thấy {len(elements)} posts với selector: {selector}")
                break

        if not post_elements:
            print(f"{Fore.RED}✗ Không tìm thấy posts nào")
            return []

        print(f"{Fore.CYAN}📊 Đang phân tích {len(post_elements)} posts...")

        for idx, element in enumerate(post_elements, 1):
            try:
                # Lấy HTML của post
                html = await element.inner_html()

                # Tìm link bài viết
                # Facebook post links có format: /groups/{group_id}/posts/{post_id}
                # hoặc /groups/{group_id}/permalink/{post_id}
                link_patterns = [
                    r'href="(/groups/\d+/posts/\d+)',
                    r'href="(/groups/\d+/permalink/\d+)',
                    r'href="(https://www\.facebook\.com/groups/\d+/posts/\d+)',
                    r'href="(https://www\.facebook\.com/groups/\d+/permalink/\d+)',
                ]

                post_link = None
                for pattern in link_patterns:
                    matches = re.findall(pattern, html)
                    if matches:
                        post_link = matches[0]
                        # Làm sạch link (remove query params)
                        post_link = post_link.split('?')[0]
                        # Convert relative URL to absolute
                        if not post_link.startswith('http'):
                            post_link = f"https://www.facebook.com{post_link}"
                        break

                if not post_link or post_link in seen_links:
                    continue

                # Tìm thời gian đăng
                time_element = await element.query_selector('a[href*="posts"] span, a[href*="permalink"] span')
                post_time = datetime.now()  # Default

                if time_element:
                    time_text = await time_element.inner_text()
                    post_time = self.parse_relative_time(time_text)

                # Kiểm tra xem post có trong khoảng thời gian không
                if post_time < cutoff_date:
                    continue

                # Lấy preview text của post
                preview = ""
                text_elements = await element.query_selector_all('div[dir="auto"]')
                if text_elements:
                    for text_el in text_elements[:3]:  # Chỉ lấy 3 đoạn đầu
                        text = await text_el.inner_text()
                        if len(text) > 20:  # Bỏ qua text quá ngắn
                            preview = text[:200]
                            break

                posts.append({
                    'link': post_link,
                    'time': post_time.isoformat(),
                    'time_relative': self.get_relative_time_string(post_time),
                    'preview': preview
                })

                seen_links.add(post_link)
                print(f"{Fore.GREEN}   ✓ Post {len(posts)}: {post_link[:60]}...", end='\r')

            except Exception as e:
                continue

        print()  # New line
        print(f"{Fore.GREEN}✓ Tìm thấy {len(posts)} posts trong {days} ngày qua")

        # Sort by time (newest first)
        posts.sort(key=lambda x: x['time'], reverse=True)

        return posts

    def get_relative_time_string(self, dt: datetime) -> str:
        """Convert datetime thành string tương đối"""
        now = datetime.now()
        diff = now - dt

        if diff.days > 0:
            return f"{diff.days} ngày trước"
        elif diff.seconds >= 3600:
            hours = diff.seconds // 3600
            return f"{hours} giờ trước"
        elif diff.seconds >= 60:
            minutes = diff.seconds // 60
            return f"{minutes} phút trước"
        else:
            return "Vừa xong"

    async def check_if_login_required(self) -> bool:
        """
        Kiểm tra xem page hiện tại có yêu cầu login không

        Returns:
            True nếu cần login, False nếu không
        """
        try:
            current_url = self.page.url
            page_content = await self.page.content()

            # Kiểm tra các dấu hiệu cần login
            login_indicators = [
                'login' in current_url.lower(),
                'login_attempt' in current_url.lower(),
                'id="login_form"' in page_content,
                'name="login"' in page_content,
            ]

            return any(login_indicators)
        except:
            return False

    async def scrape_group(self, group_url: str, days: int = 7, skip_login: bool = False) -> List[dict]:
        """
        Main method để scrape Facebook group

        Args:
            group_url: URL của Facebook group
            days: Số ngày lấy posts (mặc định 7)
            skip_login: Thử scrape mà không login (cho public groups)

        Returns:
            List các posts
        """
        try:
            # Khởi tạo browser
            await self.init_browser()

            # Kiểm tra login status
            is_logged_in = await self.check_login_status()

            # Nếu không skip login và chưa login -> yêu cầu login
            if not skip_login and not is_logged_in:
                await self.wait_for_login()

            # Nếu skip login
            if skip_login and not is_logged_in:
                print(f"{Fore.CYAN}🔓 Thử truy cập public group mà không login...")

            # Navigate đến group
            print(f"\n{Fore.CYAN}🌐 Đang truy cập group: {group_url}")
            await self.page.goto(group_url, wait_until='networkidle', timeout=60000)

            # Đợi page load
            await asyncio.sleep(3)

            # Kiểm tra xem có bị redirect về login page không
            if await self.check_if_login_required():
                print(f"{Fore.YELLOW}⚠ Facebook yêu cầu login để xem group này")

                if skip_login:
                    print(f"{Fore.YELLOW}💡 Group này không phải public hoặc cần login để xem")
                    print(f"{Fore.YELLOW}   Bạn có muốn login không? (y/n)")
                    user_choice = input(f"{Fore.CYAN}> ").strip().lower()

                    if user_choice == 'y':
                        await self.wait_for_login()
                        # Navigate lại sau khi login
                        await self.page.goto(group_url, wait_until='networkidle', timeout=60000)
                        await asyncio.sleep(3)
                    else:
                        print(f"{Fore.RED}✗ Không thể tiếp tục mà không login")
                        return []

            # Scroll và load posts
            await self.scroll_and_load_posts(max_scrolls=50)

            # Extract post links
            posts = await self.extract_post_links(days=days)

            return posts

        except Exception as e:
            print(f"{Fore.RED}✗ Lỗi: {str(e)}")
            raise
        finally:
            # Cleanup
            if self.context:
                await self.context.close()
            if self.playwright:
                await self.playwright.stop()

    def save_results(self, posts: List[dict], output_file: str = None):
        """
        Lưu kết quả ra file

        Args:
            posts: List các posts
            output_file: Đường dẫn file output (mặc định: output/posts_{timestamp}.json)
        """
        if not posts:
            print(f"{Fore.YELLOW}⚠ Không có posts nào để lưu")
            return

        # Tạo output directory
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        # Generate filename nếu không có
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"output/posts_{timestamp}.json"

        # Lưu JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)

        print(f"\n{Fore.GREEN}✓ Đã lưu {len(posts)} posts vào: {output_file}")

        # Lưu cả file text đơn giản (chỉ links)
        text_file = output_file.replace('.json', '_links.txt')
        with open(text_file, 'w', encoding='utf-8') as f:
            for post in posts:
                f.write(f"{post['link']}\n")

        print(f"{Fore.GREEN}✓ Đã lưu danh sách links vào: {text_file}")


async def main():
    """Main function"""
    print(f"{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}   📱 FACEBOOK GROUP POST SCRAPER 📱")
    print(f"{Fore.CYAN}   Lấy tất cả links bài viết mới từ Facebook group")
    print(f"{Fore.CYAN}{'='*70}\n")

    # Get input from user
    group_url = input(f"{Fore.YELLOW}📝 Nhập link Facebook group: {Fore.WHITE}").strip()

    if not group_url:
        print(f"{Fore.RED}✗ Vui lòng nhập link group!")
        return

    # Validate URL
    if 'facebook.com/groups' not in group_url:
        print(f"{Fore.RED}✗ Link không hợp lệ! Vui lòng nhập link Facebook group.")
        return

    days = input(f"{Fore.YELLOW}📅 Lấy posts trong bao nhiêu ngày qua? (mặc định 7): {Fore.WHITE}").strip()
    days = int(days) if days.isdigit() else 7

    # Hỏi về public group
    is_public = input(f"{Fore.YELLOW}🌍 Group này có phải PUBLIC group không? (y/n, mặc định n): {Fore.WHITE}").strip().lower()
    skip_login = is_public == 'y'

    if skip_login:
        print(f"{Fore.CYAN}💡 Sẽ thử truy cập mà không login (chỉ hoạt động với public groups)")
        print(f"{Fore.CYAN}   Nếu không được, tool sẽ yêu cầu login sau")

    headless_input = input(f"{Fore.YELLOW}🖥️  Chạy ẩn browser? (y/n, mặc định n): {Fore.WHITE}").strip().lower()
    headless = headless_input == 'y'

    # Create scraper
    scraper = FacebookGroupScraper(headless=headless)

    try:
        # Scrape
        posts = await scraper.scrape_group(group_url, days=days, skip_login=skip_login)

        # Display results
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.GREEN}🎉 KẾT QUẢ:")
        print(f"{Fore.CYAN}{'='*70}\n")

        for idx, post in enumerate(posts, 1):
            print(f"{Fore.YELLOW}{idx}. {Fore.WHITE}{post['link']}")
            print(f"   {Fore.CYAN}⏰ {post['time_relative']}")
            if post['preview']:
                preview = post['preview'][:100] + "..." if len(post['preview']) > 100 else post['preview']
                print(f"   {Fore.WHITE}💬 {preview}")
            print()

        # Save results
        scraper.save_results(posts)

        print(f"\n{Fore.GREEN}✓ Hoàn thành!")

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠ Đã hủy bởi user")
    except Exception as e:
        print(f"\n{Fore.RED}✗ Lỗi: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
