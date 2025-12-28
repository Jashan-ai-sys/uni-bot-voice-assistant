#!/usr/bin/env python3
"""
Compare BGE vs Gemini Embeddings for Retrieval Quality
Usage: python tests/compare_embeddings.py
"""

import sys
import os

# Add parent to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.embeddings_router import get_embeddings
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv

load_dotenv()

# Test queries
TEST_QUERIES = [
    ("What are the hostel fees?", ["hostel", "fees", "accommodation"]),
    ("How do I apply for scholarships?", ["scholarship", "financial", "application"]),
    ("What is the attendance policy?", ["attendance", "75%", "policy"]),
    ("Where is the library located?", ["library", "block", "location"]),
    ("What are the exam eligibility criteria?", ["exam", "eligibility", "attendance"])
]

def test_retrieval(query, embeddings_model, provider_name, index_name):
    """Test retrieval with given embeddings model"""
    try:
        vectorstore = PineconeVectorStore(
            index_name=index_name,
            embedding=embeddings_model
        )
        
        results = vectorstore.similarity_search_with_score(query, k=3)
        
        print(f"\n{'=' * 60}")
        print(f"Provider: {provider_name}")
        print(f"Query: '{query}'")
        print(f"{'=' * 60}")
        
        for i, (doc, score) in enumerate(results, 1):
            print(f"\n{i}. [Score: {score:.4f}]")
            print(f"   {doc.page_content[:150]}...")
            if doc.metadata:
                print(f"   Source: {doc.metadata.get('source', 'N/A')}")
        
        return results
        
    except Exception as e:
        print(f"Error with {provider_name}: {e}")
        return []


def compare_quality(bge_results, gemini_results, expected_keywords):
    """Compare quality between two result sets"""
    bge_score = sum(1 for doc, _ in bge_results[:3] 
                    if any(kw.lower() in doc.page_content.lower() for kw in expected_keywords))
    
    gemini_score = sum(1 for doc, _ in gemini_results[:3]
                       if any(kw.lower() in doc.page_content.lower() for kw in expected_keywords))
    
    print(f"\n📊 Relevance Score:")
    print(f"   BGE: {bge_score}/3 docs contain expected keywords")
    print(f"   Gemini: {gemini_score}/3 docs contain expected keywords")
    
    if gemini_score > bge_score:
        print("   ✅ Winner: Gemini")
    elif bge_score > gemini_score:
        print("   ✅ Winner: BGE")
    else:
        print("   🤝 Tie")
    
    return {"bge": bge_score, "gemini": gemini_score}


def main():
    print("🧪 Embedding Comparison Test")
    print("=" * 60)
    
    # Load models
    print("\n📦 Loading embedding models...")
    try:
        bge_emb = get_embeddings("huggingface")
        print("   ✅ BGE loaded (384 dims)")
    except Exception as e:
        print(f"   ❌ BGE failed: {e}")
        return
    
    try:
        gemini_emb = get_embeddings("gemini")
        query_vec = gemini_emb.embed_query("test")
        print(f"   ✅ Gemini loaded ({len(query_vec)} dims)")
    except Exception as e:
        print(f"   ❌ Gemini failed: {e}")
        print("   💡 Make sure GEMINI_API_KEY is set in .env")
        return
    
    # Get index name
    index_name = os.getenv("PINECONE_INDEX_NAME", "uni-bot-index")
    print(f"\n🌲 Using Pinecone index: {index_name}")
    
    # Run tests
    total_scores = {"bge": 0, "gemini": 0}
    
    for query, expected_kw in TEST_QUERIES:
        print(f"\n\n{'#' * 60}")
        print(f"# Test Query: {query}")
        print(f"{'#' * 60}")
        
        # Test BGE
        bge_results = test_retrieval(query, bge_emb, "BGE", index_name)
        
        # Test Gemini
        gemini_results = test_retrieval(query, gemini_emb, "Gemini (text-embedding-004)", index_name)
        
        # Compare
        scores = compare_quality(bge_results, gemini_results, expected_kw)
        total_scores["bge"] += scores["bge"]
        total_scores["gemini"] += scores["gemini"]
    
    # Final results
    print(f"\n\n{'=' * 60}")
    print("📊 FINAL RESULTS")
    print(f"{'=' * 60}")
    print(f"Total Relevant Docs (out of {len(TEST_QUERIES) * 3}):")
    print(f"   BGE: {total_scores['bge']}")
    print(f"   Gemini: {total_scores['gemini']}")
    
    if total_scores["gemini"] > total_scores["bge"]:
        print(f"\n🏆 WINNER: Gemini (+{total_scores['gemini'] - total_scores['bge']} more relevant docs)")
        print("\n💡 Recommendation: Consider migrating to Gemini embeddings")
    elif total_scores["bge"] > total_scores["gemini"]:
        print(f"\n🏆 WINNER: BGE (+{total_scores['bge'] - total_scores['gemini']} more relevant docs)")
        print("\n💡 Recommendation: Keep current BGE embeddings")
    else:
        print("\n🤝 TIE: Both models performed equally")
        print("\n💡 Recommendation: Keep BGE (faster, no API latency)")


if __name__ == "__main__":
    main()
