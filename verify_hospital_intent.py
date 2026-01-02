from src.rag_pipeline import identify_intent

def test():
    queries = [
        "give me unihospital number",
        "hospital emergency",
        "where is the hospital"
    ]
    for q in queries:
        print(f"'{q}' -> {identify_intent(q)}")

if __name__ == "__main__":
    test()
