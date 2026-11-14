"""One internal marketplace boundary for demo and future live adapters."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any


class MarketplacePort(ABC):
    @abstractmethod
    def search_jobs(self) -> list[dict[str, Any]]: ...

    @abstractmethod
    def get_job(self, job_id: str) -> dict[str, Any]: ...

    @abstractmethod
    def create_proposal_draft(self, payload: dict[str, Any], idempotency_key: str, dry_run: bool = True) -> dict[str, Any]: ...


class DemoMarketplaceAdapter(MarketplacePort):
    def __init__(self, jobs: list[dict[str, Any]]):
        self.jobs = {job["id"]: job for job in jobs}
        self.writes: dict[str, dict[str, Any]] = {}

    def search_jobs(self) -> list[dict[str, Any]]:
        return list(self.jobs.values())

    def get_job(self, job_id: str) -> dict[str, Any]:
        return self.jobs[job_id]

    def create_proposal_draft(self, payload: dict[str, Any], idempotency_key: str, dry_run: bool = True) -> dict[str, Any]:
        if idempotency_key in self.writes:
            return self.writes[idempotency_key]
        result = {"dry_run": dry_run, "would_send": payload, "connects_cost": payload.get("connects_cost", 0)}
        self.writes[idempotency_key] = result
        return result


class UpworkLiveAdapter(MarketplacePort):
    """Deliberately inert until a user configures approved OAuth/MCP access."""
    def _unconfigured(self):
        raise RuntimeError("Live mode is not configured. Connect the official Upwork MCP server with OAuth first.")
    def search_jobs(self): return self._unconfigured()
    def get_job(self, job_id: str): return self._unconfigured()
    def create_proposal_draft(self, payload, idempotency_key, dry_run=True): return self._unconfigured()

