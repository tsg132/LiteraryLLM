from fastapi import FastAPI, Query
import os
import psycopg2
from sentence_transformers import SentenceTransformer
from typing import List

app = FastAPI()

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

embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

@app.get("/retrieve")
def retrieve_documents(query: str, k: int = 3):
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
    
    results = [{"title": row[0], "text": row[1]} for row in rows]
    return {"query": query, "results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
