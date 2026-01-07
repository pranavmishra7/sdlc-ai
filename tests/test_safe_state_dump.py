from app.state.sdlc_state import SDLCState
from app.workers.tasks import safe_state_dump


def test_safe_state_dump_handles_dicts_and_strings():
    state = SDLCState(
        job_id="job-123",
        product_idea="Test",
        scope={"a": 1},
        risk={"b": 2},
        sow="FINAL DOCUMENT"
    )

    dumped = safe_state_dump(state)

    assert isinstance(dumped, dict)
    assert dumped["scope"] == {"a": 1}
    assert dumped["risk"] == {"b": 2}
    assert dumped["sow"] == "FINAL DOCUMENT"
