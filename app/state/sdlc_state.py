from typing import Dict, Any, Optional
from pydantic import BaseModel

from typing import Any
from pydantic import BaseModel

class SDLCState(BaseModel):
    job_id: str
    product_idea: str

    intake: dict | None = None
    scope: dict | None = None
    requirements: dict | None = None
    architecture: dict | None = None
    estimation: dict | None = None
    risk: dict | None = None

    sow: Any | None = None   # ✅ FIX IS HERE

