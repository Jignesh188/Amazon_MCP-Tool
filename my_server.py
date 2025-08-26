# my_server.py
"""
Amazon Product Search Server
- Defines a single tool to find a product on Amazon.
- Scrapes the search results to find the first product link using multiple patterns for reliability.
"""

import sys
import io
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from fastmcp import FastMCP, Context
from my_config import AMAZON_SEARCH_URL, USER_AGENT, REQUEST_TIMEOUT

# --- Boilerplate setup ---
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

mcp = FastMCP("Amazon Search Server")
# --- [MODIFIED] Using headers that more closely mimic a real browser ---
headers = {
    'User-Agent': USER_AGENT,
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Referer': 'https://www.google.com/',
}

# --- [NEW] Helper Function for Amazon Scraping (More Robust) ---
def fetch_amazon_product_page(url: str, query: str) -> str:
    """
    Fetches the Amazon search results and tries multiple selectors to find the first product link.
    This makes the scraper more resilient to changes in Amazon's HTML.
    """
    try:
        search_url = url.format(query=requests.utils.quote(query))
        resp = requests.get(search_url, headers=headers, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # --- List of potential selectors to find the product link ---
        # We will try these in order.
        selectors = [
            'div[data-asin] h2 a.a-link-normal',  # Primary, most common selector for product titles
            'a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal', # A common fallback
            'div[data-asin] a[href*="/dp/"]' # A broad selector looking for any product link inside a result
        ]

        link_tag = None
        for selector in selectors:
            link_tag = soup.select_one(selector)
            if link_tag:
                # If we found a link with this selector, stop searching
                print(f"Found product link using selector: '{selector}'") # Debug message
                break
        
        if link_tag and link_tag.get('href'):
            # The scraped link is often relative, so we join it with the base URL.
            product_link = urljoin('https://www.amazon.com', link_tag['href'])
            return product_link
            
        # If none of the selectors worked
        print("Scraping failed: None of the selectors found a matching product link.", file=sys.stderr)
        return None
        
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Amazon might be blocking the request.", file=sys.stderr)
        return None
    except Exception as e:
        print(f"An error occurred during scraping: {e}", file=sys.stderr)
        return None


# --- The single MCP tool for Amazon product search ---
@mcp.tool()
def search_amazon(query: str, ctx: Context = None) -> dict:
    """Searches for a product on Amazon and returns the link to the first result."""
    product_url = fetch_amazon_product_page(AMAZON_SEARCH_URL, query)
    
    if product_url:
        # Success: return the URL in the data payload
        return {"product_url": product_url}
    else:
        # Failure: return an error message
        return {"message": f"Sorry, I could not find '{query}' on Amazon. The website structure may have changed."}


if __name__ == "__main__":
    mcp.run()