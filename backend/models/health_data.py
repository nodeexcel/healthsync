from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    health_metrics = relationship("HealthData", back_populates="user")

class HealthData(Base):
    __tablename__ = 'health_data'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    weight = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    blood_pressure = Column(String, nullable=True)
    heart_rate = Column(Integer, nullable=True)
    cholesterol = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="health_metrics")

def create_health_data(db_session, user_id, weight, height, blood_pressure=None, heart_rate=None, cholesterol=None):
    try:
        health_data = HealthData(
            user_id=user_id,
            weight=weight,
            height=height,
            blood_pressure=blood_pressure,
            heart_rate=heart_rate,
            cholesterol=cholesterol
        )
        db_session.add(health_data)
        db_session.commit()
        db_session.refresh(health_data)
        return health_data
    except Exception as e:
        db_session.rollback()
        raise Exception(f"Error creating health data: {str(e)}")