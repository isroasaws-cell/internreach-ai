from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class HRContact(Base):
    __tablename__ = "hr_contacts"
    id       = Column(Integer, primary_key=True)
    hr_name  = Column(String(100))
    hr_email = Column(String(100), unique=True)
    company  = Column(String(100))
    domain   = Column(String(100))
    website  = Column(String(200), nullable=True)
    added_at = Column(DateTime, default=datetime.utcnow)

class EmailCampaign(Base):
    __tablename__ = "email_campaigns"
    id                    = Column(Integer, primary_key=True)
    hr_id                 = Column(Integer, ForeignKey("hr_contacts.id"))
    subject               = Column(String(300))
    body                  = Column(Text)
    rag_context           = Column(Text)
    gmail_msg_id          = Column(String(100))
    thread_id             = Column(String(100))
    status                = Column(String(20), default="sent")
    quality_score         = Column(Float, default=0.0)
    personalization_score = Column(Integer, default=0)
    professionalism_score = Column(Integer, default=0)
    relevance_score       = Column(Integer, default=0)
    attempts              = Column(Integer, default=1)
    sent_at               = Column(DateTime, default=datetime.utcnow)
    replied_at            = Column(DateTime, nullable=True)

class FollowUp(Base):
    __tablename__ = "followups"
    id           = Column(Integer, primary_key=True)
    campaign_id  = Column(Integer, ForeignKey("email_campaigns.id"))
    subject      = Column(String(300))
    body         = Column(Text)
    gmail_msg_id = Column(String(100))
    sent_at      = Column(DateTime, default=datetime.utcnow)

import os
DATABASE_URL = "sqlite:////tmp/outreach.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)
    print("Database initialized")