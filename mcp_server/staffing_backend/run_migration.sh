#!/bin/bash
# Run migration via Supabase CLI or psql

# Method 1: Supabase CLI (if linked to project)
if command -v supabase &> /dev/null; then
    echo "Running migration via Supabase CLI..."
    supabase db push --file migrate_resume_submissions.sql
    exit $?
fi

# Method 2: Direct psql connection
# Replace with your actual connection string from Supabase dashboard
# Settings > Database > Connection string > URI
if [ -z "$SUPABASE_DB_URL" ]; then
    echo "Error: SUPABASE_DB_URL environment variable not set"
    echo ""
    echo "To use psql, set your connection string:"
    echo "  export SUPABASE_DB_URL='postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres'"
    echo ""
    echo "Or run the SQL directly in Supabase SQL Editor (recommended)"
    exit 1
fi

echo "Running migration via psql..."
psql "$SUPABASE_DB_URL" -f migrate_resume_submissions.sql

