"""
Database models for the voting system
"""
from sqlalchemy import Column, Integer, String, DateTime, LargeBinary, Boolean, Text, ForeignKey
from datetime import datetime
from backend.database import Base

class Election(Base):
    """Model for elections"""
    __tablename__ = "elections"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Election {self.title}>"


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
    election_id = Column(Integer, ForeignKey('elections.id'), nullable=True)
    image_url = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<Candidate {self.candidate_id}: {self.name}>"
