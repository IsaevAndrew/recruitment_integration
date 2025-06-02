from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.database import Base


class Question(Base):
    __tablename__ = "question"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid()
    )
    test_id = Column(
        UUID(as_uuid=True),
        ForeignKey("test_template.id", ondelete="CASCADE"),
        nullable=False
    )
    sequence = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    template = relationship("TestTemplate", back_populates="questions")
    answer_options = relationship(
        "AnswerOption",
        back_populates="question",
        cascade="all, delete-orphan"
    )
