import re
import time
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def extract_emails_from_html(html):
    emails = set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", html))
    emails.update(re.findall(r"mailto:([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", html))
    return emails

def is_valid_url(url, base_domain):
    try:
        parsed = urlparse(url)
        return parsed.netloc.endswith(base_domain)
    except:
        return False

def crawl(driver, url, base_domain, visited_urls, emails_found,
          depth=0, max_depth=3, max_links_per_page=30):
    if url in visited_urls or depth > max_depth:
        return

    print(f"Crawling (depth {depth}): {url}")
    visited_urls.add(url)

    try:
        driver.set_page_load_timeout(20)
        driver.get(url)

        # Wait for presence of any email link or fallback to body
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='@'], a[href^='mailto:']"))
            )
        except TimeoutException:
            pass

        # Extra wait to allow JS email rendering
        time.sleep(2)

        page_html = driver.page_source
        emails_found.update(extract_emails_from_html(page_html))

        soup = BeautifulSoup(page_html, "html.parser")
        links_crawled = 0

        for link in soup.find_all('a', href=True):
            if links_crawled >= max_links_per_page:
                break

            href = link['href'].strip()
            if href.startswith(("mailto:", "tel:", "#", "javascript:")):
                continue

            next_url = urljoin(url, href).split('#')[0]
            if is_valid_url(next_url, base_domain):
                crawl(driver, next_url, base_domain, visited_urls, emails_found,
                      depth + 1, max_depth, max_links_per_page)
                links_crawled += 1

    except (WebDriverException, TimeoutException) as e:
        print(f"Failed to load {url}: {e}")

def scrape_emails(starting_url, max_depth=3, max_links_per_page=30):
    visited_urls = set()
    emails_found = set()
    base_domain = urlparse(starting_url).netloc

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        crawl(driver, starting_url, base_domain, visited_urls, emails_found,
              depth=0, max_depth=max_depth, max_links_per_page=max_links_per_page)
    finally:
        driver.quit()

    return sorted(emails_found)

if __name__ == "__main__":
    url = "https://sendcrux.com"  # Replace with any URL you want to test
    emails = scrape_emails(url, max_depth=4, max_links_per_page=50)
    print(f"\n--- Emails found ({len(emails)}) ---")
    for e in emails:
        print(e)
