"""Google Drive API integration for document search and retrieval."""

import json
import os
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleDriveService:
    """Service for interacting with Google Drive API."""

    SCOPES = [
        "https://www.googleapis.com/auth/drive.readonly",
        "https://www.googleapis.com/auth/documents.readonly",
    ]

    def __init__(self) -> None:
        """Initialize Google Drive service with authentication."""
        self.creds = self._get_credentials()
        self.drive_service = build("drive", "v3", credentials=self.creds)
        self.docs_service = build("docs", "v1", credentials=self.creds)
        self.folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")

    def _get_credentials(self) -> service_account.Credentials:
        """Get service account credentials from environment."""
        service_account_key = os.getenv("GOOGLE_SERVICE_ACCOUNT_KEY_BASE64")

        if not service_account_key:
            raise ValueError(
                "GOOGLE_SERVICE_ACCOUNT_KEY_BASE64 environment variable not set. "
                "Set it to the path of your service account JSON file."
            )

        # Check if it's a file path or JSON string
        if os.path.isfile(service_account_key):
            creds = service_account.Credentials.from_service_account_file(
                service_account_key, scopes=self.SCOPES
            )
        else:
            # Try parsing as JSON string
            try:
                service_account_info = json.loads(service_account_key)
                creds = service_account.Credentials.from_service_account_info(
                    service_account_info, scopes=self.SCOPES
                )
            except json.JSONDecodeError:
                raise ValueError(
                    "GOOGLE_SERVICE_ACCOUNT_KEY_BASE64 must be either a file path "
                    "or a valid JSON string containing service account credentials."
                )

        return creds

    def search_documents(self, query: str, max_results: int = 5) -> list[dict[str, Any]]:
        """
        Search for Google Docs matching the query.

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List of document metadata dictionaries
        """
        try:
            # Build search query
            search_query = f"mimeType='application/vnd.google-apps.document' and fullText contains '{query}'"

            # Add folder restriction if specified
            if self.folder_id:
                search_query += f" and '{self.folder_id}' in parents"

            # Execute search
            results = (
                self.drive_service.files()
                .list(
                    q=search_query,
                    spaces="drive",
                    fields="files(id, name, modifiedTime, webViewLink, owners)",
                    pageSize=max_results,
                    orderBy="modifiedTime desc",
                )
                .execute()
            )

            files = results.get("files", [])

            # Format results
            documents = []
            for file in files:
                documents.append(
                    {
                        "id": file["id"],
                        "name": file["name"],
                        "modified_time": file.get("modifiedTime", "Unknown"),
                        "url": file.get("webViewLink", ""),
                        "owners": [
                            owner.get("displayName", "Unknown")
                            for owner in file.get("owners", [])
                        ],
                    }
                )

            return documents

        except HttpError as error:
            print(f"An error occurred searching documents: {error}")
            return []

    def read_document(self, doc_id: str) -> dict[str, Any]:
        """
        Read the full content of a Google Doc.

        Args:
            doc_id: Google Doc ID

        Returns:
            Dictionary with document content and metadata
        """
        try:
            # Get document content
            doc = self.docs_service.documents().get(documentId=doc_id).execute()

            # Extract text content
            content = self._extract_text_from_doc(doc)

            # Get metadata from Drive
            metadata = (
                self.drive_service.files()
                .get(fileId=doc_id, fields="id, name, modifiedTime, webViewLink")
                .execute()
            )

            return {
                "id": doc_id,
                "name": metadata.get("name", "Unknown"),
                "content": content,
                "modified_time": metadata.get("modifiedTime", "Unknown"),
                "url": metadata.get("webViewLink", ""),
            }

        except HttpError as error:
            print(f"An error occurred reading document {doc_id}: {error}")
            return {
                "id": doc_id,
                "name": "Error",
                "content": f"Failed to read document: {str(error)}",
                "modified_time": "",
                "url": "",
            }

    def list_recent_documents(self, max_results: int = 10) -> list[dict[str, Any]]:
        """
        List recently modified Google Docs.

        Args:
            max_results: Maximum number of documents to return

        Returns:
            List of document metadata dictionaries
        """
        try:
            # Build query for Google Docs
            query = "mimeType='application/vnd.google-apps.document'"

            # Add folder restriction if specified
            if self.folder_id:
                query += f" and '{self.folder_id}' in parents"

            # Execute query
            results = (
                self.drive_service.files()
                .list(
                    q=query,
                    spaces="drive",
                    fields="files(id, name, modifiedTime, webViewLink)",
                    pageSize=max_results,
                    orderBy="modifiedTime desc",
                )
                .execute()
            )

            files = results.get("files", [])

            # Format results
            documents = []
            for file in files:
                documents.append(
                    {
                        "id": file["id"],
                        "name": file["name"],
                        "modified_time": file.get("modifiedTime", "Unknown"),
                        "url": file.get("webViewLink", ""),
                    }
                )

            return documents

        except HttpError as error:
            print(f"An error occurred listing recent documents: {error}")
            return []

    def _extract_text_from_doc(self, doc: dict[str, Any]) -> str:
        """
        Extract plain text from Google Docs API response.

        Args:
            doc: Document object from Google Docs API

        Returns:
            Plain text content
        """
        content = doc.get("body", {}).get("content", [])
        text_parts = []

        for element in content:
            if "paragraph" in element:
                paragraph = element["paragraph"]
                for text_run in paragraph.get("elements", []):
                    if "textRun" in text_run:
                        text_content = text_run["textRun"].get("content", "")
                        text_parts.append(text_content)

        return "".join(text_parts)


# Initialize global service instance
_drive_service: GoogleDriveService | None = None


def get_drive_service() -> GoogleDriveService:
    """Get or create the global Google Drive service instance."""
    global _drive_service
    if _drive_service is None:
        _drive_service = GoogleDriveService()
    return _drive_service


# ADK Tool functions
def search_google_docs(query: str) -> str:
    """
    Search for Google Docs matching the query.

    Args:
        query: Search query string

    Returns:
        JSON string with search results
    """
    service = get_drive_service()
    results = service.search_documents(query, max_results=5)

    if not results:
        return json.dumps(
            {
                "success": False,
                "message": f"No documents found matching query: '{query}'",
                "documents": [],
            }
        )

    return json.dumps(
        {
            "success": True,
            "message": f"Found {len(results)} document(s) matching query: '{query}'",
            "documents": results,
        },
        indent=2,
    )


def read_google_doc(doc_id: str) -> str:
    """
    Read the full content of a Google Doc.

    Args:
        doc_id: Google Doc ID

    Returns:
        JSON string with document content
    """
    service = get_drive_service()
    doc = service.read_document(doc_id)

    if "Error" in doc.get("name", ""):
        return json.dumps(
            {"success": False, "message": doc["content"], "document": None}
        )

    return json.dumps(
        {
            "success": True,
            "message": f"Successfully read document: {doc['name']}",
            "document": doc,
        },
        indent=2,
    )


def list_recent_docs() -> str:
    """
    List recently modified Google Docs.

    Returns:
        JSON string with list of recent documents
    """
    service = get_drive_service()
    results = service.list_recent_documents(max_results=10)

    if not results:
        return json.dumps(
            {
                "success": False,
                "message": "No recent documents found",
                "documents": [],
            }
        )

    return json.dumps(
        {
            "success": True,
            "message": f"Found {len(results)} recent document(s)",
            "documents": results,
        },
        indent=2,
    )

