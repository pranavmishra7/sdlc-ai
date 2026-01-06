from langgraph.graph import StateGraph
from app.state.sdlc_state import SDLCState

from app.workflows.nodes.intake import intake_node
from app.workflows.nodes.scope import scope_node
from app.workflows.nodes.requirements import requirements_node
from app.workflows.nodes.architecture import architecture_node
from app.workflows.nodes.estimation import estimation_node
from app.workflows.nodes.risk import risk_node
from app.workflows.nodes.sow import sow_node

def build_graph():
    graph = StateGraph(SDLCState)

    graph.add_node("intake", intake_node)
    graph.add_node("scope", scope_node)
    graph.add_node("requirements", requirements_node)
    graph.add_node("architecture", architecture_node)
    graph.add_node("estimation", estimation_node)
    graph.add_node("risk", risk_node)
    graph.add_node("sow", sow_node)

    graph.set_entry_point("intake")

    graph.add_edge("intake", "scope")
    graph.add_edge("scope", "requirements")
    graph.add_edge("requirements", "architecture")
    graph.add_edge("architecture", "estimation")
    graph.add_edge("estimation", "risk")
    graph.add_edge("risk", "sow")

    return graph.compile()
