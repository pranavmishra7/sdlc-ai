from datetime import datetime
import uuid
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.db.base import Base

class SDLCJob(Base):
    __tablename__ = "sdlc_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )

    status: Mapped[str] = mapped_column(String, nullable=False)

    current_step: Mapped[str | None] = mapped_column(String)

    retry_count: Mapped[int] = mapped_column(default=0)

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
