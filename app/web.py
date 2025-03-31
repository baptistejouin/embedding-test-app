"""Web interface for the embedding application."""
from fastapi import FastAPI, Depends, HTTPException, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from app.db import get_db, get_all_documents
from app.embedding import query_similar

app = FastAPI(title="Embedding Test App")

# HTML Templates
templates = Jinja2Templates(directory="app/templates")

# Basic HTML template string since we're not using an actual templates directory
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Embedding Test App</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        h1 { color: #333; }
        .container { max-width: 1000px; margin: 0 auto; }
        .search-box { margin: 20px 0; padding: 10px; }
        .search-box input { padding: 8px; width: 70%; }
        .search-box button { padding: 8px 15px; background: #4CAF50; color: white; border: none; cursor: pointer; }
        .document { margin: 10px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .document h3 { margin-top: 0; }
        .metadata { color: #666; font-size: 0.9em; }
        .nav-links { margin: 20px 0; }
        .nav-links a { margin-right: 15px; color: #4CAF50; text-decoration: none; }
        .nav-links a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Embedding Test App</h1>
        
        <div class="nav-links">
            <a href="/">Home</a>
            <a href="/embeddings">View Embeddings</a>
        </div>
        
        <div class="search-box">
            <form action="/search" method="post">
                <input type="text" name="query" placeholder="Enter your search query...">
                <button type="submit">Search</button>
            </form>
        </div>
        
        <h2>{% if search_results %}Search Results{% else %}All Documents (total: {{ total_count }}){% endif %}</h2>
        
        {% if search_results %}
            {% for doc in search_results %}
            <div class="document">
                <h3>{{ doc.title }}</h3>
                <p>{{ doc.content }}</p>
                <div class="metadata">
                    <strong>ID:</strong> {{ doc.id }}
                    {% if doc.metadata %}
                    <div><strong>Metadata:</strong> {{ doc.metadata }}</div>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        {% else %}
            {% for doc in documents %}
            <div class="document">
                <h3>{{ doc.title }}</h3>
                <p>{{ doc.content[:200] }}...</p>
                <div class="metadata">
                    <strong>ID:</strong> {{ doc.id }}
                </div>
            </div>
            {% endfor %}
        {% endif %}
    </div>
</body>
</html>
"""

EMBEDDINGS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Embedding Vectors - Embedding Test App</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        h1 { color: #333; }
        .container { max-width: 1200px; margin: 0 auto; }
        .nav-links { margin: 20px 0; }
        .nav-links a { margin-right: 15px; color: #4CAF50; text-decoration: none; }
        .nav-links a:hover { text-decoration: underline; }
        .embedding-card { 
            margin: 15px 0; 
            padding: 15px; 
            border: 1px solid #ddd; 
            border-radius: 5px;
            background: #f9f9f9;
        }
        .embedding-vector {
            font-family: monospace;
            white-space: pre-wrap;
            word-break: break-all;
            font-size: 0.9em;
            background: #fff;
            padding: 10px;
            border-radius: 3px;
            margin-top: 10px;
        }
        .metadata { color: #666; font-size: 0.9em; margin-top: 10px; }
        .pagination { margin-top: 20px; text-align: center; }
        .pagination a { 
            margin: 0 5px; 
            padding: 5px 10px; 
            border: 1px solid #ddd; 
            text-decoration: none; 
            color: #4CAF50;
        }
        .pagination a:hover { background: #f0f0f0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Embedding Vectors</h1>
        
        <div class="nav-links">
            <a href="/">Home</a>
            <a href="/embeddings">View Embeddings</a>
        </div>

        <div class="pagination">
            {% if page > 1 %}
            <a href="/embeddings?page={{ page - 1 }}">Previous</a>
            {% endif %}
            <span>Page {{ page }} of {{ total_pages }}</span>
            {% if page < total_pages %}
            <a href="/embeddings?page={{ page + 1 }}">Next</a>
            {% endif %}
        </div>

        {% for doc in documents %}
        <div class="embedding-card">
            <h3>{{ doc.title }}</h3>
            <div class="metadata">
                <strong>ID:</strong> {{ doc.id }}
                {% if doc.get_metadata() %}
                <div><strong>Metadata:</strong> {{ doc.get_metadata() }}</div>
                {% endif %}
            </div>
            <div class="embedding-vector">
                {{ doc.get_embedding_str() }}
            </div>
        </div>
        {% endfor %}

        <div class="pagination">
            {% if page > 1 %}
            <a href="/embeddings?page={{ page - 1 }}">Previous</a>
            {% endif %}
            <span>Page {{ page }} of {{ total_pages }}</span>
            {% if page < total_pages %}
            <a href="/embeddings?page={{ page + 1 }}">Next</a>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

# Create the templates directory and index.html at runtime
import os
if not os.path.exists("app/templates"):
    os.makedirs("app/templates")
    
with open("app/templates/index.html", "w") as f:
    f.write(HTML_TEMPLATE)

with open("app/templates/embeddings.html", "w") as f:
    f.write(EMBEDDINGS_TEMPLATE)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    total_count = get_all_documents(db, count_only=True)
    documents = get_all_documents(db)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "documents": documents,
        "search_results": None,
        "total_count": total_count
    })


@app.post("/search", response_class=HTMLResponse)
async def search(request: Request, query: str = Form(...)):
    results = query_similar(query)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "search_results": results,
        "documents": []
    })


@app.get("/api/documents")
def get_documents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    documents = get_all_documents(db, skip=skip, limit=limit)
    return [{"id": doc.id, "title": doc.title, "content": doc.content, "metadata": doc.metadata} for doc in documents]


@app.get("/api/search")
def search_documents(query: str, limit: int = 5):
    results = query_similar(query, limit)
    return results


@app.get("/embeddings", response_class=HTMLResponse)
async def view_embeddings(request: Request, page: int = 1, db: Session = Depends(get_db)):
    per_page = 10
    documents = get_all_documents(db)
    total_pages = (len(documents) + per_page - 1) // per_page
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_documents = documents[start_idx:end_idx]
    
    return templates.TemplateResponse("embeddings.html", {
        "request": request,
        "documents": paginated_documents,
        "page": page,
        "total_pages": total_pages
    })