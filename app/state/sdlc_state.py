from typing import Dict, Any, Optional
from pydantic import BaseModel

class SDLCState(BaseModel):
    job_id: str

    # user input
    product_idea: Optional[str] = None

    # outputs of agents
    intake: Optional[Dict[str, Any]] = None
    scope: Optional[Dict[str, Any]] = None
    requirements: Optional[Dict[str, Any]] = None
    architecture: Optional[Dict[str, Any]] = None
    estimation: Optional[Dict[str, Any]] = None
    risk: Optional[Dict[str, Any]] = None
    sow: Optional[str] = None
