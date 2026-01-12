import json
import re
from typing import Any, Dict

from app.state.sdlc_state import SDLCState
from app.agents.requirements_agent import run_requirements


def _extract_json_block(text: str) -> Dict[str, Any]:
    """
    Extracts the FIRST JSON object found in the text.
    Raises ValueError if extraction or parsing fails.
    """

    # Match ```json ... ``` OR first {...}
    fence_match = re.search(r"```json\s*(\{[\s\S]*?\})\s*```", text, re.IGNORECASE)
    raw_json = fence_match.group(1) if fence_match else None

    if raw_json is None:
        brace_match = re.search(r"(\{[\s\S]*\})", text)
        raw_json = brace_match.group(1) if brace_match else None

    if raw_json is None:
        raise ValueError("No JSON object found in requirements output")

    try:
        return json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in requirements output: {exc}") from exc


def requirements_node(state: SDLCState) -> SDLCState:
    """
    Requirements node.
    Applies runtime schema parsing ONLY here.
    """

    # Provide full accumulated context
    context = state.get_context()

    # Run agent (may raise)
    agent_result = run_requirements(context)

    # agent_result is expected to be:
    # {
    #   "raw_output": "<verbatim llm output>"
    # }

    raw = agent_result["raw_output"]

    # Parse JSON deterministically (raw preserved regardless)
    parsed = _extract_json_block(raw)

    output = {
        "type": "json",
        "raw": raw,        # 🔒 NEVER modified
        "parsed": parsed,  # ✅ structured, safe
    }

    return state.complete_step("requirements", output)
