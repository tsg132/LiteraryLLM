import requests
from bs4 import BeautifulSoup

import os

import time

from tqdm import tqdm


BASE_URL = "https://en.wikipedia.org"
MAIN_PAGE = "https://en.wikipedia.org/wiki/Russian_literature"
SAVE_DIR = "data/wikipedia_russian_lit"

os.makedirs(SAVE_DIR, exist_ok=True)

def fetch_wikipedia(url):
    """Scrape the text content from Wikipedia page"""

    response = requests.get(url)

    if response.status_code != 200:

        print(f"Failed to fetch: {url}")

        return None

    soup = BeautifulSoup(response.text, "html.parser")

    content = ""

    for paragraph in soup.select("div.mw-parser-output > p"):

        content += paragraph.text + "\n"

    return content.strip()

def save_text(title, content):

    """Save text content as a .txt file"""

    file_path = os.path.join(SAVE_DIR, f"{title.replace(' ',  '_')}.txt")

    with open(file_path, 'w', encoding="utf-8") as f:

        f.write(content)

def get_internal_links(url):

    """Extract all internal Wikipedia links from a page."""

    response = requests.get(url)

    if response.status_code != 200:

        print("Failed to fetch links")

        return []
    
    soup = BeautifulSoup(response.text, "html.parser")

    links = []

    # for a_tag in soup.select("div.mw-parser-output a[href]"):

    #     link = a_tag["href"]

    #     if link.startswith("'/wiki/") and ":" not in link: # Ignore non-article links

    #         links.append(BASE_URL + link)

    for a_tag in soup.select("p a[href], ul a[href], ol a[href], table a[href]"):
        link = a_tag["href"]
        if link.startswith("/wiki/") and not any(ignore in link for ignore in [":", "#"]):
            full_url = BASE_URL + link
            links.append(full_url)    

    return list(set(links))

print(f"Scraping main page: {MAIN_PAGE}")

main_text = fetch_wikipedia(MAIN_PAGE)

if main_text:

    save_text("Russian_Literature", main_text)

linked_pages = get_internal_links(MAIN_PAGE)

print(f"Found {len(linked_pages)} linked Wikipedia pages.")

for link in tqdm(linked_pages, desc="Scraping linked pages"):

    title = link.split("/")[-1]

    content = fetch_wikipedia(link)

    if content:

        save_text(title, content)

    time.sleep(2)



