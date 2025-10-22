"""
Database models for the voting system
"""
from sqlalchemy import Column, Integer, String, DateTime, LargeBinary, Boolean
from datetime import datetime
from backend.database import Base

class Voter(Base):
    """Model for registered voters"""
    __tablename__ = "voters"
    
    id = Column(Integer, primary_key=True, index=True)
    voter_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    face_data = Column(LargeBinary, nullable=True)  # Store face image data
    has_voted = Column(Boolean, default=False)
    registered_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Voter {self.voter_id}: {self.name}>"


class Candidate(Base):
    """Model for election candidates"""
    __tablename__ = "candidates"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    party = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<Candidate {self.candidate_id}: {self.name}>"
