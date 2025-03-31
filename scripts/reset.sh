#!/bin/bash
set -e

echo "Resetting embedding application database..."

# Reset the database
python -m app.main reset

echo "Database reset complete!"