from RAG.rag_database import search_knowledge
from backend.servies.ollama_service import ask_qwen

def ask_hr_with_rag(question):

    results = search_knowledge(question, results=3)

    documents = results["documents"][0]

    context = "\n\n".join(documents)

    prompt = f"""
You are an HR Management AI Assistant.

Answer the user's question using ONLY the information
provided in the knowledge base context below.

If the answer is not available in the context,
say exactly:

Information not found in the knowledge base.

Knowledge Base Context:
{context}

User Question:
{question}

Give a clear and professional answer.
"""

    answer = ""

    for chunk in ask_qwen(prompt):
        answer += chunk

    return answer


if __name__ == "__main__":

    question = "How many casual leave days are available per year?"

    answer = ask_hr_with_rag(question)

    print("\n--- HR AGENT ANSWER ---\n")
    print(answer)