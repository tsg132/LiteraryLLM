import os
import glob
import psycopg2
from sentence_transformers import SentenceTransformer

DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "rag_db")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "secret")

# Make a connection
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASS,
    host=DB_HOST,
    port=DB_PORT
)
cur = conn.cursor()

# All-MiniLM for embedding
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def split_into_paragraphs(text):
    paras = text.split("\n\n")
    paras = [p.strip() for p in paras if p.strip()]
    return paras

def ingest_file(file_path, title):
    with open(file_path, "r", encoding="utf-8") as f:
        raw = f.read()
    paragraphs = split_into_paragraphs(raw)

    for p in paragraphs:
        emb = embedder.encode([p])[0]  # shape: (384,) or (768,) depending on model
        emb_str = "[" + ",".join(f"{x:.6f}" for x in emb) + "]"
        insert_sql = """
          INSERT INTO documents (title, text, embedding)
          VALUES (%s, %s, %s::vector)
        """
        cur.execute(insert_sql, (title, p, emb_str))

def main():
    # Create table if not exists
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS documents (
      id SERIAL PRIMARY KEY,
      title TEXT,
      text TEXT,
      embedding vector(384)
    );
    """
    cur.execute(create_table_sql)

    # Ingest all txt files from data/ folder
    files = glob.glob("/app/data/*.txt")
    for f in files:
        title = os.path.basename(f).replace(".txt", "")
        ingest_file(f, title)

    conn.commit()
    cur.close()
    conn.close()
    print("Ingestion complete.")

if __name__ == "__main__":
    main()
