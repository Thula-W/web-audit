import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re


def extract_links(soup, base_url):
    """
    Robustly extracts and classifies unique internal and external links.
    """
    parsed_base = urlparse(base_url)
    base_domain = parsed_base.netloc

    # Using sets to ensure we only count UNIQUE destinations (SEO best practice)
    internal_links = set()
    external_links = set()

    # 1. Capture all 'a' tags safely
    for link in soup.find_all('a'):
        # 2. Defensive check: safely get href without crashing if missing
        href = link.get('href')
        if not href:
            continue
            
        href = href.strip()

        # 3. Filter Noise: skip non-navigational protocols and UI fragments
        if href.startswith(('mailto:', 'tel:', 'javascript:', '#')) or not href:
            continue

        # 4. Normalization: convert relative paths (/about) to absolute URLs
        full_url = urljoin(base_url, href)
        parsed_href = urlparse(full_url)
        link_domain = parsed_href.netloc

        # 5. Classification Logic: Handle subdomains (e.g., blog.example.com) as internal
        if link_domain == base_domain or link_domain.endswith(f".{base_domain}"):
            internal_links.add(full_url)
        else:
            external_links.add(full_url)

    return {
        "total_unique": len(internal_links) + len(external_links),
        "internal_count": len(internal_links),
        "external_count": len(external_links),
    }

def extract_ctas(soup):
    cta_keywords = [
        "buy", "sign up", "get started", "contact", "download",
        "subscribe", "join", "start free", "book", "request",
        "try", "learn more"
    ]

    def is_cta(tag):
        text = tag.get_text(strip=True).lower()
        classes = " ".join(tag.get("class", [])).lower()
        aria = tag.get("aria-label", "").lower()

        # Heuristic signals
        keyword_match = any(k in text for k in cta_keywords)
        class_signal = any(k in classes for k in ["btn", "cta", "primary", "action"])
        aria_signal = any(k in aria for k in cta_keywords)

        return keyword_match or class_signal or aria_signal

    # Buttons + anchor tags
    candidates = soup.find_all(['a', 'button'])

    ctas = []
    for tag in candidates:
        if is_cta(tag):
            text = tag.get_text(strip=True)
            if text:  # avoid empty UI elements
                ctas.append(text)

    # Remove duplicates
    ctas = list(set(ctas))

    return ctas

def get_metrics(url: str) -> dict:
    """
    Extract factual metrics from a single webpage.
    
    Args:
        url: The URL to scrape
        
    Returns:
        Dictionary containing word count, headings, CTAs, links, images, and meta tags
    """
    try:
        response = requests.get(
            url,
            headers={'User-Agent': 'WebsiteAuditTool/1.0'},
            timeout=10,
            verify=False  # Disable SSL verification for dev/testing
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Word count
        text = soup.get_text()
        words = text.split()
        word_count = len(words)
        
        # Headings: count + text list per level
        def heading_texts(tag_name):
            return [h.get_text(strip=True) for h in soup.find_all(tag_name) if h.get_text(strip=True)]

        h1_texts = heading_texts('h1')
        h2_texts = heading_texts('h2')
        h3_texts = heading_texts('h3')

        links = extract_links(soup, url)
        
        # Images and alt text
        images = soup.find_all('img')
        image_count = len(images)
        missing_alt = sum(1 for img in images if not img.get('alt') or img.get('alt').strip() == '')
        alt_percentage = (
            ((image_count - missing_alt) / image_count * 100)
            if image_count > 0
            else 100
        )
        
        # Meta title and description
        title_tag = soup.find('title')
        meta_title = title_tag.get_text(strip=True) if title_tag else ''
        meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
        meta_desc = meta_desc_tag.get('content', '').strip() if meta_desc_tag else ''
        
        ctas = extract_ctas(soup)
        return {
            'word_count': word_count,
            'headings': {
                'h1': {'count': len(h1_texts), 'texts': h1_texts},
                'h2': {'count': len(h2_texts), 'texts': h2_texts},
                'h3': {'count': len(h3_texts), 'texts': h3_texts}
            },
            'ctas': {
                'count': len(ctas),
            },
            'links': {
                'total': links['total_unique'],
                'internal': links['internal_count'],
                'external': links['external_count'],
            },
            'images': {
                'count': image_count,
                'missing_alt_count': missing_alt,
                'alt_text_percentage': round(alt_percentage, 2)
            },
            'meta': {
                'title': meta_title,
                'description': meta_desc
            }
        }
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error fetching {url}: {str(e)}")
    except Exception as e:
        raise Exception(f"Error scraping {url}: {str(e)}")
