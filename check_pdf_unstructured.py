from langchain_community.document_loaders import UnstructuredPDFLoader
import os

file_path = r"c:\Users\WIN11\lpu bot RAG\uni-bot\data\hostel\emeergency_numbers.pdf"

print(f"Checking file with UnstructuredPDFLoader: {file_path}")

try:
    loader = UnstructuredPDFLoader(file_path, mode="elements", strategy="hi_res")
    docs = loader.load()
    
    print(f"Loaded {len(docs)} elements.")
    for i, doc in enumerate(docs[:5]):
        print(f"\n--- Element {i+1} Content ---")
        print(doc.page_content[:500])
        print("------------------------")
        
        if "fire" in doc.page_content.lower():
            print("✅ Found 'fire' in content")
            
except Exception as e:
    print(f"Error loading PDF: {e}")
