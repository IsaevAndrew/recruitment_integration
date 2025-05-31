from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from src.database import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)

    last_name = Column(String(100), nullable=False)
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)

    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)

    status = Column(String(50), nullable=False, default="new")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    applications = relationship(
        "JobApplication",
        back_populates="candidate",
        cascade="all, delete-orphan"
    )
