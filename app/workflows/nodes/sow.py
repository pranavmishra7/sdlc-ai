import json
import re
from typing import Dict, Any

from app.state.sdlc_state import SDLCState
from app.agents.sow_agent import run_sow


def _extract_json_block(text: str) -> Dict[str, Any]:
    fence = re.search(r"```json\s*(\{[\s\S]*?\})\s*```", text, re.I)
    raw_json = fence.group(1) if fence else None

    if raw_json is None:
        brace = re.search(r"(\{[\s\S]*\})", text)
        raw_json = brace.group(1) if brace else None

    if raw_json is None:
        raise ValueError("No JSON object found in SOW output")

    return json.loads(raw_json)


def sow_node(state: SDLCState) -> SDLCState:
    context = state.get_context()
    agent_result = run_sow(context)

    raw = agent_result["raw_output"]
    parsed = _extract_json_block(raw)

    output = {
        "type": "json",
        "raw": raw,      # 🔒 preserved
        "parsed": parsed,
    }

    return state.complete_step("sow", output)
