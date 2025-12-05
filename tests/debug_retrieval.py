import sys
import os
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

DB_PATH = "./db"

def debug_retrieval(query):
    output_file = "tests/retrieval_result.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"🔍 Searching for: '{query}'\n")
        try:
            if not os.path.exists(DB_PATH):
                f.write(f"❌ DB not found at {DB_PATH}\n")
                return

            embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
            vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
            
            docs = vectorstore.similarity_search(query, k=5)
            
            f.write(f"📄 Found {len(docs)} documents:\n")
            found = False
            for i, doc in enumerate(docs):
                source = doc.metadata.get('source', 'unknown')
                content_snippet = doc.page_content.replace('\n', ' ')
                f.write(f"  {i+1}. [{source}]\n{content_snippet}\n\n")
                
                if "Block 32" in doc.page_content:
                    found = True
                    f.write("     ✅ 'Block 32' found in this chunk!\n")
            
            if not found:
                f.write("❌ 'Block 32' NOT found in top 5 results.\n")
                
        except Exception as e:
            f.write(f"❌ Error: {e}\n")
    print(f"Debug output written to {output_file}")

if __name__ == "__main__":
    debug_retrieval("Where is Block 32?")
