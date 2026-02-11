from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID


class TargetAudienceDTO(BaseModel):
    primary: List[str]
    secondary: List[str]


class StartWorkflowRequestDTO(BaseModel):
    product_idea: Optional[str] = Field(
        None,
        description="Core product idea to initiate workflow"
    )

    domain: Optional[str] = Field(
        None,
        description="Business domain of the product"
    )

    target_audience: Optional[TargetAudienceDTO] = None

    documentation_objective: Optional[str] = None

    regulatory_context: Optional[List[str]] = None

    job_id: Optional[UUID] = Field(
        None,
        description="Existing job ID to resume workflow"
    )
