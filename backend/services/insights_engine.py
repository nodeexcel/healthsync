import os
import json
from fastapi import APIRouter, HTTPException
from langchain import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

router = APIRouter()

class UserHealthData(Base):
    __tablename__ = "user_health_data"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    health_info = Column(Text)

Base.metadata.create_all(bind=engine)

openai_api_key = os.getenv("OPENAI_API_KEY")
llm = OpenAI(api_key=openai_api_key)

prompt_template = PromptTemplate(
    input_variables=["health_info"],
    template="Based on the following health information, provide personalized health insights: {health_info}"
)

insight_chain = LLMChain(llm=llm, prompt=prompt_template)

@router.post("/generate-insights/{user_id}")
async def generate_insights(user_id: int):
    db = SessionLocal()
    try:
        user_health_data = db.query(UserHealthData).filter(UserHealthData.user_id == user_id).first()
        if not user_health_data:
            raise HTTPException(status_code=404, detail="User health data not found")

        health_info = user_health_data.health_info
        insights = insight_chain.run(health_info=health_info)

        return {"user_id": user_id, "insights": insights}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()