from pydantic import BaseModel
from typing import Dict, Optional
from uuid import UUID
from datetime import datetime


class StepStatusDTO(BaseModel):
    intake: str
    scope: str
    requirements: str
    architecture: str
    estimation: str
    risk: str
    sow: str


class RetryPolicyDTO(BaseModel):
    intake: int
    scope: int
    requirements: int
    architecture: int
    estimation: int
    risk: int
    sow: int


class ErrorDetailDTO(BaseModel):
    message: str
    type: str


class DeadLetterDTO(BaseModel):
    step: str
    error: ErrorDetailDTO
    failed_at: datetime


class WorkflowStatusResponseDTO(BaseModel):
    job_id: UUID
    product_idea: str
    job_status: str
    steps: StepStatusDTO
    current_step: str

    outputs: Dict[str, dict]
    errors: Dict[str, ErrorDetailDTO]
    retries: Dict[str, int]

    retry_policy: RetryPolicyDTO

    step_started_at: Dict[str, datetime]
    step_completed_at: Dict[str, datetime]

    step_approvals: Dict[str, dict]
    quality: Dict[str, dict]

    dead_letter: Optional[DeadLetterDTO] = None
