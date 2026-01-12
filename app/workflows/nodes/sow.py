import json
import re
from typing import Any, Dict

from app.state.sdlc_state import SDLCState
from app.agents.sow_agent import run_sow


def _extract_json_block(text: str) -> Dict[str, Any]:
    """
    Extracts the FIRST valid JSON object from the LLM output.
    Raw text is NEVER modified or trimmed.
    """

    # Prefer fenced ```json blocks
    fence_match = re.search(
        r"```json\s*(\{[\s\S]*?\})\s*```",
        text,
        re.IGNORECASE,
    )
    raw_json = fence_match.group(1) if fence_match else None

    # Fallback: first {...} block
    if raw_json is None:
        brace_match = re.search(r"(\{[\s\S]*\})", text)
        raw_json = brace_match.group(1) if brace_match else None

    if raw_json is None:
        raise ValueError("No JSON object found in SOW output")

    try:
        return json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in SOW output: {exc}") from exc


def sow_node(state: SDLCState) -> SDLCState:
    """
    SOW node.
    Applies schema parsing ONLY here.
    """

    # Full accumulated context (intake → requirements → architecture → etc.)
    context = state.get_context()

    # Run agent (may raise; graph will catch)
    agent_result = run_sow(context)

    # Expected agent_result:
    # {
    #   "raw_output": "<verbatim LLM output>"
    # }

    raw = agent_result["raw_output"]

    parsed = _extract_json_block(raw)

    output = {
        "type": "json",
        "raw": raw,        # 🔒 NEVER altered
        "parsed": parsed,  # ✅ structured + stable
    }

    return state.complete_step("sow", output)
