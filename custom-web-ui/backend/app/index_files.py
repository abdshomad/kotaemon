"""File index REST API (Phase 5): list, upload, delete."""

from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, Query, Request, UploadFile, status
from pydantic import BaseModel
from theflow.settings import settings as flowsettings

from app.auth import SESSION_USER_KEY
from app.services.file_index_ops import (
    delete_index_file,
    index_uploaded_file,
    list_index_files,
)
from app.services.ktem_index_runtime import get_file_index, get_index_manager
from app.settings import get_flat_settings_snapshot
from ktem.index.file.index import FileIndex

router = APIRouter(prefix="/api/index", tags=["index"])


class IndexSummaryOut(BaseModel):
    id: int
    name: str


class FileEntryOut(BaseModel):
    id: str
    name: str
    size_bytes: int
    size: str
    date_created: str


class UploadResultOut(BaseModel):
    ok: bool
    file_id: str | None = None
    name: str | None = None
    log: str | None = None
    error: str | None = None


def _require_user_id(request: Request) -> str:
    user = request.session.get(SESSION_USER_KEY)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = user.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return str(user_id)


@router.get("", response_model=list[IndexSummaryOut])
def api_list_indices(request: Request) -> list[IndexSummaryOut]:
    _require_user_id(request)
    mgr = get_index_manager()

    return [
        IndexSummaryOut(id=idx.id, name=idx.name)
        for idx in mgr.indices
        if isinstance(idx, FileIndex)
    ]


@router.get("/{index_id}/files", response_model=list[FileEntryOut])
def api_list_files(
    index_id: int,
    request: Request,
    q: str = Query("", description="Filter by file name (substring)"),
) -> list[FileEntryOut]:
    user_id = _require_user_id(request)
    try:
        get_file_index(index_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    try:
        rows = list_index_files(index_id, user_id, q=q)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return [FileEntryOut(**row) for row in rows]


@router.post("/{index_id}/upload", response_model=UploadResultOut)
async def api_upload_file(
    index_id: int,
    request: Request,
    file: UploadFile = File(...),
) -> UploadResultOut:
    user_id = _require_user_id(request)
    try:
        get_file_index(index_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    raw_name = file.filename or "upload"
    safe_name = Path(raw_name).name
    if not safe_name or safe_name in (".", ".."):
        raise HTTPException(status_code=400, detail="Invalid filename")

    zip_dir = Path(flowsettings.KH_ZIP_INPUT_DIR)
    zip_dir.mkdir(parents=True, exist_ok=True)
    sub = zip_dir / uuid.uuid4().hex
    sub.mkdir(parents=True, exist_ok=True)
    dest = sub / safe_name

    try:
        with dest.open("wb") as out:
            shutil.copyfileobj(file.file, out)
        settings_flat = get_flat_settings_snapshot()
        result = index_uploaded_file(
            index_id,
            user_id,
            local_path=dest,
            original_filename=safe_name,
            settings_flat=settings_flat,
            reindex=False,
        )
    finally:
        shutil.rmtree(sub, ignore_errors=True)

    if not result.get("ok"):
        return UploadResultOut(
            ok=False,
            error=str(result.get("error", "Upload failed")),
            log=result.get("log"),
        )
    return UploadResultOut(
        ok=True,
        file_id=str(result.get("file_id")),
        name=result.get("name"),
        log=result.get("log"),
    )


@router.delete("/{index_id}/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def api_delete_file(index_id: int, file_id: str, request: Request) -> None:
    user_id = _require_user_id(request)
    try:
        get_file_index(index_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    removed = delete_index_file(index_id, user_id, file_id)
    if not removed:
        raise HTTPException(status_code=404, detail="File not found")
