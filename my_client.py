# # my_client.py
# """
# Amazon Product Page Opener
# - Accepts a product query from the user.
# - Calls the server's 'search_amazon' tool.
# - Automatically opens the resulting Amazon page in the user's browser.
# """

# import asyncio
# import logging
# import webbrowser  # To automatically open the web browser
# from fastmcp import Client

# # --- Configuration ---
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)


# # --- AmazonAssistant Class (Simplified) ---
# class AmazonAssistant:
#     def __init__(self, server_script: str = None):
#         self.server_script = server_script or "my_server.py"
#         self.client = None

#     async def __aenter__(self):
#         """Asynchronously sets up the client."""
#         logger.info("Initializing MCP client...")
#         self.client = Client(self.server_script)
#         await self.client.__aenter__()
#         return self

#     async def __aexit__(self, exc_type, exc_val, exc_tb):
#         """Asynchronously tears down the client."""
#         if self.client:
#             logger.info("Shutting down MCP client.")
#             await self.client.__aexit__(exc_type, exc_val, exc_tb)

#     async def process_query(self, query: str) -> str:
#         """
#         Processes a product query by calling the search_amazon tool 
#         and opening the browser.
#         """
#         try:
#             if not query:
#                 return "Please enter a product name to search for."

#             logger.info(f"Calling MCP tool 'search_amazon' for product: '{query}'")
#             tool_result = await self.client.call_tool("search_amazon", {"query": query})

#             # Check the result from the server
#             if tool_result and tool_result.data:
#                 # If the server found a URL, open it
#                 if 'product_url' in tool_result.data:
#                     url = tool_result.data['product_url']
#                     logger.info(f"Opening browser to Amazon URL: {url}")
#                     webbrowser.open(url)
#                     return f"✅ Opening Amazon page for '{query}' in your browser."
#                 else:
#                     # Otherwise, display the 'not found' message from the server
#                     return f"❌ {tool_result.data.get('message', 'Could not process the request.')}"
            
#             return "❌ Failed to get a valid response from the server."
            
#         except Exception as e:
#             logger.error(f"An error occurred while processing the query: {e}", exc_info=True)
#             return f"Sorry, a critical error occurred: {e}"


# # --- Main Execution Loop ---
# async def main():
#     """The main entry point for the client application."""
#     print("Welcome to the Amazon Product Opener! (Type 'exit' or 'quit' to end)")
    
#     async with AmazonAssistant() as assistant:
#         while True:
#             try:
#                 query = input("\nEnter product name to find on Amazon: ").strip()
#                 if query.lower() in ('exit', 'quit'):
#                     print("Goodbye!")
#                     break
#                 if not query:
#                     continue

#                 print("\n📦 Searching Amazon...")
#                 response = await assistant.process_query(query)
#                 print(response)

#             except KeyboardInterrupt:
#                 print("\nGoodbye!")
#                 break
#             except Exception as e:
#                 logger.error(f"An unexpected error occurred in the main loop: {e}")


# if __name__ == "__main__":
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         logger.info("Application terminated by user.")




# # my_client.py
# """
# Amazon Multi-Product Page Opener
# - Accepts multiple product queries from the user, separated by commas.
# - Calls the server's 'search_amazon' tool for each product concurrently.
# - Automatically opens a separate Amazon page for each product found.
# """

# import asyncio
# import logging
# import webbrowser
# from typing import List, Tuple
# from fastmcp import Client

# # --- Configuration ---
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)


# # --- AmazonAssistant Class (Modified) ---
# class AmazonAssistant:
#     def __init__(self, server_script: str = None):
#         self.server_script = server_script or "my_server.py"
#         self.client = None

#     async def __aenter__(self):
#         """Asynchronously sets up the client."""
#         logger.info("Initializing MCP client...")
#         self.client = Client(self.server_script)
#         await self.client.__aenter__()
#         return self

#     async def __aexit__(self, exc_type, exc_val, exc_tb):
#         """Asynchronously tears down the client."""
#         if self.client:
#             logger.info("Shutting down MCP client.")
#             await self.client.__aexit__(exc_type, exc_val, exc_tb)

#     # [MODIFIED] This function now processes a single product and returns a result tuple
#     # It no longer prints or opens the browser directly.
#     async def find_single_product(self, product_name: str) -> Tuple[str, str, str]:
#         """
#         Processes a single product query and returns its status and result (URL or error message).
#         Returns a tuple: (product_name, status, data)
#         """
#         try:
#             tool_result = await self.client.call_tool("search_amazon", {"query": product_name})

#             if tool_result and tool_result.data:
#                 if 'product_url' in tool_result.data:
#                     # Success: return the URL
#                     url = tool_result.data['product_url']
#                     return (product_name, "SUCCESS", url)
#                 else:
#                     # Failure (not found): return the message from the server
#                     message = tool_result.data.get('message', f"Could not find '{product_name}'.")
#                     return (product_name, "NOT_FOUND", message)
            
#             return (product_name, "ERROR", "Failed to get a valid response from the server.")
            
#         except Exception as e:
#             logger.error(f"Error processing '{product_name}': {e}", exc_info=True)
#             return (product_name, "ERROR", f"A critical error occurred while searching for '{product_name}'.")


# # --- Main Execution Loop (MODIFIED for multi-product search) ---
# async def main():
#     """The main entry point for the client application."""
#     print("Welcome to the Amazon Multi-Product Opener! (Type 'exit' or 'quit' to end)")
    
#     async with AmazonAssistant() as assistant:
#         while True:
#             try:
#                 # Get comma-separated input from the user
#                 query = input("\nEnter product(s) to find on Amazon (separate with commas): ").strip()
#                 if query.lower() in ('exit', 'quit'):
#                     print("Goodbye!")
#                     break

#                 # Split the input string into a list of product names
#                 products_to_search = [p.strip() for p in query.split(',') if p.strip()]

#                 if not products_to_search:
#                     continue

#                 print(f"\n📦 Searching Amazon for {len(products_to_search)} product(s)...")

#                 # Create a list of concurrent tasks, one for each product
#                 tasks = [assistant.find_single_product(p) for p in products_to_search]
                
#                 # Run all search tasks at the same time for speed and efficiency
#                 results = await asyncio.gather(*tasks)

#                 # Process the results after all searches are complete
#                 print("\n--- Search Complete ---")
#                 success_count = 0
#                 for product_name, status, data in results:
#                     if status == "SUCCESS":
#                         # If successful, open the browser tab and print a success message
#                         webbrowser.open(data)
#                         print(f"✅ Opened Amazon page for '{product_name}'.")
#                         success_count += 1
#                     else:
#                         # If not found or an error occurred, print the message from the server
#                         print(f"❌ {data}")
#                 print(f"-----------------------\nFound and opened {success_count} of {len(products_to_search)} products.")

#             except KeyboardInterrupt:
#                 print("\nGoodbye!")
#                 break
#             except Exception as e:
#                 logger.error(f"An unexpected error occurred in the main loop: {e}")


# if __name__ == "__main__":
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         logger.info("Application terminated by user.")



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