from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from firebase_admin import auth as firebase_auth
from firebase_admin import credentials, get_app, initialize_app

from app.core.config import get_settings

settings = get_settings()


def _build_credentials() -> tuple[Any | None, dict[str, Any] | None]:
    if settings.firebase_service_account_json:
        info = json.loads(settings.firebase_service_account_json)
        return credentials.Certificate(info), {
            "projectId": settings.firebase_project_id or info.get("project_id")
        }

    if settings.firebase_service_account_path:
        return credentials.Certificate(settings.firebase_service_account_path), (
            {"projectId": settings.firebase_project_id}
            if settings.firebase_project_id
            else None
        )

    if settings.firebase_project_id:
        return None, {"projectId": settings.firebase_project_id}

    return None, None


@lru_cache
def init_firebase_app() -> None:
    try:
        get_app()
        return
    except ValueError:
        pass

    cred, options = _build_credentials()
    if cred is not None:
        initialize_app(cred, options)
        return

    if options is not None:
        initialize_app(options=options)
        return

    initialize_app()


def verify_firebase_id_token(id_token: str) -> dict[str, Any]:
    init_firebase_app()
    return firebase_auth.verify_id_token(id_token, check_revoked=False)
