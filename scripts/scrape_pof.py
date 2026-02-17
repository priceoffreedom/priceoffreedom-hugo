#!/usr/bin/env python3
"""
Scraper for priceoffreedom.us
Downloads all pages, images, and converts content to Hugo-ready markdown.
"""

import os
import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

BASE_URL = "https://priceoffreedom.us"
OUTPUT_DIR = "/home/mrbell/Desktop/webdev/pof-scraped"
IMAGES_DIR = os.path.join(OUTPUT_DIR, "static", "images")
CONTENT_DIR = os.path.join(OUTPUT_DIR, "content")

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
})

# All known pages from the sitemap
PAGES = [
    "/",
    "/reviews/",
    "/media/",
    "/price-of-freedom-volunteer-appreciation-dinner/",
]


def ensure_dirs():
    """Create output directory structure."""
    for d in [IMAGES_DIR, CONTENT_DIR, os.path.join(CONTENT_DIR, "posts")]:
        os.makedirs(d, exist_ok=True)


def download_image(url):
    """Download an image and return the local path relative to /static/."""
    if not url or not url.startswith("http"):
        return url

    parsed = urlparse(url)
    # Only download images from the site itself
    if "priceoffreedom.us" not in parsed.netloc:
        return url

    # Build local filename preserving path structure
    path = parsed.path.lstrip("/")
    local_path = os.path.join(IMAGES_DIR, path)
    local_dir = os.path.dirname(local_path)
    os.makedirs(local_dir, exist_ok=True)

    if os.path.exists(local_path):
        print(f"  [SKIP] Already downloaded: {path}")
        return f"/images/{path}"

    try:
        print(f"  [DL] {url}")
        resp = SESSION.get(url, timeout=30)
        resp.raise_for_status()
        with open(local_path, "wb") as f:
            f.write(resp.content)
        time.sleep(0.5)  # Be polite
        return f"/images/{path}"
    except Exception as e:
        print(f"  [ERR] Failed to download {url}: {e}")
        return url


def extract_images(soup):
    """Find and download all images from a page."""
    images = []
    for img in soup.find_all("img"):
        src = img.get("src", "")
        srcset = img.get("srcset", "")
        alt = img.get("alt", "")

        if src:
            full_url = urljoin(BASE_URL, src)
            local = download_image(full_url)
            images.append({"src": local, "alt": alt, "original": full_url})

        # Also grab highest resolution from srcset
        if srcset:
            for entry in srcset.split(","):
                entry = entry.strip()
                if entry:
                    parts = entry.split()
                    if parts:
                        img_url = urljoin(BASE_URL, parts[0])
                        download_image(img_url)

    return images


def html_to_markdown(element):
    """Convert an HTML element to markdown text."""
    if element is None:
        return ""

    lines = []
    for child in element.children:
        if isinstance(child, str):
            text = child.strip()
            if text:
                lines.append(text)
            continue

        if not hasattr(child, 'name'):
            continue

        tag = child.name

        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(tag[1])
            text = child.get_text(strip=True)
            if text:
                lines.append(f"\n{'#' * level} {text}\n")

        elif tag == 'p':
            text = process_inline(child)
            if text.strip():
                lines.append(f"\n{text}\n")

        elif tag == 'blockquote':
            text = child.get_text(strip=True)
            if text:
                lines.append(f"\n> {text}\n")

        elif tag in ['ul', 'ol']:
            for i, li in enumerate(child.find_all('li', recursive=False)):
                prefix = f"{i+1}." if tag == 'ol' else "-"
                text = li.get_text(strip=True)
                lines.append(f"{prefix} {text}")
            lines.append("")

        elif tag == 'img':
            src = child.get('src', '')
            alt = child.get('alt', '')
            if src:
                local = download_image(urljoin(BASE_URL, src))
                lines.append(f"\n![{alt}]({local})\n")

        elif tag == 'figure':
            img = child.find('img')
            caption = child.find('figcaption')
            if img:
                src = img.get('src', '')
                alt = img.get('alt', '')
                cap = caption.get_text(strip=True) if caption else alt
                local = download_image(urljoin(BASE_URL, src))
                lines.append(f"\n![{cap}]({local})\n")
                if caption:
                    lines.append(f"*{cap}*\n")

        elif tag == 'a':
            href = child.get('href', '')
            text = child.get_text(strip=True)
            if text and href:
                lines.append(f"[{text}]({href})")

        elif tag == 'div':
            # Recurse into divs
            inner = html_to_markdown(child)
            if inner.strip():
                lines.append(inner)

        elif tag in ['section', 'article', 'main', 'header', 'footer']:
            inner = html_to_markdown(child)
            if inner.strip():
                lines.append(inner)

        elif tag == 'br':
            lines.append("")

        else:
            text = child.get_text(strip=True)
            if text:
                lines.append(text)

    return "\n".join(lines)


def process_inline(element):
    """Process inline elements within a paragraph."""
    parts = []
    for child in element.children:
        if isinstance(child, str):
            parts.append(child)
            continue

        if not hasattr(child, 'name'):
            continue

        tag = child.name
        text = child.get_text(strip=True)

        if tag == 'strong' or tag == 'b':
            parts.append(f"**{text}**")
        elif tag == 'em' or tag == 'i':
            parts.append(f"*{text}*")
        elif tag == 'a':
            href = child.get('href', '')
            parts.append(f"[{text}]({href})")
        elif tag == 'img':
            src = child.get('src', '')
            alt = child.get('alt', '')
            local = download_image(urljoin(BASE_URL, src))
            parts.append(f"![{alt}]({local})")
        elif tag == 'br':
            parts.append("  \n")
        else:
            parts.append(text)

    return "".join(parts)


