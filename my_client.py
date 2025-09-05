# my_client.py
"""
Amazon Multi-Product Page Opener
- Accepts multiple product queries from the user, separated by commas, 'and', or 'or'.
- Calls the server's 'search_amazon' tool for each product concurrently.
- Automatically opens a separate Amazon page for each product found.
"""

import asyncio
import logging
import webbrowser
import re  # [MODIFIED] Import the regular expression module
from typing import List, Tuple
from fastmcp import Client

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# --- AmazonAssistant Class (Unchanged from previous version) ---
class AmazonAssistant:
    def __init__(self, server_script: str = None):
        self.server_script = server_script or "my_server.py"
        self.client = None

    async def __aenter__(self):
        """Asynchronously sets up the client."""
        logger.info("Initializing MCP client...")
        self.client = Client(self.server_script)
        await self.client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Asynchronously tears down the client."""
        if self.client:
            logger.info("Shutting down MCP client.")
            await self.client.__aexit__(exc_type, exc_val, exc_tb)

    async def find_single_product(self, product_name: str) -> Tuple[str, str, str]:
        """
        Processes a single product query and returns its status and result (URL or error message).
        Returns a tuple: (product_name, status, data)
        """
        try:
            tool_result = await self.client.call_tool("search_amazon", {"query": product_name})

            if tool_result and tool_result.data:
                if 'product_url' in tool_result.data:
                    url = tool_result.data['product_url']
                    return (product_name, "SUCCESS", url)
                else:
                    message = tool_result.data.get('message', f"Could not find '{product_name}'.")
                    return (product_name, "NOT_FOUND", message)
            
            return (product_name, "ERROR", "Failed to get a valid response from the server.")
            
        except Exception as e:
            logger.error(f"Error processing '{product_name}': {e}", exc_info=True)
            return (product_name, "ERROR", f"A critical error occurred while searching for '{product_name}'.")


# --- Main Execution Loop ---
async def main():
    """The main entry point for the client application."""
    print("Welcome to the Amazon Multi-Product Opener! (Type 'exit' or 'quit' to end)")
    
    async with AmazonAssistant() as assistant:
        while True:
            try:
                query = input("\nEnter product(s) to find : ").strip()
                if query.lower() in ('exit', 'quit'):
                    print("Goodbye!")
                    break

                # --- [MODIFIED] This is the line we upgraded ---
                # It now uses re.split to handle multiple separators, ignoring case (e.g., 'AND' vs 'and').
                # The pattern r'\s+and\s+|\s+or\s+|,' splits by:
                #   \s+and\s+  -> the word 'and' surrounded by spaces
                #   \s+or\s+   -> the word 'or' surrounded by spaces
                #   ,          -> a comma
                products_to_search = [p.strip() for p in re.split(r'\s+and\s+|\s+or\s+|,', query, flags=re.IGNORECASE) if p.strip()]
                # --- End of modification ---

                if not products_to_search:
                    continue

                print(f"\n📦 Searching Amazon for {len(products_to_search)} product(s)...")

                tasks = [assistant.find_single_product(p) for p in products_to_search]
                results = await asyncio.gather(*tasks)

                print("\n--- Search Complete ---")
                success_count = 0
                for product_name, status, data in results:
                    if status == "SUCCESS":
                        webbrowser.open(data)
                        print(f"✅ Opened Amazon page for '{product_name}'.")
                        success_count += 1
                    else:
                        print(f"❌ {data}")
                print(f"-----------------------\nFound and opened {success_count} of {len(products_to_search)} products.")

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                logger.error(f"An unexpected error occurred in the main loop: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application terminated by user.")