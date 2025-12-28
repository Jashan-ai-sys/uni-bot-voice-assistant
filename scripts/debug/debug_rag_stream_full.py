import asyncio
import os
import sys
import traceback
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# Force utf-8 for console
sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()

async def debug_stream():
    print("--- FULL DEBUG STREAM TEST ---")
    
    # Import exactly as in rag_pipeline.py
    try:
        from rag_pipeline import get_vectorstore, identify_intent
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        import google.generativeai as genai
        
        query = "Where is block 34?"
        student_id = None
        
        print(f"Query: {query}")

        # 1. Vector Search Debug
        print("1. Testing Vector Search...")
        vectorstore = get_vectorstore()
        search_filter = identify_intent(query)
        print(f"   Filter: {search_filter} (Type: {type(search_filter)})")
        
        docs = vectorstore.max_marginal_relevance_search(query, k=5, filter=search_filter)
        print(f"   Docs found: {len(docs)}")
        
        for i, d in enumerate(docs):
            print(f"   --- Doc {i} ---")
            print(f"   Type: {type(d)}")
            print(f"   Metadata Type: {type(d.metadata)}")
            print(f"   Metadata Value: {d.metadata}")
            
            if isinstance(d.metadata, list):
                print("   !!! CRITICAL: Metadata is a LIST, expected DICT !!!")
            
            m = d.metadata.get('source', 'unknown')
            print(f"   Doc source: {m}")
            
        # 2. Context Construction
        print("2. Building Context...")
        context_parts = []
        for doc in docs:
            source = doc.metadata.get('source', 'unknown')
            content = f"Source: {source}\nContent: {doc.page_content}"
            context_parts.append(content)
        context = "\n\n---\n\n".join(context_parts)
        print(f"   Context length: {len(context)}")

        # 3. LLM Setup
        print("3. Testing LLM Stream...")
        # replicate config
        genai.configure(transport='rest')
        llm = ChatGoogleGenerativeAI(
            model="models/gemini-2.0-flash", 
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        template = """Answer: {context} \n Q: {query}""" # simplified for test
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | llm | StrOutputParser()
        
        print("   Starting stream loop...")
        async for chunk in chain.astream({"context": context, "query": query}):
            print(f"   CHUNK: {chunk}", end="|", flush=True)
            
        print("\n--- DONE ---")

    except Exception:
        print("\n!!! EXCEPTION CAUGHT !!!")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_stream())