def get_page_content(soup):
    """Extract the main content area from the page."""
    # Try various WordPress content selectors
    content = (
        soup.find('main')
        or soup.find('div', class_='entry-content')
        or soup.find('article')
        or soup.find('div', id='content')
        or soup.find('div', class_='site-content')
        or soup.find('div', class_='wp-site-blocks')
    )
    return content


def get_page_title(soup):
    """Extract the page title."""
    # Try og:title first
    og = soup.find('meta', property='og:title')
    if og and og.get('content'):
        return og['content']

    title_tag = soup.find('title')
    if title_tag:
        text = title_tag.get_text(strip=True)
        # Remove site name suffix
        text = re.sub(r'\s*[–-]\s*Price of Freedom Museum\s*$', '', text)
        return text

    h1 = soup.find('h1')
    if h1:
        return h1.get_text(strip=True)

    return "Untitled"


def scrape_page(path):
    """Scrape a single page and return structured data."""
    url = urljoin(BASE_URL, path)
    print(f"\n{'='*60}")
    print(f"Scraping: {url}")
    print(f"{'='*60}")

    resp = SESSION.get(url, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, 'html.parser')

    title = get_page_title(soup)
    print(f"  Title: {title}")

    # Download all images on the page
    images = extract_images(soup)
    print(f"  Found {len(images)} images")

    # Extract main content as markdown
    content_el = get_page_content(soup)
    markdown = html_to_markdown(content_el) if content_el else ""

    # Get meta description
    meta_desc = ""
    desc_tag = soup.find('meta', attrs={'name': 'description'})
    if desc_tag:
        meta_desc = desc_tag.get('content', '')

    # Get featured image
    og_image = soup.find('meta', property='og:image')
    featured = ""
    if og_image and og_image.get('content'):
        featured = download_image(og_image['content'])

    # Get publish date
    date_tag = soup.find('meta', property='article:published_time')
    date = ""
    if date_tag:
        date = date_tag.get('content', '')[:10]

    modified_tag = soup.find('meta', property='article:modified_time')
    modified = ""
    if modified_tag:
        modified = modified_tag.get('content', '')[:10]

    return {
        "title": title,
        "path": path,
        "markdown": markdown,
        "description": meta_desc,
        "featured_image": featured,
        "date": date or modified or "2025-01-01",
        "images": images,
    }


def save_raw_html(path, html_content):
    """Save the raw HTML for reference."""
    raw_dir = os.path.join(OUTPUT_DIR, "raw_html")
    os.makedirs(raw_dir, exist_ok=True)

    filename = path.strip("/").replace("/", "_") or "index"
    filepath = os.path.join(raw_dir, f"{filename}.html")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"  Saved raw HTML: {filepath}")


def save_as_hugo_content(page_data):
    """Save scraped page data as Hugo markdown."""
    path = page_data["path"]

    # Determine output path
    if path == "/":
        filepath = os.path.join(CONTENT_DIR, "_index.md")
    elif path.startswith("/price-of-freedom-volunteer"):
        filepath = os.path.join(CONTENT_DIR, "posts", "volunteer-appreciation-dinner.md")
    else:
        slug = path.strip("/")
        filepath = os.path.join(CONTENT_DIR, slug, "_index.md")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

    # Build front matter
    front_matter = f"""---
title: "{page_data['title']}"
date: {page_data['date']}
draft: false"""

    if page_data['description']:
        front_matter += f'\ndescription: "{page_data["description"]}"'

    if page_data['featured_image']:
        front_matter += f'\nfeatured_image: "{page_data["featured_image"]}"'

    front_matter += "\n---\n"

    content = front_matter + "\n" + page_data["markdown"]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"  Saved Hugo content: {filepath}")


def save_raw_pages():
    """Also save the raw HTML for each page."""
    for path in PAGES:
        url = urljoin(BASE_URL, path)
        try:
            resp = SESSION.get(url, timeout=30)
            resp.raise_for_status()
            save_raw_html(path, resp.text)
            time.sleep(0.5)
        except Exception as e:
            print(f"  [ERR] Could not save raw HTML for {path}: {e}")


def main():
    print("Price of Freedom Museum - Site Scraper")
    print("=" * 60)

    ensure_dirs()

    # Scrape all pages
    all_pages = []
    for path in PAGES:
        try:
            data = scrape_page(path)
            all_pages.append(data)
            save_as_hugo_content(data)
            time.sleep(1)  # Be polite between requests
        except Exception as e:
            print(f"  [ERR] Failed to scrape {path}: {e}")

    # Save raw HTML too
    print("\n\nSaving raw HTML copies...")
    save_raw_pages()

    # Summary
    print("\n\n" + "=" * 60)
    print("SCRAPING COMPLETE")
    print("=" * 60)
    print(f"\nOutput directory: {OUTPUT_DIR}")
    print(f"  content/     - Hugo markdown files")
    print(f"  static/images/ - Downloaded images")
    print(f"  raw_html/    - Original HTML for reference")

    total_images = sum(len(p["images"]) for p in all_pages)
    print(f"\nPages scraped: {len(all_pages)}")
    print(f"Images found: {total_images}")

    # List all downloaded images
    img_count = 0
    for root, dirs, files in os.walk(IMAGES_DIR):
        img_count += len(files)
    print(f"Images downloaded: {img_count}")


if __name__ == "__main__":
    main()
