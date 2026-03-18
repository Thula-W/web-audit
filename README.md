# AI-Powered Website Audit Tool

## Overview
This project is a lightweight AI-powered Website Audit Tool that analyzes a single webpage and provides:

1. **Factual metrics** extracted deterministically  
2. **AI-generated insights and recommendations** grounded in those metrics  

The system is intentionally designed to be **simple, structured, and cost-efficient**, aligning with real-world agency needs such as SEO, UX, and conversion optimization.

---

## Features

### 1. Factual Metrics Extraction
- Total word count  
- Heading counts (H1–H3)  
- CTA count (buttons + primary action links)  
- Internal vs external links  
- Image count  
- % of images missing alt text  
- Meta title & description  

---

### 2. AI Insights
Structured analysis covering:
- SEO structure  
- Messaging clarity  
- CTA usage  
- Content depth  
- UX / structural concerns  

---

### 3. Recommendations
- 3–5 prioritized, actionable recommendations  
- Each tied directly to extracted metrics  

---

## Architecture Overview

    [ User Input URL ]
            ↓
    [ Scraper Layer ]
      - Requests + BeautifulSoup
      - Extracts structured metrics
            ↓
    [ Structured Data Layer ]
      - Clean JSON object
            ↓
    [ AI Analysis Layer ]
      - LLM receives ONLY structured metrics
            ↓
    [ Output Formatter ]
      - JSON output (insights + recommendations)


### Key Design Principle
**Strict separation between deterministic scraping and AI-based reasoning**

---

## AI Design Decisions

### 1. AI Grounded in Structured Data
The LLM receives only:
- Extracted metrics (counts, percentages, metadata)

It does NOT receive:
- Raw HTML  
- Full page text  

This ensures:
- Lower token usage  
- Faster responses  
- Reduced hallucination risk  
- More consistent outputs  

---

### 2. No Raw Text Sent to LLM
Instead of sending full page content:
- The system relies on structured signals (headings, CTAs, metadata)

**Reason:**
- Large webpages significantly increase token cost  
- Many insights (SEO, CTA usage, structure) can be derived from metrics alone  

---

### 3. Structured Prompting
- Strict system prompt defines responsibilities  
- Output enforced as JSON  
- Insights must reference metrics  

This improves:
- Consistency  
- Parseability  
- Evaluation clarity  

---

## Trade-offs

### 1. Not Sending Page Content to LLM
I considered sending parsed page text to the LLM for richer insights (especially for messaging clarity and UX).

**Trade-off:**
- Large pages → high token usage → increased cost and latency  

**Decision:**
- Use only structured metrics for analysis  

**Impact:**
- Slightly less depth in messaging analysis  
- Much better efficiency and scalability  

---

### 2. Heuristic CTA Detection
CTA detection uses:
- Keywords (e.g., "Get Started", "Contact")  
- HTML classes (e.g., `btn`, `cta`)  
- ARIA labels  

**Trade-off:**
- Not perfectly accurate  

**Reason:**
- Keeps solution lightweight  
- Avoids overengineering for assignment scope  

---

### 3. Static Scraping Only
Uses:
- `requests`  
- `BeautifulSoup`  

**Trade-off:**
- Does not capture JavaScript-rendered content  

**Reason:**
- Simpler and faster  
- Keeps focus on AI + system design  

---

## What I Would Improve with More Time

### 1. Dynamic Website Support
Use:
- **Playwright** or **Puppeteer**

This would:
- Render JavaScript-heavy pages  
- Improve accuracy of metrics  

---

### 2. Improved CTA Detection
Enhancements:
- DOM position analysis (above-the-fold detection)  
- Visual importance signals  
- ML/LLM-based classification  

---

### 3. Hybrid AI Approach
- Send **selected content sections only** (not full page)  
- Use chunking or embeddings  

Benefits:
- Better insight quality  
- Controlled token usage  

---

### 4. Advanced SEO Analysis
Add:
- Keyword density  
- Heading hierarchy validation  
- Semantic structure checks  

---

### 5. Scoring System
Introduce:
- SEO score  
- UX score  
- Conversion score  

---

## How to Run

### Local Setup

```bash
git clone <https://github.com/Thula-W/web-audit.git>
pip install -r requirements.txt
python run.py
