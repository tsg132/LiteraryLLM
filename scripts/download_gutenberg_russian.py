import requests
from bs4 import BeautifulSoup
import os
import time
from tqdm import tqdm

BASE_URL = "https://www.gutenberg.org"
SEARCH_URL = "https://www.gutenberg.org/ebooks/search/?query=Russian+Literature&submit_search=Go%21"
SAVE_DIR = "data/gutenberg_russian_lit"

os.makedirs(SAVE_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def get_book_links():
    """Find all book links by paginating through the search results."""
    book_links = set()
    page_url = SEARCH_URL

    while True:
        response = requests.get(page_url, headers=HEADERS)
        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract book links
        for link in soup.select(".booklink a[href]"):
            href = link["href"]
            if href.startswith("/ebooks/"):
                book_links.add(BASE_URL + href)

        # Find the "Next" button
        next_page = soup.find("a", text="Next")
        if next_page:
            page_url = BASE_URL + next_page["href"]
            time.sleep(2)  # ✅ Avoid overloading Gutenberg servers
        else:
            break  # No more pages

    return list(book_links)

# def get_plain_text_url(book_page):
#     """Extract the UTF-8 plain text URL from a book's main page."""
#     response = requests.get(book_page, headers=HEADERS)
#     if response.status_code != 200:
#         print(f"❌ Failed to fetch {book_page}")
#         return None

#     soup = BeautifulSoup(response.text, "html.parser")

#     # Find the first plain text file link
#     for link in soup.select("a[href]"):
#         href = link["href"]
#         if "txt" in href and "utf-8" in href:
#             return BASE_URL + href if href.startswith("/files/") else href

#     return None  # No text file found

def get_plain_text_url(book_page):
    """Extract the UTF-8 plain text URL from a book's main page."""
    response = requests.get(book_page, headers=HEADERS)
    if response.status_code != 200:
        print(f"❌ Failed to fetch {book_page}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Find the first plain text file link
    for link in soup.select("a[href]"):
        href = link["href"]
        if "txt" in href and "utf-8" in href:
            # Ensure the URL is absolute
            full_url = BASE_URL + href if href.startswith("/") else href
            return full_url

    return None  # No text file found

def download_book(title, text_url):
    """Download and save the book as a .txt file."""
    response = requests.get(text_url, headers=HEADERS)
    if response.status_code != 200:
        return

    file_path = os.path.join(SAVE_DIR, f"{title}.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(response.text)

    print(f"✅ Saved: {file_path}")

# Start Scraping
book_pages = get_book_links()

for book_page in tqdm(book_pages[:600], desc="Downloading Books"):  # Limit to 600
    title = book_page.split("/")[-1]  # Use book ID as filename
    text_url = get_plain_text_url(book_page)
    
    if text_url:
        download_book(title, text_url)
    
    time.sleep(2)  # ✅ Respect Gutenberg's rate limits