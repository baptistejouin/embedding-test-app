"""Embedding utilities for the application."""
import os
from typing import List, Dict, Any
import numpy as np
from langchain_openai import OpenAIEmbeddings
from app.schema import IssueCollection
from app.db import SessionLocal, insert_document, reset_db, init_db
from tqdm import tqdm

# Initialize the embeddings model
embeddings_model = OpenAIEmbeddings(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    model="text-embedding-ada-002"
)


def get_embedding(text: str) -> List[float]:
    """Get embedding for a text using the OpenAI API."""
    return embeddings_model.embed_query(text)


def process_document(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Process a document to prepare it for database storage."""
    # Generate embeddings for the document content
    embedding = get_embedding(doc['content'])
    
    return {
        "id": doc['id'],
        "title": doc['title'],
        "content": doc['content'],
        "metadata": doc['metadata'],
        "embedding": embedding
    }


def embed_documents_from_file(file_path: str, batch_size: int = 10) -> int:
    """Process documents from a JSON file and store them in the database."""
    # Load issues from the file
    issue_collection = IssueCollection.from_file(file_path)
    
    # Convert issues to documents
    documents = issue_collection.to_documents()
    total_docs = len(documents)
    
    print(f"Processing {total_docs} documents...")
    
    # Process documents in batches
    db = SessionLocal()
    try:
        for i in tqdm(range(0, total_docs, batch_size), desc="Processing batches"):
            batch = documents[i:i + batch_size]
            for doc in batch:
                processed = process_document(doc)
                insert_document(
                    db,
                    processed["id"],
                    processed["title"], 
                    processed["content"],
                    processed["metadata"],
                    processed["embedding"]
                )
            db.commit()  # Commit after each batch
        return total_docs
    finally:
        db.close()


def setup_database():
    """Initialize the database tables."""
    init_db()
    print("Database initialized successfully.")


def reset_database():
    """Reset the database by dropping and recreating tables."""
    reset_db()
    print("Database reset successfully.")


def query_similar(query_text: str, limit: int = 5) -> List[Dict]:
    """Query documents similar to the given text."""
    # Generate embedding for the query
    query_embedding = get_embedding(query_text)
    
    # Search for similar documents
    db = SessionLocal()
    try:
        similar_docs = []
        from app.db import search_similar
        results = search_similar(db, query_embedding, limit)
        
        for doc in results:
            similar_docs.append({
                "id": doc.id,
                "title": doc.title,
                "content": doc.content[:200] + "..." if len(doc.content) > 200 else doc.content,
                "metadata": doc.metadata
            })
        
        return similar_docs
    finally:
        db.close()