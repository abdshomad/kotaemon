"""File index list/upload/delete using ktem pipelines (Phase 5)."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from sqlmodel import Session, select
from theflow.settings import settings as flowsettings

from ktem.db.models import engine
from ktem.index.file.index import FileIndex

from app.services.ktem_index_runtime import get_file_index


def _format_size_human_readable(num: float | int) -> str:
    n = float(num)
    for unit in ("", "K", "M", "G", "T", "P", "E", "Z"):
        if abs(n) < 1024.0:
            return f"{n:3.0f}{unit}B"
        n /= 1024.0
    return f"{n:.0f}YiB"


def list_index_files(
    index_id: int,
    user_id: str,
    *,
    q: str = "",
) -> list[dict[str, Any]]:
    fi = get_file_index(index_id)
    Source = fi._resources["Source"]
    KH_DEMO_MODE = getattr(flowsettings, "KH_DEMO_MODE", False)
    MAX_FILE_COUNT = 200

    with Session(engine) as session:
        statement = select(Source)
        if fi.config.get("private", False):
            statement = statement.where(Source.user == user_id)
        if q:
            statement = statement.where(Source.name.ilike(f"%{q}%"))
        if KH_DEMO_MODE:
            statement = statement.limit(MAX_FILE_COUNT)
        rows = session.exec(statement).all()

    out: list[dict[str, Any]] = []
    for row in rows:
        src = row[0] if isinstance(row, tuple) else row
        size = getattr(src, "size", 0) or 0
        dc = getattr(src, "date_created", None)
        out.append(
            {
                "id": src.id,
                "name": src.name,
                "size_bytes": int(size),
                "size": _format_size_human_readable(size),
                "date_created": dc.isoformat() if isinstance(dc, datetime) else "",
            }
        )
    return out


def _validate_extension(fi: FileIndex, filename: str) -> str | None:
    ext = Path(filename).suffix.lower()
    raw = fi.config.get("supported_file_types", "") or ""
    types = [x.strip().lower() for x in str(raw).split(",") if x.strip()]
    if not types:
        return None
    if ext not in types:
        return f"Unsupported file type {ext}. Allowed: {raw}"
    return None


def _validate_before_upload(fi: FileIndex, path: Path) -> str | None:
    err = _validate_extension(fi, path.name)
    if err:
        return err
    max_mb = fi.config.get("max_file_size", 0) or 0
    if max_mb and path.stat().st_size > float(max_mb) * 1e6:
        return f"Maximum file size ({max_mb} MB) exceeded for {path.name}"
    max_n = fi.config.get("max_number_of_files", 0) or 0
    if max_n:
        Source = fi._resources["Source"]
        with Session(engine) as session:
            count = len(session.exec(select(Source)).all())
        if count + 1 > max_n:
            return f"Maximum number of files ({max_n}) would be exceeded"
    return None


def index_uploaded_file(
    index_id: int,
    user_id: str,
    *,
    local_path: Path,
    original_filename: str,
    settings_flat: dict[str, object],
    reindex: bool = False,
) -> dict[str, Any]:
    """Run indexing pipeline for one file on disk. Caller removes local_path when done."""
    fi = get_file_index(index_id)
    err = _validate_before_upload(fi, local_path)
    if err:
        return {"ok": False, "error": err}

    indexing_pipeline = fi.get_indexing_pipeline(settings_flat, user_id)
    outputs: list[str] = []
    debugs: list[str] = []
    output_stream = indexing_pipeline.stream([str(local_path)], reindex=reindex)
    file_ids: list[str | None] = []
    index_errors: list[str | None] = []
    try:
        while True:
            response = next(output_stream)
            if response is None:
                continue
            if response.channel == "index" and response.content:
                c = response.content
                if isinstance(c, dict):
                    if c.get("status") == "success":
                        outputs.append(f"✅ | {c.get('file_name', '')}")
                    elif c.get("status") == "failed":
                        outputs.append(
                            f"❌ | {c.get('file_name', '')}: {c.get('message', '')}"
                        )
            elif response.channel == "debug":
                debugs.append(response.text)
    except StopIteration as e:
        file_ids, index_errors, _docs = e.value
    except Exception as exc:
        return {"ok": False, "error": str(exc)}

    fid = file_ids[0] if file_ids else None
    ierr = index_errors[0] if index_errors else None
    if ierr:
        return {"ok": False, "error": ierr, "log": "\n".join(outputs + debugs)}
    if not fid:
        return {"ok": False, "error": "Indexing produced no file id", "log": "\n".join(debugs)}

    return {
        "ok": True,
        "file_id": fid,
        "name": original_filename,
        "log": "\n".join(outputs + debugs),
    }


def delete_index_file(index_id: int, user_id: str, file_id: str) -> bool:
    """Remove a file from the index (DB + vector + docstore). Returns False if missing."""
    fi = get_file_index(index_id)
    Source = fi._resources["Source"]
    Index = fi._resources["Index"]

    with Session(engine) as session:
        statement = select(Source).where(Source.id == file_id)
        if fi.config.get("private", False):
            statement = statement.where(Source.user == user_id)
        source = session.exec(statement).one_or_none()
        if source is None:
            return False
        session.delete(source)

        vs_ids: list[str] = []
        ds_ids: list[str] = []
        for item in session.exec(
            select(Index).where(Index.source_id == file_id)
        ).all():
            if item.relation_type == "vector":
                vs_ids.append(item.target_id)
            elif item.relation_type == "document":
                ds_ids.append(item.target_id)
            session.delete(item)
        session.commit()

    if vs_ids:
        fi._vs.delete(vs_ids)
    fi._docstore.delete(ds_ids)
    return True


def validate_file_ids_for_turn(
    index_id: int,
    user_id: str,
    file_ids: list[str],
) -> None:
    """Ensure each id exists and is visible to this user for a private index."""
    if not file_ids:
        return
    fi = get_file_index(index_id)
    Source = fi._resources["Source"]
    with Session(engine) as session:
        for fid in file_ids:
            statement = select(Source).where(Source.id == fid)
            if fi.config.get("private", False):
                statement = statement.where(Source.user == user_id)
            row = session.exec(statement).one_or_none()
            if not row:
                raise ValueError(f"Invalid or inaccessible file id: {fid}")
