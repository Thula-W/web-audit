import json
from urllib.parse import urlparse, urljoin


def safe_json_parse(text):
    try:
        return json.loads(text)
    except:
        # fallback: try extracting JSON substring
        import re
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise Exception("Failed to parse JSON from AI response")
    
    
def validate_output(result):
    if not isinstance(result, dict):
        raise Exception("Invalid AI output format")

    if "insights" not in result or "recommendations" not in result:
        raise Exception("Missing required keys")

    if not isinstance(result["recommendations"], list):
        raise Exception("Recommendations must be a list")
    

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
