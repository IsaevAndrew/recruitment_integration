from sqlalchemy import Column, Integer, Text, Boolean, TIMESTAMP, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.database import Base


class AnswerOption(Base):
    __tablename__ = "answer_option"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid()
    )
    question_id = Column(
        UUID(as_uuid=True),
        ForeignKey("question.id", ondelete="CASCADE"),
        nullable=False
    )
    sequence = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False, default=False)

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

    # Обратная связь к Question
    question = relationship("Question", back_populates="answer_options")
