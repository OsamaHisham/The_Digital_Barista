import sqlalchemy
import pandas as pd
import json
import os

# --- Configuration ---

# The JSON file created by scrape_outlets.py
DATA_SOURCE_FILE = "outlets.json"

# The name for our new SQLite database file
DB_FILE = "outlets.db"

# The name of the table we'll create inside the database
TABLE_NAME = "outlets"

# --- Main Script ---

def create_db_from_json():
    """
    Reads the scraped outlets.json file, loads it into a pandas DataFrame,
    and then saves it to a new SQLite database file.
    This creates the "SQL DB" required by the assessment .
    """
    print(f"🚀 Starting DB setup...")

    # --- 1. Find and Load JSON Data ---
    script_dir = os.path.dirname(__file__)
    data_path = os.path.join(script_dir, DATA_SOURCE_FILE)
    
    if not os.path.exists(data_path):
        print(f"❌ Error: Data file not found at {data_path}")
        print("Please run scrape_outlets.py first.")
        return

    print(f"📂 Loading data from {DATA_SOURCE_FILE}...")
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # --- 2. Convert Data to Pandas DataFrame ---
    # This is an easy way to move from JSON to a SQL table structure
    df = pd.DataFrame(data)

    # --- 3. Clean Data for SQL ---
    # SQLite doesn't have a "list" type. We must convert the 'services'
    # list into a plain text string (e.g., comma-separated).
    # The Text2SQL model can easily query this.
    if 'services' in df.columns:
        # .join() creates a string: ["a", "b"] -> "a, b"
        df['services'] = df['services'].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)
    
    print(f"Loaded {len(df)} records into DataFrame.")

    # --- 4. Create SQLite Database ---
    db_path = os.path.join(script_dir, DB_FILE)
    
    # Delete the old DB file if it exists for a fresh start
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed old {DB_FILE}.")

    # Create the connection "engine" to our new SQLite file
    # This line *creates* the outlets.db file
    engine = sqlalchemy.create_engine(f"sqlite:///{db_path}")

    # --- 5. Save DataFrame to SQL Table ---
    print(f"Writing data to table '{TABLE_NAME}' in {DB_FILE}...")
    
    # This is the magic: pandas writes the data, schema, and all
    # to the SQL database.
    df.to_sql(
        TABLE_NAME, 
        engine, 
        index=False,          # Don't save the pandas index column
        if_exists="replace"   # Overwrite the table if it exists
    )

    print("\n🎉 Success! SQLite database created.")
    
    # --- 6. Verify (Optional) ---
    print("\nVerifying database contents (first 3 rows):")
    with engine.connect() as conn:
        result = conn.execute(sqlalchemy.text(f"SELECT * FROM {TABLE_NAME} LIMIT 3")).fetchall()
        for row in result:
            print(row)

# --- Execution ---

if __name__ == "__main__":
    create_db_from_json()