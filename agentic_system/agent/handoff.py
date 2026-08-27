import json
import logging
from typing import Any

from openai import OpenAI

from agentic_system.agent.prompts import HANDOFF_CLASSIFIER_PROMPT

logger = logging.getLogger(__name__)

HANDOFF_MESSAGE = (
    "تمام يا فندم، هوقف المساعد الآلي هنا، وموظف من فريقنا هيتابع مع حضرتك في أقرب وقت."
)


def _normalize_text(content: Any) -> str:
    """Convert a model string or content-block list into plain text."""
    if content is None:
        return ""

    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, dict):
                parts.append(str(part.get("text", "")))
            elif hasattr(part, "text"):
                parts.append(str(part.text or ""))
            else:
                parts.append(str(part))
        return "".join(parts).strip()

    return str(content).strip()


def _to_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, default=str)


def _parse_classifier_json(text: str) -> dict[str, Any] | None:
    """Parse JSON even when the model wraps it in a Markdown code fence."""
    text = text.strip()

    if text.startswith("```"):
        lines = [
            line for line in text.splitlines()
            if not line.strip().startswith("```")
        ]
        if lines and lines[0].strip().lower() == "json":
            lines = lines[1:]
        text = "\n".join(lines).strip()

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end <= start:
        return None

    try:
        result = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None

    return result if isinstance(result, dict) else None


def classify_turn(
    client: OpenAI,
    handoff_model: str,
    user_message: str,
    agent_response: str,
) -> dict[str, Any] | None:
    """Classify the current turn for human handoff."""
    try:
        response = client.chat.completions.create(
            model=handoff_model,
            messages=[
                {"role": "system", "content": HANDOFF_CLASSIFIER_PROMPT},
                {
                    "role": "user",
                    "content": _to_json(
                        {
                            "user_message": user_message,
                            "agent_response": agent_response,
                        }
                    ),
                },
            ],
            temperature=0,
        )

        result = _parse_classifier_json(
            _normalize_text(response.choices[0].message.content)
        )
        if result is None:
            return None

        return {
            "response_is_bad": bool(result.get("response_is_bad", False)),
            "user_is_angry": bool(result.get("user_is_angry", False)),
            "strong_complaint": bool(result.get("strong_complaint", False)),
            "requests_human": bool(result.get("requests_human", False)),
            "reason": str(result.get("reason", ""))[:500],
        }

    except Exception:
        logger.exception("Handoff classifier failed")
        return None


__all__ = ["HANDOFF_MESSAGE", "classify_turn"]
