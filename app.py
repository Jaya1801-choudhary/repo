from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List
import uvicorn
import asyncio
import time

# ==========================================
# Database Setup
# ==========================================
SQLALCHEMY_DATABASE_URL = "sqlite:///./construction.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ProjectPlanDB(Base):
    __tablename__ = "project_plans"
    id = Column(Integer, primary_key=True, index=True)
    property_size_sqft = Column(Float)
    location_zone = Column(String)
    materials_cost_est = Column(Float)
    estimated_duration_days = Column(Integer)
    valuation_insights = Column(JSON)
    recommendations = Column(JSON)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Multimodal Construction Intelligence Platform", version="1.0.0")

# Allow React Frontend to communicate with Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# Pydantic Models
# ==========================================
class RealEstateData(BaseModel):
    property_size_sqft: float
    location_zone: str
    materials_cost_est: float

class PlanningResponse(BaseModel):
    id: int
    status: str
    estimated_duration_days: int
    valuation_insights: dict
    recommendations: List[str]

# ==========================================
# API Endpoints (Demo Mode)
# ==========================================
@app.get("/")
def health_check():
    return {"status": "Active", "message": "Construction Intelligence API is running."}

@app.post("/api/generate-plan", response_model=PlanningResponse)
def generate_project_plan(data: RealEstateData, db: Session = Depends(get_db)):
    """
    Demo endpoint for Project Planning.
    """
    time.sleep(1.5) # Fake loading delay for realistic UI feel
    
    duration = 150
    valuation = {"base_valuation": data.materials_cost_est * 1.8, "market_trend": "Rising"}
    recs = [
        f"Ensure zoning permits for {data.location_zone} area are acquired.", 
        "Optimize material sourcing to stay within budget."
    ]

    new_plan = ProjectPlanDB(
        property_size_sqft=data.property_size_sqft,
        location_zone=data.location_zone,
        materials_cost_est=data.materials_cost_est,
        estimated_duration_days=duration,
        valuation_insights=valuation,
        recommendations=recs
    )
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)

    return PlanningResponse(
        id=new_plan.id,
        status="success",
        estimated_duration_days=new_plan.estimated_duration_days,
        valuation_insights=new_plan.valuation_insights,
        recommendations=new_plan.recommendations
    )

@app.post("/api/analyze-site-image")
async def analyze_site_image(file: UploadFile = File(...)):
    """
    Demo endpoint for Image Analysis.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File provided is not an image.")
    
    await asyncio.sleep(2) # Fake loading delay
    
    return {
        "filename": file.filename,
        "analysis": {
            "overall_safety_status": "Unsafe",
            "hazards_detected": [
                "Workers spotted without safety helmets.",
                "Disorganized wires creating tripping hazards."
            ],
            "structural_issues": [
                "No major cracks visible in the current frame."
            ],
            "immediate_action_required": "Enforce hard hat compliance and clear ground wires."
        }
    }

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)