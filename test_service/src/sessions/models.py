from sqlalchemy import Column, Text, TIMESTAMP, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.database import Base


class TestSession(Base):
    __tablename__ = "test_session"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid()
    )
    test_id = Column(
        UUID(as_uuid=True),
        ForeignKey("test_template.id", ondelete="RESTRICT"),
        nullable=False
    )
    external_application_id = Column(UUID(as_uuid=True), nullable=False)
    token = Column(String, nullable=False, unique=True)

    status = Column(String(20), nullable=False, default="pending")
    score = Column(Numeric(5, 2), nullable=True)

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    started_at = Column(TIMESTAMP(timezone=True), nullable=True)
    completed_at = Column(TIMESTAMP(timezone=True), nullable=True)

    test_template = relationship("TestTemplate")
    session_answers = relationship(
        "SessionAnswer",
        back_populates="test_session",
        cascade="all, delete-orphan"
    )


class SessionAnswer(Base):
    __tablename__ = "session_answer"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid()
    )
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("test_session.id", ondelete="CASCADE"),
        nullable=False
    )
    question_id = Column(
        UUID(as_uuid=True),
        ForeignKey("question.id", ondelete="RESTRICT"),
        nullable=False
    )
    answer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("answer_option.id", ondelete="RESTRICT"),
        nullable=False
    )
    answered_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    test_session = relationship("TestSession", back_populates="session_answers")

