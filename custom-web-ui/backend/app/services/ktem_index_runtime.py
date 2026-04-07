"""Headless IndexManager singleton for API routes (no Gradio UI)."""

from __future__ import annotations

from dataclasses import dataclass

from ktem.index import IndexManager
from ktem.index.file.index import FileIndex

_index_manager: IndexManager | None = None


@dataclass
class _StubApp:
    """Minimal app object FileIndex stores; Gradio is not initialized."""

    f_user_management: bool = False


def get_index_manager() -> IndexManager:
    global _index_manager
    if _index_manager is None:
        _index_manager = IndexManager(_StubApp())
        _index_manager.on_application_startup()
    return _index_manager


def get_file_index(index_id: int) -> FileIndex:
    """Return the running file index with this id, or raise KeyError."""
    mgr = get_index_manager()
    for idx in mgr.indices:
        if idx.id == index_id and isinstance(idx, FileIndex):
            return idx
    raise KeyError(f"No file index with id {index_id}")
