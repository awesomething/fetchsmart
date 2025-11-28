"""Question logging for tracking user queries and document usage."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class QuestionLogger:
    """Logger for tracking questions asked and documents accessed."""

    def __init__(self, log_file: str = "logs/questions.jsonl") -> None:
        """
        Initialize the question logger.

        Args:
            log_file: Path to the log file
        """
        self.log_file = Path(log_file)
        self._ensure_log_directory()

    def _ensure_log_directory(self) -> None:
        """Create log directory if it doesn't exist."""
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def log_question(
        self,
        question: str,
        user_id: str,
        session_id: str,
        documents_searched: list[dict[str, Any]] | None = None,
        documents_used: list[dict[str, Any]] | None = None,
        answer_summary: str | None = None,
    ) -> None:
        """
        Log a question and related metadata.

        Args:
            question: The user's question
            user_id: User ID who asked the question
            session_id: Session ID
            documents_searched: List of documents that were searched
            documents_used: List of documents used in the answer
            answer_summary: Brief summary of the answer provided
        """
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "question": question,
            "user_id": user_id,
            "session_id": session_id,
            "documents_searched": documents_searched or [],
            "documents_used": documents_used or [],
            "answer_summary": answer_summary,
        }

        # Append to JSONL file
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

    def get_recent_questions(self, limit: int = 100) -> list[dict[str, Any]]:
        """
        Get recent questions from the log.

        Args:
            limit: Maximum number of questions to return

        Returns:
            List of log entries
        """
        if not self.log_file.exists():
            return []

        questions = []
        with open(self.log_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    questions.append(json.loads(line))

        # Return most recent questions
        return questions[-limit:]

    def get_question_stats(self) -> dict[str, Any]:
        """
        Get statistics about logged questions.

        Returns:
            Dictionary with question statistics
        """
        questions = self.get_recent_questions(limit=1000)

        if not questions:
            return {
                "total_questions": 0,
                "unique_users": 0,
                "documents_accessed": {},
                "recent_questions": [],
            }

        # Count unique users
        unique_users = len(set(q["user_id"] for q in questions))

        # Count document access frequency
        doc_access_counts: dict[str, int] = {}
        for q in questions:
            for doc in q.get("documents_used", []):
                doc_name = doc.get("name", "Unknown")
                doc_access_counts[doc_name] = doc_access_counts.get(doc_name, 0) + 1

        # Sort documents by access count
        sorted_docs = sorted(
            doc_access_counts.items(), key=lambda x: x[1], reverse=True
        )

        return {
            "total_questions": len(questions),
            "unique_users": unique_users,
            "most_accessed_documents": sorted_docs[:10],
            "recent_questions": [
                {
                    "question": q["question"],
                    "timestamp": q["timestamp"],
                    "user_id": q["user_id"],
                }
                for q in questions[-10:]
            ],
        }


# Global logger instance
_question_logger: QuestionLogger | None = None


def get_question_logger() -> QuestionLogger:
    """Get or create the global question logger instance."""
    global _question_logger
    if _question_logger is None:
        _question_logger = QuestionLogger()
    return _question_logger

