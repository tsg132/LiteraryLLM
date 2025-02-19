import os
import psycopg2
from sentence_transformers import SentenceTransformer
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "rag_db")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "secret")

conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASS,
    host=DB_HOST,
    port=DB_PORT
)
cur = conn.cursor()

# The same embedder for queries
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# We use something small like flan-t5-base
model_name = "google/flan-t5-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

def retrieve_top_k(query, k=3):
    emb = embedder.encode([query])[0]
    emb_str = "[" + ",".join(f"{x:.6f}" for x in emb) + "]"
    sql = f"""
        SELECT title, text
        FROM documents
        ORDER BY embedding <-> '{emb_str}'
        LIMIT {k};
    """
    cur.execute(sql)
    rows = cur.fetchall()
    return rows  # list of (title, text)

def generate_rag_response(query):
    top_docs = retrieve_top_k(query)
    context = "\n\n".join([f"[{doc[0]}]\n{doc[1]}" for doc in top_docs])

    prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
    inputs = tokenizer(prompt, return_tensors="pt")
    output_ids = model.generate(**inputs, max_new_tokens=100)
    return tokenizer.decode(output_ids[0], skip_special_tokens=True)

def main():
    # Quick test
    user_query = "What are major themes in War and Peace?"
    answer = generate_rag_response(user_query)
    print("RAG Answer:", answer)

if __name__ == "__main__":
    main()

