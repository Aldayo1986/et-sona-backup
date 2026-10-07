import os
import time
import requests
from urllib.parse import urljoin, urlparse
import re

def download_with_retry(url, filepath, max_retries=5, delay=3):
    """Download a URL with retry logic for 429 errors."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                # Ensure directory exists
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                return True
            elif response.status_code == 429:
                print(f"HTTP 429 for {url}, waiting 60 seconds (attempt {attempt+1}/{max_retries})")
                time.sleep(60)
            else:
                print(f"HTTP {response.status_code} for {url}")
                return False
        except Exception as e:
            print(f"Error downloading {url}: {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)
            else:
                return False
        # Normal delay between requests
        if attempt < max_retries - 1:
            time.sleep(delay)
    return False

def extract_image_urls(html_content, base_url):
    """Extract image URLs from HTML content."""
    # Simple regex to find img src attributes
    img_pattern = r'<img[^>]+src=["\']([^"\']+)["\']'
    urls = re.findall(img_pattern, html_content, re.IGNORECASE)
    # Also check for data-src or other attributes
    data_src_pattern = r'<img[^>]+data-src=["\']([^"\']+)["\']'
    urls.extend(re.findall(data_src_pattern, html_content, re.IGNORECASE))
    
    # Convert to absolute URLs
    absolute_urls = []
    for url in urls:
        if url.startswith('http'):
            absolute_urls.append(url)
        else:
            absolute_urls.append(urljoin(base_url, url))
    return absolute_urls

def download_missing_posts():
    base_dir = '/Users/fernandoalday/et-sona-site'
    missing_file = os.path.join(base_dir, 'missing.txt')
    
    if not os.path.exists(missing_file):
        print("Missing file not found!")
        return
    
    with open(missing_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    print(f"Found {len(urls)} missing URLs to download")
    
    downloaded = 0
    failed = 0
    
    for url in urls:
        print(f"Processing: {url}")
        
        # Determine the local file path
        if url.startswith('https://www.et-sona.com/en/post/'):
            slug = url[len('https://www.et-sona.com/en/post/'):]
            local_path = os.path.join(base_dir, 'www.et-sona.com', 'en', 'post', slug + '.html')
        elif url.startswith('https://www.et-sona.com/post/'):
            slug = url[len('https://www.et-sona.com/post/'):]
            local_path = os.path.join(base_dir, 'www.et-sona.com', 'post', slug + '.html')
        else:
            print(f"Skipping non-post URL: {url}")
            continue
        
        # Skip if already exists
        if os.path.exists(local_path):
            print(f"Already exists: {local_path}")
            downloaded += 1
            continue
        
        # Download the HTML file
        print(f"Downloading HTML: {url}")
        if download_with_retry(url, local_path):
            print(f"Successfully downloaded: {local_path}")
            downloaded += 1
            
            # Now download images referenced in this HTML
            try:
                with open(local_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                image_urls = extract_image_urls(html_content, url)
                print(f"Found {len(image_urls)} image URLs in {local_path}")
                
                for img_url in image_urls:
                    # Determine local path for image
                    parsed = urlparse(img_url)
                    path = parsed.path
                    # Remove leading slash and any query/fragment
                    path = path.split('?')[0].split('#')[0]
                    if path.startswith('/'):
                        path = path[1:]
                    
                    # Images should go under static.wixstatic.com
                    # The URL might be like https://static.wixstatic.com/media/...
                    if 'static.wixstatic.com' in img_url:
                        # Keep the path relative to static.wixstatic.com
                        local_img_path = os.path.join(base_dir, 'static.wixstatic.com', path)
                    else:
                        # For other domains, we'll skip or put in a generic location
                        # For now, skip non-static.wixstatic.com images as per instructions
                        continue
                    
                    # Skip if image already exists
                    if os.path.exists(local_img_path):
                        continue
                    
                    print(f"Downloading image: {img_url}")
                    if download_with_retry(img_url, local_img_path):
                        print(f"Successfully downloaded image: {local_img_path}")
                    else:
                        print(f"Failed to download image: {img_url}")
                    
                    # Delay between image downloads
                    time.sleep(3)
                    
            except Exception as e:
                print(f"Error processing images for {local_path}: {e}")
        else:
            print(f"Failed to download: {url}")
            failed += 1
        
        # Delay between post downloads
        time.sleep(3)
    
    print(f"\nDownload complete. Successfully downloaded: {downloaded}, Failed: {failed}")

if __name__ == '__main__':
    download_missing_posts()