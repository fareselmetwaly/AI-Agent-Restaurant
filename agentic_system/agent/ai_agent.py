import json
import logging
import os
from typing import Any

from agentic_system.memory import supabase_memory
from agentic_system.tools.tool_registry import (get_tool_function,get_tool_schemas)
from agentic_system.agent.prompts import SYSTEM_PROMPT
from agentic_system.agent.handoff import (HANDOFF_MESSAGE,classify_turn)
from agentic_system.integrations.llm_client import (HANDOFF_MODEL,MODEL_NAME,client)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


TOOLS = get_tool_schemas()
HISTORY_LIMIT = 10
MAX_TOOL_ROUNDS = 4
MAX_FAILED_ATTEMPTS = 3



def normalize_text(content: Any) -> str:
    """Convert a string or content-block response to plain Markdown text."""
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


def to_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, default=str)


def parse_classifier_json(text: str) -> dict[str, Any] | None:
    """Parse classifier JSON, including JSON wrapped in a Markdown code fence."""
    text = text.strip()

    if text.startswith("```"):
        lines = [line for line in text.splitlines() if not line.strip().startswith("```")]
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


def run_agent_loop(messages: list[dict[str, Any]]) -> str:
    """Call the main model and execute tools until a final answer is returned."""
    working_messages = list(messages)

    for _ in range(MAX_TOOL_ROUNDS):
        request: dict[str, Any] = {
            "model": MODEL_NAME,
            "messages": working_messages,
            "temperature": 0.2,
        }

        if TOOLS:
            request["tools"] = TOOLS
            request["tool_choice"] = "auto"

        response = client.chat.completions.create(**request)
        assistant_message = response.choices[0].message
        tool_calls = assistant_message.tool_calls or []

        if not tool_calls:
            answer = normalize_text(assistant_message.content)
            if not answer:
                raise RuntimeError("The model returned an empty response")
            return answer

        working_messages.append(
            {
                "role": "assistant",
                "content": normalize_text(assistant_message.content),
                "tool_calls": [
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {
                            "name": call.function.name,
                            "arguments": call.function.arguments,
                        },
                    }
                    for call in tool_calls
                ],
            }
        )

        for call in tool_calls:
            tool_name = call.function.name

            try:
                tool_args = json.loads(call.function.arguments or "{}")
                tool_function = get_tool_function(tool_name)

                if tool_function is None:
                    tool_result = {
                        "success": False,
                        "error": f"Unknown function: {tool_name}",
                    }
                else:
                    tool_result = tool_function(**tool_args)

            except json.JSONDecodeError:
                tool_result = {
                    "success": False,
                    "error": "Invalid function arguments.",
                }
            except Exception:
                logger.exception("Tool failed: %s", tool_name)
                tool_result = {
                    "success": False,
                    "error": "The requested function failed.",
                }

            working_messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "name": tool_name,
                    "content": to_json(tool_result),
                }
            )

    raise RuntimeError("Maximum tool rounds reached without a final answer")



def handle_customer_message(chat_id: str, user_message: str) -> str:
    """Process one turn through memory, the main agent, and handoff rules."""
    session = supabase_memory.get_session(chat_id)

    if session["human_handoff"]:
        supabase_memory.save_message(chat_id, "user", user_message)
        supabase_memory.save_message(chat_id, "assistant", HANDOFF_MESSAGE)
        return HANDOFF_MESSAGE

    history = supabase_memory.get_recent_history(chat_id, HISTORY_LIMIT)
    messages = [
        *history,
        {"role": "user", "content": user_message},
    ]

    try:
        agent_response = run_agent_loop(
            [
                {"role": "system", "content": SYSTEM_PROMPT},
                *messages,
            ]
        )
    except Exception:
        logger.exception("Main agent failed for chat_id=%s", chat_id)
        failed_attempts = session["failed_attempts"] + 1

        if failed_attempts >= MAX_FAILED_ATTEMPTS:
            final_response = HANDOFF_MESSAGE
            supabase_memory.set_handoff(
                chat_id,
                reason="The main agent failed three consecutive times.",
                failed_attempts=failed_attempts,
            )
        else:
            final_response = (
                "معلش يا فندم، حصلت مشكلة مؤقتة وأنا بجهز الرد. "
                "ممكن تجرب تبعتلي تاني؟"
            )
            supabase_memory.save_session(
                chat_id,
                human_handoff=False,
                failed_attempts=failed_attempts,
            )

        supabase_memory.save_message(chat_id, "user", user_message)
        supabase_memory.save_message(chat_id, "assistant", final_response)
        return final_response

    classification = classify_turn(
        client,
        HANDOFF_MODEL,
        user_message,
        agent_response,
    )
    failed_attempts = session["failed_attempts"]

    if classification is None:
        # Classifier failure is not treated as a bad agent response.
        final_response = agent_response
        supabase_memory.save_session(
            chat_id,
            human_handoff=False,
            failed_attempts=failed_attempts,
        )

    elif (
        classification["user_is_angry"]
        or classification["strong_complaint"]
        or classification["requests_human"]
    ):
        final_response = HANDOFF_MESSAGE
        supabase_memory.set_handoff(
            chat_id,
            reason=classification["reason"] or "The customer needs human assistance.",
            failed_attempts=failed_attempts,
        )

    elif classification["response_is_bad"]:
        failed_attempts += 1

        if failed_attempts >= MAX_FAILED_ATTEMPTS:
            final_response = HANDOFF_MESSAGE
            supabase_memory.set_handoff(
                chat_id,
                reason=classification["reason"] or "Three consecutive poor responses.",
                failed_attempts=failed_attempts,
            )
        else:
            final_response = agent_response
            supabase_memory.save_session(
                chat_id,
                human_handoff=False,
                failed_attempts=failed_attempts,
            )

    else:
        # A good response resets the consecutive-failure counter.
        final_response = agent_response
        supabase_memory.save_session(
            chat_id,
            human_handoff=False,
            failed_attempts=0,
        )

    supabase_memory.save_message(chat_id, "user", user_message)
    supabase_memory.save_message(chat_id, "assistant", final_response)
    return final_response


