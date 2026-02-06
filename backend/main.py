from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import traceback

from schemas.travel import TravelPlanResponse, TravelQuery
from services.planner_service import PlannerServiceError, planner_service

# -----------------------
# Load environment variables
# -----------------------
load_dotenv()

app = FastAPI()

# -----------------------
# CORS Setup
# -----------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # use specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# Include routers
# -----------------------
from Routes.main_router import main_router
app.include_router(main_router)

# -----------------------
# Startup: load LLM and build agent once
# -----------------------
@app.on_event("startup")
def startup_event():
    try:
        print("Initializing agent graph...")
        planner_service.warmup()
        print(" Agent graph initialized successfully")
    except Exception as e:
        print(" Failed to initialize agent graph")
        traceback.print_exc()
        raise e

# -----------------------
# Travel query endpoint
# -----------------------
@app.post("/travel/query", response_model=TravelPlanResponse)
async def travel_query(payload: TravelQuery):
    try:
        print("User question:", payload.query)
        return planner_service.generate_plan(payload.query, payload.layers)
    except PlannerServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:  # pragma: no cover
        print(" Error in /travel/query endpoint")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Unhandled error while generating plan") from exc