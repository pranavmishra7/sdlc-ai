# app/dto/workflow_dto.py

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID


class StartWorkflowRequestDTO(BaseModel):
    product_idea: Optional[str] = Field(
        None,
        description="Business idea to start a new SDLC workflow"
    )
    job_id: Optional[UUID] = Field(
        None,
        description="Existing job ID to resume workflow"
    )
