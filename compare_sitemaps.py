import os
import xml.etree.ElementTree as ET

def get_urls_from_sitemap(sitemap_path):
    urls = []
    try:
        tree = ET.parse(sitemap_path)
        root = tree.getroot()
        # namespace
        ns = {'': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        for url_elem in root.findall('.//url', ns):
            loc_elem = url_elem.find('loc', ns)
            if loc_elem is not None and loc_elem.text:
                urls.append(loc_elem.text.strip())
    except Exception as e:
        print(f"Error parsing {sitemap_path}: {e}")
    return urls

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    es_sitemap = os.path.join(base_dir, 'sitemap-es.xml')
    en_sitemap = os.path.join(base_dir, 'sitemap-en.xml')
    
    es_urls = get_urls_from_sitemap(es_sitemap)
    en_urls = get_urls_from_sitemap(en_sitemap)
    
    print(f"Found {len(es_urls)} Spanish URLs in sitemap")
    print(f"Found {len(en_urls)} English URLs in sitemap")
    
    # Convert URLs to expected file paths
    missing_es = []
    missing_en = []
    
    for url in es_urls:
        # Example: https://www.et-sona.com/post/ifi-neo-idsd-3-1
        # We want: www.et-sona.com/post/ifi-neo-idsd-3-1.html
        if url.startswith('https://www.et-sona.com/post/'):
            slug = url[len('https://www.et-sona.com/post/'):]
            file_path = os.path.join(base_dir, 'www.et-sona.com', 'post', slug + '.html')
            if not os.path.isfile(file_path):
                missing_es.append(url)
        else:
            # Other pages? We'll treat similarly but without .html? The task only concerns posts.
            # For safety, we'll ignore non-post URLs for now.
            pass
    
    for url in en_urls:
        if url.startswith('https://www.et-sona.com/en/post/'):
            slug = url[len('https://www.et-sona.com/en/post/'):]
            file_path = os.path.join(base_dir, 'www.et-sona.com', 'en', 'post', slug + '.html')
            if not os.path.isfile(file_path):
                missing_en.append(url)
        else:
            pass
    
    missing_file = os.path.join(base_dir, 'missing.txt')
    with open(missing_file, 'w') as f:
        for url in missing_es:
            f.write(url + '\n')
        for url in missing_en:
            f.write(url + '\n')
    
    print(f"Written {len(missing_es)} missing Spanish and {len(missing_en)} missing English URLs to {missing_file}")

if __name__ == '__main__':
    main()