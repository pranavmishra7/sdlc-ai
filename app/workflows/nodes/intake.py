from app.state.sdlc_state import SDLCState
from app.agents.intake_agent import run_intake


def intake_node(state: SDLCState) -> SDLCState:
    """
    Intake node.
    - Executes intake agent
    - Completes step via SDLCState
    """

    # Run agent (may raise, graph will catch)
    result = run_intake(state.product_idea)

    # Expected result shape:
    # {
    #   "type": "json",
    #   "raw": "<verbatim llm output>",
    #   "parsed": { ... } | None
    # }

    return state.complete_step("intake", result)
