import re
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

def extract_emails_from_html(html):
    return set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", html))

def is_valid_url(url, base_domain):
    try:
        parsed = urlparse(url)
        return parsed.netloc.endswith(base_domain)
    except:
        return False

def crawl(url, base_domain, visited_urls, emails_found, depth=0, max_depth=1):
    if url in visited_urls or depth > max_depth:
        return

    visited_urls.add(url)
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        html = response.text
        emails_found.update(extract_emails_from_html(html))

        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a', href=True):
            href = link['href']
            next_url = urljoin(url, href).split('#')[0]
            if is_valid_url(next_url, base_domain):
                crawl(next_url, base_domain, visited_urls, emails_found, depth + 1, max_depth)
    except requests.RequestException:
        pass

def scrape_emails(starting_url, max_depth=1):
    visited_urls = set()
    emails_found = set()
    base_domain = urlparse(starting_url).netloc
    crawl(starting_url, base_domain, visited_urls, emails_found, 0, max_depth)
    return sorted(emails_found)
