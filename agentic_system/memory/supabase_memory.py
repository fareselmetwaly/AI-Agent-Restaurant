import logging
from datetime import datetime, timezone

from agentic_system.integrations.db_config import supabase

logger = logging.getLogger(__name__)

CHAT_MESSAGES_TABLE = "n8n_chat_histories"
CHAT_SESSIONS_TABLE = "restaurant_chat_sessions"
VALID_ROLES = {"user", "assistant"}


def save_message(chat_id: str, role: str, content: str) -> bool:
    if not chat_id or role not in VALID_ROLES or not content:
        return False

    try:
        supabase.table(CHAT_MESSAGES_TABLE).insert(
            {
                "session_id": chat_id,
                "message": {
                    "role": role,
                    "content": str(content),
                },
            }
        ).execute()
        return True
    except Exception:
        logger.exception("Could not save message for chat_id=%s", chat_id)
        return False


def get_recent_history(chat_id: str, limit: int = 10) -> list[dict]:
    try:
        limit = max(1, int(limit))
        response = (
            supabase.table(CHAT_MESSAGES_TABLE)
            .select("id, message")
            .eq("session_id", chat_id)
            .order("id", desc=True)
            .limit(limit)
            .execute()
        )

        rows = list(reversed(response.data or []))
        history = []

        for row in rows:
            message = row.get("message")
            if not isinstance(message, dict):
                continue

            role = message.get("role")
            content = message.get("content")

            if role in VALID_ROLES and content:
                history.append(
                    {
                        "role": role,
                        "content": str(content),
                    }
                )

        return history
    except Exception:
        logger.exception("Could not load history for chat_id=%s", chat_id)
        return []


def get_session(chat_id: str) -> dict:
    default_session = {
        "chat_id": chat_id,
        "human_handoff": False,
        "escalation_reason": None,
        "failed_attempts": 0,
    }

    try:
        response = (
            supabase.table(CHAT_SESSIONS_TABLE)
            .select("chat_id, human_handoff, escalation_reason, failed_attempts")
            .eq("chat_id", chat_id)
            .limit(1)
            .execute()
        )

        rows = response.data or []
        if not rows:
            return default_session

        row = rows[0]
        return {
            "chat_id": chat_id,
            "human_handoff": bool(row.get("human_handoff", False)),
            "escalation_reason": row.get("escalation_reason"),
            "failed_attempts": max(0, int(row.get("failed_attempts", 0) or 0)),
        }
    except Exception:
        logger.exception("Could not load session for chat_id=%s", chat_id)
        return default_session


def save_session(
    chat_id: str,
    human_handoff: bool = False,
    escalation_reason: str | None = None,
    failed_attempts: int = 0,
) -> bool:
    try:
        supabase.table(CHAT_SESSIONS_TABLE).upsert(
            {
                "chat_id": chat_id,
                "human_handoff": bool(human_handoff),
                "escalation_reason": escalation_reason,
                "failed_attempts": max(0, int(failed_attempts)),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            on_conflict="chat_id",
        ).execute()
        return True
    except Exception:
        logger.exception("Could not save session for chat_id=%s", chat_id)
        return False


def set_handoff(chat_id: str, reason: str, failed_attempts: int = 0) -> bool:
    return save_session(
        chat_id=chat_id,
        human_handoff=True,
        escalation_reason=reason,
        failed_attempts=failed_attempts,
    )
