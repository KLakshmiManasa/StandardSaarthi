"""
Search History & Saved Project Store for SIH 26108 / Product Engine.
Stores persistent search history and saved procurement analyses in JSON (`data/processed/history.json`).
"""

import os
import json
import time
import uuid
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("HistoryStore")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HISTORY_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'history.json')

class HistoryStore:
    def __init__(self):
        self.history: List[Dict[str, Any]] = []
        self._load()

    def _load(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
                logger.info(f"Loaded {len(self.history)} history records.")
            except Exception as e:
                logger.error(f"Failed to load history.json: {e}")
                self.history = []

    def _save(self):
        try:
            os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save history.json: {e}")

    def add_entry(self, query: str, mode: str, result_summary: Dict[str, Any], language: str = "en") -> Dict[str, Any]:
        """
        Adds a new analysis entry to history.
        """
        entry_id = f"ANALYSIS_{uuid.uuid4().hex[:8].upper()}"
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        entry = {
            "id": entry_id,
            "timestamp": timestamp,
            "query": query,
            "mode": mode,
            "language": language,
            "status": result_summary.get("status", "success"),
            "top_recommendation": result_summary.get("recommendations", [{}])[0].get("is_code") if result_summary.get("recommendations") else "N/A",
            "top_title": result_summary.get("recommendations", [{}])[0].get("title") if result_summary.get("recommendations") else "N/A",
            "is_saved": False,
            "project_name": None,
            "result_summary": result_summary
        }

        # Prepend to history
        self.history.insert(0, entry)
        # Keep last 100 entries
        if len(self.history) > 100:
            self.history = self.history[:100]

        self._save()
        return entry

    def list_history(self, saved_only: bool = False) -> List[Dict[str, Any]]:
        """
        Returns history entries, optionally filtered for saved analyses.
        """
        if saved_only:
            return [e for e in self.history if e.get("is_saved")]
        return self.history

    def get_entry(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """
        Gets a single entry by ID.
        """
        for e in self.history:
            if e.get("id") == entry_id:
                return e
        return None

    def save_project(self, entry_id: str, project_name: str) -> Optional[Dict[str, Any]]:
        """
        Marks an entry as saved with a custom project name.
        """
        for e in self.history:
            if e.get("id") == entry_id:
                e["is_saved"] = True
                e["project_name"] = project_name
                self._save()
                return e
        return None

history_store = HistoryStore()
