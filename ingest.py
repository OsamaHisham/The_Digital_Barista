import json
import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

# from langchain.docstore.document import Document
from langchain_core.documents import Document

# from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter


# --- Configuration ---
JSON_PATH = "products.json"       # The data from our first script
INDEX_PATH = "faiss_index"        # The folder to save our vector store
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100

def create_vector_store():
    """
    Reads product data from JSON, creates Document objects,
    splits them, embeds them, and saves them to a local FAISS index.
    This is the "ingestion script" .
    """
    
    print("🚀 Starting vector store ingestion...")

    # 1. Load the product data from our JSON file
    if not os.path.exists(JSON_PATH):
        print(f"❌ Error: {JSON_PATH} not found.")
        return

    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        products_data = json.load(f)

    print(f"✅ Loaded {len(products_data)} products from {JSON_PATH}.")

    # 2. Convert JSON data into LangChain 'Document' objects
    # We will format the content so the AI can understand it easily.
    all_documents = []
    for product in products_data:
        # Create a single string of "page content" for each product
        content = f"Product Name: {product['name']}\n" \
                  f"Price: {product['price']}\n" \
                  f"Description: {product['description']}"
        
        # Store the original source name in the metadata
        metadata = {
            "source": product['name'],
            "price": product['price']
        }
        
        all_documents.append(Document(page_content=content, metadata=metadata))

    # 3. Split the documents into smaller chunks
    # This helps the RAG model find more precise pieces of information.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, 
        chunk_overlap=CHUNK_OVERLAP
    )
    split_docs = text_splitter.split_documents(all_documents)
    
    print(f"📄 Split {len(all_documents)} documents into {len(split_docs)} chunks.")

    # 4. Create embeddings
    # This checks for your OPENAI_API_KEY environment variable.
    try:
        embeddings = OpenAIEmbeddings()
        print("✅ OpenAI embeddings loaded.")
    except Exception as e:
        print(f"❌ Error loading OpenAI embeddings: {e}")
        print("👉 Please make sure your OPENAI_API_KEY environment variable is set.")
        return

    # 5. Create the vector store from the chunks and save it
    # This is the step that "ingests ZUS product docs into a vector store" 
    print("⏳ Creating FAISS vector store... (This may take a moment)")
    
    # FAISS.from_documents creates the index in memory
    db = FAISS.from_documents(split_docs, embeddings)
    
    # .save_local saves it to disk
    db.save_local(INDEX_PATH)
    
    print(f"\n🎉 Success! Vector store saved to {INDEX_PATH}")


if __name__ == "__main__":
    create_vector_store()