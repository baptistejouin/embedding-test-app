"""Main application entry point."""
import os
import sys
import click
from pathlib import Path

from app.embedding import embed_documents_from_file, setup_database, reset_database
from app.web import app
import uvicorn


@click.group()
def cli():
    """Embedding test application CLI."""
    pass


@cli.command("setup")
def setup():
    """Set up the database for the application."""
    setup_database()
    click.echo("Database setup complete.")


@cli.command("reset")
def reset():
    """Reset the database."""
    reset_database()
    click.echo("Database reset complete.")


@cli.command("embed")
@click.argument("file_path", type=click.Path(exists=True))
def embed(file_path):
    """Embed documents from a JSON file."""
    try:
        count = embed_documents_from_file(file_path)
        click.echo(f"Successfully embedded {count} documents from {file_path}")
    except Exception as e:
        click.echo(f"Error embedding documents: {str(e)}", err=True)
        sys.exit(1)


@cli.command("serve")
@click.option("--host", default="0.0.0.0", help="Host to bind the server")
@click.option("--port", default=8080, help="Port to bind the server")
def serve(host, port):
    """Start the web server."""
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    # If no commands are provided, default to starting the web server
    if len(sys.argv) == 1:
        # Create templates directory if it doesn't exist
        if not os.path.exists("app/templates"):
            os.makedirs("app/templates")
            
        # If no command is specified, run the web server
        sys.argv.append("serve")
    
    cli()