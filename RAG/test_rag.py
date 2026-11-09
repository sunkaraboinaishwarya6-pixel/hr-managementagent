from rag_database import search_knowledge


question = "How many casual leave days are available per year?"


results = search_knowledge(question, results=3)


print("\n--- RAG SEARCH RESULTS ---\n")


for i, document in enumerate(results["documents"][0], start=1):

    print(f"Result {i}:")
    print(document)
    print("\n" + "-" * 80)