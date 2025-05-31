from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.orm import relationship
from src.database import Base


class Vacancy(Base):
    __tablename__ = "vacancies"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    applications = relationship(
        "JobApplication",
        back_populates="vacancy",
        cascade="all, delete-orphan"
    )
