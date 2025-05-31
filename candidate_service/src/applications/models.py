from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from src.database import Base


class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, index=True)

    candidate_id = Column(
        Integer,
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False
    )
    vacancy_id = Column(
        Integer,
        ForeignKey("vacancies.id", ondelete="CASCADE"),
        nullable=False
    )

    status = Column(String(50), nullable=False, default="new")
    # Будем хранить UUID сессии теста из test_service как строку
    test_session_id = Column(String, nullable=True)
    test_score = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Обратные связи
    candidate = relationship("Candidate", back_populates="applications")
    vacancy = relationship("Vacancy", back_populates="applications")
