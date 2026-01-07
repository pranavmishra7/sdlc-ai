from app.state.sdlc_state import SDLCState
from app.workflows.nodes.sow import sow_node   # adjust path if needed

state = SDLCState(
    job_id="test-job",
    product_idea="Test product idea",
    scope={"test": "scope"},
    requirements={"test": "requirements"},
    architecture={"test": "architecture"},
    estimation={"test": "estimation"},
    risk={"test": "risk"},
)

print("Before:", state.sow)

state = sow_node(state)

print("After:", state.sow)
print("Type:", type(state.sow))
