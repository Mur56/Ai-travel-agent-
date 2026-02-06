from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field


class LayerPreferences(BaseModel):
    """Toggles that control which enrichment layers the backend should compute."""
    liveWeather: bool = True
    mapLayers: bool = True
    budgetGuard: bool = False
    localHosts: bool = False
    wellnessSync: bool = False
    sustainMode: bool = False


class PlanSection(BaseModel):
    title: str
    details: List[str] = Field(default_factory=list)


class WeatherSnapshot(BaseModel):
    label: str
    tempC: Optional[float] = None
    description: Optional[str] = None
    rainChance: Optional[int] = None


class WeatherBlock(BaseModel):
    location: str
    summary: Optional[str] = None
    high: Optional[float] = None
    low: Optional[float] = None
    condition: Optional[str] = None
    humidity: Optional[int] = None
    windKph: Optional[float] = None
    daylight: Optional[str] = None
    trend: Optional[str] = None
    rainChance: Optional[int] = None
    forecast: List[WeatherSnapshot] = Field(default_factory=list)


class RouteNode(BaseModel):
    label: str
    latitude: float
    longitude: float
    hint: Optional[str] = None


class RouteMap(BaseModel):
    nodes: List[RouteNode] = Field(default_factory=list)


class BudgetGuardInsight(BaseModel):
    tier: str
    perPerson: str
    totalRange: str
    riskAlerts: List[str] = Field(default_factory=list)
    recommendedSplits: List[str] = Field(default_factory=list)
    currencyCode: Optional[str] = None
    currencySymbol: Optional[str] = None
    localCurrencyCode: Optional[str] = None
    localCurrencySymbol: Optional[str] = None
    perPersonLocal: Optional[str] = None
    localRange: Optional[str] = None
    conversionRate: Optional[float] = None


class LocalHostProfile(BaseModel):
    name: str
    role: str
    specialty: str
    contactHint: str
    availability: str


class WellnessSyncInsight(BaseModel):
    balanceScore: int
    tempo: str
    anchors: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class SustainabilityInsight(BaseModel):
    co2Delta: str
    lowImpactMoves: List[str] = Field(default_factory=list)
    energyNotes: List[str] = Field(default_factory=list)
    status: str


class GalleryImage(BaseModel):
    url: str
    alt: Optional[str] = None
    photographer: Optional[str] = None
    source: Optional[str] = None


class LocaleBrief(BaseModel):
    summary: str
    highlights: List[str] = Field(default_factory=list)


class TravelPlanResponse(BaseModel):
    answer: str
    itinerary: List[PlanSection] = Field(default_factory=list)
    keyMoments: List[str] = Field(default_factory=list)
    weather: Optional[WeatherBlock] = None
    routeMap: Optional[RouteMap] = None
    budgetGuard: Optional[BudgetGuardInsight] = None
    localHosts: List[LocalHostProfile] = Field(default_factory=list)
    wellnessSync: Optional[WellnessSyncInsight] = None
    sustainability: Optional[SustainabilityInsight] = None
    galleryImages: List[GalleryImage] = Field(default_factory=list)
    layers: LayerPreferences = Field(default_factory=LayerPreferences)
    timestamp: str
    status: str = "success"
    localeBrief: Optional[LocaleBrief] = None


class TravelQuery(BaseModel):
    query: str = Field(
        ...,
        min_length=3,
        max_length=2000,
        description="Travel planning prompt"
    )
    layers: Optional[LayerPreferences] = None
