#!/usr/bin/env python3
"""Quick test script for Google Drive connection - lists recent docs."""

from app.tools.google_drive import list_recent_docs

if __name__ == "__main__":
    result = list_recent_docs()
    print(result)

