from pydantic import BaseModel
from typing import Dict, Optional, Any
from uuid import UUID


class RetryPolicyDTO(BaseModel):
    intake: int
    scope: int
    requirements: int
    architecture: int
    estimation: int
    risk: int
    sow: int


class StepsDTO(BaseModel):
    intake: str
    scope: str
    requirements: str
    architecture: str
    estimation: str
    risk: str
    sow: str


class WorkflowResponseDTO(BaseModel):
    job_id: UUID
    product_idea: str
    job_status: str
    steps: StepsDTO
    current_step: str
    outputs: Dict[str, Any]
    errors: Dict[str, Any]
    retries: Dict[str, int]
    retry_policy: RetryPolicyDTO
    step_started_at: Dict[str, Any]
    step_completed_at: Dict[str, Any]
    step_approvals: Dict[str, Any]
    quality: Dict[str, Any]
    dead_letter: Optional[Any] = None
