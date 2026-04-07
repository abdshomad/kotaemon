"""Settings API (Phase 2): read-only flattened settings snapshot."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from theflow.settings import settings as flowsettings
from theflow.utils.modules import import_dotted_string

from ktem.components import reasonings
from ktem.settings import BaseSettingGroup, SettingGroup, SettingReasoningGroup

from app.auth import SESSION_USER_KEY

router = APIRouter(prefix="/api", tags=["settings"])


class SettingsOut(BaseModel):
    settings: dict[str, object]


def _build_default_settings_snapshot() -> dict[str, object]:
    default_settings = SettingGroup(
        application=BaseSettingGroup(settings=flowsettings.SETTINGS_APP),
        reasoning=SettingReasoningGroup(settings=flowsettings.SETTINGS_REASONING),
    )

    for value in getattr(flowsettings, "KH_REASONINGS", []):
        reasoning_cls = import_dotted_string(value, safe=False)
        rid = reasoning_cls.get_info()["id"]
        reasonings[rid] = reasoning_cls
        default_settings.reasoning.options[rid] = BaseSettingGroup(
            settings=reasoning_cls().get_user_settings()
        )

    default_settings.reasoning.finalize()
    default_settings.index.finalize()
    return default_settings.flatten()


@router.get("/settings", response_model=SettingsOut)
def get_settings(request: Request) -> SettingsOut:
    user = request.session.get(SESSION_USER_KEY)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return SettingsOut(settings=_build_default_settings_snapshot())
