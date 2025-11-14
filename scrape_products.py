import requests
import json
from bs4 import BeautifulSoup
import os

# --- Configuration ---

# The URL of the ZUS Drinkware collection page 
COLLECTION_URL = "https://shop.zuscoffee.com/collections/drinkware"

# We append ".json" to the collection URL to access Shopify's JSON endpoint.
# This is a much more stable method than parsing HTML.
API_URL = f"{COLLECTION_URL}/products.json"

# The name of the file where we'll save our scraped data
OUTPUT_FILE = "products.json"

# --- Main Script ---

def scrape_product_data():
    """
    Fetches product data from the ZUS Drinkware Shopify JSON endpoint
    and saves it to a local JSON file.
    """
    print(f"🚀 Starting scraper for: {COLLECTION_URL}")

    try:
        # 1. Fetch the data from the JSON API endpoint
        # We set a page size limit to ensure we get all items.
        # Shopify's default is ~30, but we can request up to 250.
        params = {'limit': 250}
        response = requests.get(API_URL, params=params)

        # Raise an exception for bad status codes (like 404, 500)
        response.raise_for_status() 

        # 2. Parse the JSON response
        # The response.json() method built into requests decodes the JSON for us
        data = response.json()

        print(f"✅ Found {len(data['products'])} products in the collection.")

        # 3. Process and clean the data
        # We want to transform the raw Shopify data into a simple, clean format
        # for our RAG pipeline.
        
        cleaned_products = []
        for product in data['products']:
            
            # The description is in the 'body_html' field.
            # We use BeautifulSoup to strip the HTML tags (like <p>, <strong>)
            # and get just the plain text.
            description_html = product.get('body_html', '')
            soup = BeautifulSoup(description_html, "html.parser")
            description_text = soup.get_text(separator="\n", strip=True)

            # Get the first available variant's price.
            # Products can have multiple prices (e.g., for different colors).
            # For simplicity, we'll take the first one.
            price = "N/A"
            if product.get('variants'):
                price = product['variants'][0].get('price', 'N/A')

            # Create a clean dictionary for this product
            product_entry = {
                "name": product.get('title', 'No Title'),
                "price": price,
                "description": description_text or "No description available."
            }
            
            cleaned_products.append(product_entry)

        # 4. Save the data to a JSON file 
        print(f"💾 Saving cleaned data to {OUTPUT_FILE}...")
        
        # We save in the same directory as the script
        script_dir = os.path.dirname(__file__)
        output_path = os.path.join(script_dir, OUTPUT_FILE)

        with open(output_path, 'w', encoding='utf-8') as f:
            # json.dump writes the list of dictionaries to the file
            # indent=4 makes it human-readable ("pretty-print")
            json.dump(cleaned_products, f, indent=4, ensure_ascii=False)

        print(f"\n🎉 Success! All {len(cleaned_products)} products have been saved to {OUTPUT_FILE}.")

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# --- Execution ---

if __name__ == "__main__":
    # This block ensures the scrape_product_data() function
    # is called only when you run the script directly
    # (e.g., "python scrape_products.py")
    scrape_product_data()