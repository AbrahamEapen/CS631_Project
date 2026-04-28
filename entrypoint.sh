#!/bin/bash
set -e

echo "⏳  Waiting for Postgres to be ready..."
until python3 -c "
import psycopg2, os, sys
try:
    psycopg2.connect(os.environ['DATABASE_URL'])
except:
    sys.exit(1)
" 2>/dev/null; do
  sleep 1
done
echo "Postgres is up"

echo "🌱  Seeding database..."
python3 seed.py

echo "🚀  Starting gunicorn..."
exec gunicorn --bind 0.0.0.0:5000 --workers 2 wsgi:application