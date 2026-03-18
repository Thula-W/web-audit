import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re


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
        
        # CTAs: approximate detection based on text patterns
        cta_keywords = re.compile(
            r'\b(buy|sign up|learn more|contact|call|download|get started|subscribe|click here|join|start free)\b',
            re.I
        )
        links = soup.find_all('a')
        buttons = soup.find_all('button')
        ctas = []
        for tag in links + buttons:
            text_content = tag.get_text(strip=True)
            if text_content and cta_keywords.search(text_content):
                ctas.append(text_content)
        
        # Links: internal vs external (with text)
        total_links = len(links)
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        internal_links = []
        external_links = []
        for link in links:
            href = link.get('href')
            text_content = link.get_text(strip=True)
            if not href:
                continue
            parsed_href = urlparse(href)
            if parsed_href.netloc == domain or not parsed_href.netloc:
                internal_links.append(text_content)
            else:
                external_links.append(text_content)
        
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
        
        return {
            'word_count': word_count,
            'headings': {
                'h1': {'count': len(h1_texts), 'texts': h1_texts},
                'h2': {'count': len(h2_texts), 'texts': h2_texts},
                'h3': {'count': len(h3_texts), 'texts': h3_texts}
            },
            'ctas': {
                'count': len(ctas),
                'items': ctas
            },
            'links': {
                'total': total_links,
                'internal': len(internal_links),
                'external': len(external_links)
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