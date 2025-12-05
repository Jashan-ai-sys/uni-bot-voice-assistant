from langchain_community.document_loaders import PyPDFLoader
import os

file_path = r"c:\Users\WIN11\lpu bot RAG\uni-bot\data\hostel\emeergency_numbers.pdf"

print(f"Checking file: {file_path}")

try:
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    
    print(f"Loaded {len(docs)} pages.")
    for i, doc in enumerate(docs):
        print(f"\n--- Page {i+1} Content ---")
        print(doc.page_content[:500]) # Print first 500 chars
        print("------------------------")
        
        # Check for specific keywords
        if "fire" in doc.page_content.lower():
            print("✅ Found 'fire' in content")
        else:
            print("❌ 'fire' NOT found in content")
            
except Exception as e:
    print(f"Error loading PDF: {e}")
