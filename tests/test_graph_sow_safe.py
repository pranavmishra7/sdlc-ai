from app.workflows.sdlc_graph import build_graph
from app.state.sdlc_state import SDLCState


def test_graph_completes_with_sow_dict_return():
    graph = build_graph()

    state = SDLCState(
        job_id="test-job-1",
        product_idea="Build an AI-powered SDLC assistant"
    )

    final_state = graph.invoke(state)

    # --- ASSERTIONS (critical) ---
    assert isinstance(final_state, SDLCState)

    # sow must exist and be string
    assert final_state.sow is not None
    assert isinstance(final_state.sow, str)

    # other steps must be dicts
    assert isinstance(final_state.scope, dict)
    assert isinstance(final_state.requirements, dict)
    assert isinstance(final_state.estimation, dict)
    assert isinstance(final_state.risk, dict)
