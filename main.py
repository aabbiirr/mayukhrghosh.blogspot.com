import os
import requests
import base64
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class BlogSpotScraper:
    def __init__(self, blog_sitemap_url, output_dir):
        self.blog_sitemap_url = blog_sitemap_url
        self.output_dir = output_dir

    def get_post_links(self):
        # simple get request is sufficient 
        response = requests.get(self.blog_sitemap_url)
        if response.status_code == 200:
            # parse the xml to get the urls within
            soup = BeautifulSoup(response.text, "lxml-xml")
            return [loc.text for loc in soup.find_all("loc")]
        else:
            print("Error: Sitemap not available.")
            return []

    @staticmethod
    def capture_fullpage_screenshot(url, filename):
        # Use chrome dev tools
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        try:
            driver.get(url)

            # Chrome DevTools Protocol to screen height
            total_height = driver.execute_script("return document.body.scrollHeight")
            driver.set_window_size(1920, total_height)

            # Chrome DevTools Protocol to capture 
            screenshot_data = driver.execute_cdp_cmd("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": True})
            screenshot_bytes = base64.b64decode(screenshot_data["data"])

            # Simply Save, it may fail 
            screenshot_path = os.path.join(OUTPUT_DIR, filename)
            with open(screenshot_path, "wb") as f:
                f.write(screenshot_bytes)

            print(f"Screenshot saved: {screenshot_path}")
        
        except Exception as e:
            print(f"Capture error {url}: {e}")
        
        finally:
            driver.quit()

if __name__ == "__main__":
    # Sitemap url from blogspot
    BLOG_SITEMAP_URL = "https://mayukhrghosh.blogspot.com/sitemap.xml"

    # Full page Screenshots will be saved to this folder
    # Always create the directory at the very beginning to avoid unnceccessary errors
    OUTPUT_DIR = "screenshots"
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Create scrapper instance
    blogSpotScraper = BlogSpotScraper(BLOG_SITEMAP_URL, OUTPUT_DIR)

    # Lets get all the post links
    post_links = blogSpotScraper.get_post_links()

    # Traverse and capture 
    for index, post_url in enumerate(post_links):
        filename = f"post_{index + 1}.png"
        BlogSpotScraper.capture_fullpage_screenshot(post_url, filename)
