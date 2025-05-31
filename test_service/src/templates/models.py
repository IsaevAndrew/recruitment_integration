from sqlalchemy import Column, Text, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.database import Base


class TestTemplate(Base):
    __tablename__ = "test_template"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid()
    )
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Один шаблон может иметь несколько вопросов
    questions = relationship(
        "Question",
        back_populates="test_template",
        cascade="all, delete-orphan"
    )
