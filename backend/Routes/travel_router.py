from fastapi import APIRouter, HTTPException
from schemas.travel import TravelPlanResponse, TravelQuery
from services.planner_service import PlannerServiceError, planner_service

router = APIRouter(prefix="/travel", tags=["travel"])


@router.post("/query", response_model=TravelPlanResponse)
async def query_travel_agent(payload: TravelQuery):
    """Generate a travel plan along with enrichment layers."""
    try:
        return planner_service.generate_plan(payload.query, payload.layers)
    except PlannerServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:  # pragma: no cover - defensive fail-safe
        raise HTTPException(
            status_code=500,
            detail="Failed to generate travel plan"
        ) from exc
