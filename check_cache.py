import sys
sys.path.append('src')

print("="*60)
print("📦 CACHE CONTENTS - LPU UMS Chatbot")
print("="*60)

# Check FAQ Cache
print("\n1️⃣ FAQ CACHE (Pre-loaded)")
print("-" * 60)
import json
with open('faq_cache.json', 'r', encoding='utf-8') as f:
    faq_cache = json.load(f)

print(f"Total FAQ Entries: {len(faq_cache)}")
print("\nQuestions in FAQ Cache:")
for i, question in enumerate(faq_cache.keys(), 1):
    print(f"{i}. {question}")

# Check Smart Cache
print("\n\n2️⃣ SMART CACHE (Runtime)")
print("-" * 60)
try:
    from smart_cache import smart_cache
    
    stats = smart_cache.get_stats()
    print(f"Total Cached Entries: {stats['cached_entries']}")
    print(f"Cache Hits: {stats['hits']}")
    print(f"Cache Misses: {stats['misses']}")
    print(f"Hit Rate: {stats['hit_rate']}")
    print(f"API Calls Saved: {stats['api_calls_saved']}")
    
    if smart_cache.cache:
        print("\nCached Questions:")
        for i, (key, entry) in enumerate(list(smart_cache.cache.items())[:10], 1):
            print(f"{i}. {entry['query'][:60]}...")
    else:
        print("\n⚠️ Smart cache is empty (no queries processed yet)")
        
except Exception as e:
    print(f"⚠️ Smart cache not available: {e}")

# Check if enhanced_cache.json exists
print("\n\n3️⃣ ENHANCED CACHE FILE")
print("-" * 60)
import os
if os.path.exists('enhanced_cache.json'):
    with open('enhanced_cache.json', 'r', encoding='utf-8') as f:
        enhanced = json.load(f)
    print(f"Total Entries: {len(enhanced)}")
    print("\nSample Entries:")
    for i, (key, entry) in enumerate(list(enhanced.items())[:5], 1):
        print(f"{i}. {entry.get('query', 'N/A')[:60]}...")
else:
    print("⚠️ Enhanced cache file not created yet")

print("\n" + "="*60)
print("✅ Cache Analysis Complete!")
print("="*60)
