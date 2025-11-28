#!/usr/bin/env python3
"""
Test script for Google Drive API connection.

Run this after setting up your service account to verify everything works.

Usage:
    uv run python test_google_drive.py
"""

import json
import os
import sys
from pathlib import Path


def load_env() -> None:
    """Load environment variables from app/.env"""
    env_file = Path("app/.env")
    if not env_file.exists():
        print("❌ Error: app/.env file not found")
        print("   Create app/.env with your Google Drive credentials")
        sys.exit(1)

    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()


def test_drive_connection() -> bool:
    """Test Google Drive API connection."""
    print("🔍 Testing Google Drive API connection...\n")

    try:
        from app.tools.google_drive import (
            get_drive_service,
            list_recent_docs,
            search_google_docs,
        )

        # Test 1: Initialize service
        print("1️⃣  Initializing Google Drive service...")
        service = get_drive_service()
        print("   ✅ Service initialized successfully\n")

        # Test 2: List recent documents
        print("2️⃣  Listing recent documents...")
        result = list_recent_docs()
        result_dict = json.loads(result)

        if result_dict["success"]:
            docs = result_dict["documents"]
            print(f"   ✅ Found {len(docs)} recent document(s)")

            if docs:
                print("\n   📄 Recent documents:")
                for doc in docs[:5]:  # Show first 5
                    print(f"      • {doc['name']}")
                    print(f"        ID: {doc['id']}")
                    print(f"        Modified: {doc['modified_time']}")
                    print()
            else:
                print("\n   ⚠️  No documents found")
                print("      Make sure you've shared documents with the service account:")
                print(
                    f"      {os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY_BASE64', 'service-account-email')}"
                )
                return False
        else:
            print(f"   ❌ Failed to list documents: {result_dict['message']}")
            return False

        # Test 3: Search for documents
        print("\n3️⃣  Testing document search...")
        search_result = search_google_docs("test")
        search_dict = json.loads(search_result)

        if search_dict["success"]:
            print(f"   ✅ Search successful (found {len(search_dict['documents'])} docs)")
        else:
            print(f"   ⚠️  No documents found matching 'test'")
            print("      This is OK if your docs don't contain 'test'")

        print("\n" + "=" * 60)
        print("✅ All tests passed! Google Drive API is working correctly.")
        print("=" * 60)
        print("\nNext steps:")
        print("  1. Start the backend: make dev-backend")
        print("  2. Start the frontend: make dev-frontend")
        print("  3. Open http://localhost:3000")
        print("  4. Ask: 'What documents are available?'")
        print()

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n   Run 'uv sync' to install dependencies")
        return False

    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\n   Check your app/.env file:")
        print("   - GOOGLE_SERVICE_ACCOUNT_KEY_BASE64 must be set")
        print("   - Path must point to valid service account JSON")
        return False

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print(f"\n   Error type: {type(e).__name__}")
        return False


def main() -> None:
    """Main entry point."""
    print("\n" + "=" * 60)
    print("  Google Drive API Connection Test")
    print("=" * 60 + "\n")

    # Load environment
    load_env()

    # Check required env vars
    if not os.getenv("GOOGLE_SERVICE_ACCOUNT_KEY_BASE64"):
        print("❌ Error: GOOGLE_SERVICE_ACCOUNT_KEY_BASE64 not set in app/.env")
        print("\n   Add this line to app/.env:")
        print("   GOOGLE_SERVICE_ACCOUNT_KEY_BASE64=./service-account-key.json")
        sys.exit(1)

    # Run tests
    success = test_drive_connection()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

