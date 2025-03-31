# Embedding Test App with LangChain and Postgres

This application demonstrates how to create and query vector embeddings using LangChain and PostgreSQL with pgvector extension. The entire setup is containerized with Docker for easy deployment.

## Features

- Generate embeddings for text documents using OpenAI's embedding model
- Store embeddings in a PostgreSQL database with pgvector extension
- Perform similarity search on the stored embeddings
- Simple web interface to view documents and search similar content
- CLI to manage database and embed documents from JSON files

## Prerequisites

- Docker and Docker Compose
- OpenAI API key

## Quick Start

1. Clone this repository:

   ```bash
   git clone <repository-url>
   cd embedding-app
   ```

2. Create a `.env` file with your OpenAI API key:

   ```bash
   echo "OPENAI_API_KEY=your-api-key-here" > .env
   ```

3. Start the application with Docker Compose:

   ```bash
   docker-compose up -d
   ```

4. Set up the database:

   ```bash
   docker exec embedding-app python -m app.main setup
   ```

5. Embed sample documents:

   ```bash
   docker exec embedding-app python -m app.main embed data/sample.json
   ```

6. Access the web interface at: http://localhost:8080

## JSON Structure

The application expects JSON files with document data in the following format:

```json
{
  "documents": [
    {
      "id": "unique-id",
      "title": "Document Title",
      "content": "Document text content to be embedded",
      "metadata": {
        "author": "Author Name",
        "category": "Category",
        "date": "2023-01-01"
      }
    }
  ]
}
```

You can also provide an array of documents directly:

```json
[
  {
    "id": "unique-id",
    "title": "Document Title",
    "content": "Document text content to be embedded",
    "metadata": {
      "key": "value"
    }
  }
]
```

## CLI Commands

The application provides several commands:

```bash
# Set up the database
docker exec embedding-app python -m app.main setup

# Reset the database (clear all data)
docker exec embedding-app python -m app.main reset

# Embed documents from a JSON file
docker exec embedding-app python -m app.main embed path/to/your/file.json

# Start the web server (done automatically by Docker)
docker exec embedding-app python -m app.main serve
```

## API Endpoints

The web application provides the following API endpoints:

- `GET /api/documents` - Get all documents
- `GET /api/search?query=your+search+query` - Search for similar documents

## Development

If you want to develop the application locally:

1. Install Poetry:

   ```bash
   pip install poetry
   ```

2. Install dependencies:

   ```bash
   poetry install
   ```

3. Run PostgreSQL with pgvector:

   ```bash
   docker-compose up postgres -d
   ```

4. Set up environment variables:

   ```bash
   export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/embeddings
   export OPENAI_API_KEY=your-api-key-here
   ```

5. Run the application:
   ```bash
   poetry run python -m app.main serve
   ```

## Architecture

- **Docker**: Containerizes the application and PostgreSQL database
- **PostgreSQL + pgvector**: Stores documents and vector embeddings
- **LangChain**: Simplifies interaction with OpenAI embedding model
- **FastAPI**: Provides web interface and API endpoints
- **Poetry**: Manages Python dependencies

## License

[MIT License](LICENSE)
