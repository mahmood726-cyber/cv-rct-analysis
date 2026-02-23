from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Trial(Base):
    __tablename__ = 'trials'
    
    id = Column(Integer, primary_key=True)
    nct_id = Column(String(20), unique=True, index=True, nullable=False)
    title = Column(Text)
    phase = Column(String(50))
    conditions = Column(Text)
    interventions = Column(Text)
    primary_endpoints = Column(Text)
    completion_date = Column(Date)
    enrollment = Column(Integer)
    status = Column(String(100))
    
    publications = relationship("Publication", back_populates="trial")

class Publication(Base):
    __tablename__ = 'publications'
    
    id = Column(Integer, primary_key=True)
    pmid = Column(String(20), unique=True, index=True)
    openalex_id = Column(String(100), unique=True, index=True)
    title = Column(Text)
    journal = Column(String(255))
    publication_date = Column(Date)
    abstract = Column(Text)
    doi = Column(String(100))
    
    trial_id = Column(Integer, ForeignKey('trials.id'))
    trial = relationship("Trial", back_populates="publications")
