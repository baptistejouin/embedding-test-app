"""Database utilities for the embedding app."""
import os
from sqlalchemy import create_engine, Column, String, JSON, Integer, MetaData, Table, select, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pgvector.sqlalchemy import Vector
import numpy as np

# Get database URL from environment or use default
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/embeddings")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Document(Base):
    """SQLAlchemy model for documents with vector embeddings."""
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    document_metadata = Column(JSON, nullable=True)
    embedding = Column(Vector(1536))  # Default dimension for OpenAI embeddings
    
    def __repr__(self):
        return f"<Document(id='{self.id}', title='{self.title}')>"
    
    def get_metadata(self):
        """Get document metadata."""
        return self.document_metadata
    
    def get_embedding_str(self):
        """Convert embedding vector to a string representation."""
        if self.embedding is None:
            return "No embedding available"
        return str(self.embedding.tolist())


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    # Create the vector extension first
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    
    Base.metadata.create_all(bind=engine)


def reset_db():
    """Drop and recreate all tables."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def insert_document(db, doc_id, title, content, metadata, embedding):
    """Insert a document with its embedding into the database."""
    doc = Document(
        id=doc_id,
        title=title,
        content=content,
        document_metadata=metadata,
        embedding=embedding
    )
    db.add(doc)
    db.commit()
    return doc


def search_similar(db, query_embedding, limit=10):
    """Search for documents similar to the query embedding."""
    # Convert embedding to numpy array if it's not already
    if not isinstance(query_embedding, np.ndarray):
        query_embedding = np.array(query_embedding)
        
    # Create a query to find the most similar documents
    stmt = select(Document).order_by(Document.embedding.cosine_distance(query_embedding)).limit(limit)
    result = db.execute(stmt)
    return result.scalars().all()


def get_all_documents(db, skip=0, limit=100, count_only=False):
    """Get all documents from the database.
    
    Args:
        db: Database session
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        count_only: If True, returns only the total count of documents
    """
    if count_only:
        stmt = select(Document)
        result = db.execute(stmt)
        return len(result.scalars().all())
    
    stmt = select(Document).offset(skip).limit(limit)
    result = db.execute(stmt)
    return result.scalars().all()