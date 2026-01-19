import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Enum, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.base import Base

class TenantStatus(str, PyEnum):
    CREATED = "CREATED"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    DELETED = "DELETED"


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(String, nullable=False)
    
    status: Mapped[TenantStatus] = mapped_column(
        Enum(TenantStatus, name="tenant_status_enum"),
        nullable=False,
        server_default=TenantStatus.CREATED.value,
    )
    
    plan: Mapped[str] = mapped_column(
        String,
        nullable=False,
        server_default="free",
    )

    max_projects: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="3",
    )

    max_users: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="5",
    )

    llm_monthly_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="100000",
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
