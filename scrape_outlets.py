import requests
import json
import os
from bs4 import BeautifulSoup

# --- Configuration ---
OUTLETS_URL = "https://zuscoffee.com/category/store/kuala-lumpur-selangor/"
OUTPUT_FILE = "outlets.json"

# --- Main Script ---
def scrape_outlet_data_html_fixed():
    """
    Fetches outlet data from the ZUS WordPress store locator page .
    This version is fixed using the exact HTML structure provided.
    """
    print(f"🚀 Starting HTML scraper (Fixed) for: {OUTLETS_URL}")

    try:
        response = requests.get(OUTLETS_URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # The old script was correct: all outlets are in <article> tags.
        outlet_articles = soup.find_all("article")
        
        if not outlet_articles:
            print("❌ No <article> tags found. Page structure has changed.")
            return

        print(f"✅ Found {len(outlet_articles)} potential outlet entries. Parsing...")

        cleaned_outlets = []
        for article in outlet_articles:
            
            name = "Not Found"
            address = "Not Found"

            # --- Extract Name ---
            # Based on your HTML, the name is in a <p> tag with this class:
            name_tag = article.find("p", class_="elementor-heading-title")
            if name_tag:
                name = name_tag.get_text(strip=True)

            # --- Extract Location (Address) ---
            # Based on your HTML, the address is in a <div> with data-id "a5ba7a6"
            address_container = article.find("div", {"data-id": "a5ba7a6"})
            if address_container:
                # Find the first <p> tag inside that container that has text
                for p in address_container.find_all("p"):
                    if p.get_text(strip=True):
                        address = p.get_text(strip=True)
                        break # Found it, stop looking

            # --- Handle Missing Data (Placeholders) ---
            # The HTML does not list hours or services.
            # We add placeholders to satisfy the DB schema .
            hours = "Not Listed" 
            services = ["Dine-in", "Takeaway"] # Default services

            # --- Create a clean dictionary ---
            if name != "Not Found" and address != "Not Found":
                outlet_entry = {
                    "name": name,
                    "location": address, # As required by 
                    "hours": hours,      # As required by 
                    "services": services # As required by 
                }
                cleaned_outlets.append(outlet_entry)

        # 5. Save the data to a JSON file
        print(f"💾 Saving {len(cleaned_outlets)} cleaned outlets to {OUTPUT_FILE}...")
        
        script_dir = os.path.dirname(__file__)
        output_path = os.path.join(script_dir, OUTPUT_FILE)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(cleaned_outlets, f, indent=4, ensure_ascii=False)

        print(f"\n🎉 Success! Data saved to {OUTPUT_FILE}.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# --- Execution ---
if __name__ == "__main__":
    scrape_outlet_data_html_fixed()