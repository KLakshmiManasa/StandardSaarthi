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
AUDIT_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'audit_trail.json')

class HistoryStore:
    def __init__(self):
        self.history: List[Dict[str, Any]] = []
        self.audit_trail: List[Dict[str, Any]] = []
        self._load()
        self._load_audit()

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

    def _load_audit(self):
        if os.path.exists(AUDIT_FILE):
            try:
                with open(AUDIT_FILE, 'r', encoding='utf-8') as f:
                    self.audit_trail = json.load(f)
                logger.info(f"Loaded {len(self.audit_trail)} audit records.")
            except Exception as e:
                logger.error(f"Failed to load audit_trail.json: {e}")
                self.audit_trail = []

    def _save_audit(self):
        try:
            os.makedirs(os.path.dirname(AUDIT_FILE), exist_ok=True)
            with open(AUDIT_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.audit_trail, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save audit_trail.json: {e}")

    def add_entry(self, query: str, mode: str, result_summary: Dict[str, Any], language: str = "en") -> Dict[str, Any]:
        """
        Adds a new analysis entry to history.
        """
        entry_id = f"ANALYSIS_{uuid.uuid4().hex[:8].upper()}"
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        recs = result_summary.get("recommendations", [])
        top_rec_code = recs[0].get("is_code") if recs else "N/A"
        top_rec_title = recs[0].get("title") if recs else "N/A"
        is_gated = result_summary.get("confidence_gated", False)

        entry = {
            "id": entry_id,
            "timestamp": timestamp,
            "query": query,
            "mode": mode,
            "language": language,
            "status": result_summary.get("status", "success"),
            "confidence_gated": is_gated,
            "top_recommendation": f"(Abstained) {top_rec_code}" if is_gated else top_rec_code,
            "top_title": top_rec_title,
            "is_saved": False,
            "project_name": None,
            "officer_review": None,
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

    def add_audit_review(
        self,
        query: str,
        recommended_standard: str,
        decision: str,
        final_standard: str,
        officer_name: str,
        officer_designation: str,
        department: str,
        justification: str,
        analysis_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Logs an official procurement officer review determination into the statutory audit trail.
        Captures ACCEPT or OVERRIDE actions, officer identity, and required audit justifications.
        """
        audit_id = f"AUDIT_{uuid.uuid4().hex[:8].upper()}"
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        record = {
            "audit_id": audit_id,
            "timestamp": timestamp,
            "analysis_id": analysis_id or "ADHOC_ANALYSIS",
            "query": query,
            "recommended_standard": recommended_standard,
            "decision": str(decision or "ACCEPTED").upper(),
            "final_standard": final_standard or recommended_standard,
            "officer_name": officer_name or "Procurement Officer",
            "officer_designation": officer_designation or "Executive Official",
            "department": department or "Government Procurement Division",
            "justification": justification or "Standard verified against statutory technical schedule.",
            "status": "RECORDED"
        }

        # Prepend to audit trail
        self.audit_trail.insert(0, record)
        self._save_audit()

        # If analysis_id provided, link to history entry
        if analysis_id:
            for e in self.history:
                if e.get("id") == analysis_id:
                    e["officer_review"] = record
                    self._save()
                    break

        return record

    def list_audit_trail(self) -> List[Dict[str, Any]]:
        """
        Returns all officer determinations and audit trail logs.
        """
        return self.audit_trail

    def get_audit_by_id(self, audit_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a single audit trail record by its identifier.
        """
        for a in self.audit_trail:
            if a.get("audit_id") == audit_id:
                return a
        return None

history_store = HistoryStore()
