from typing import List, Optional, Any
from pydantic import BaseModel, Field


class DayPlan(BaseModel):
    day: int
    title: str
    schedule: List[str] = Field(description="Bullet-like steps with times")
    hotel: str
    transport: List[str]


class TourPlan(BaseModel):
    title: Optional[str] = None
    response: List[DayPlan] = Field(description="Day wise planning of the tour")
    confirmation: Optional[str] | None = Field(
        description="If the complete tour plan is created ask the user whether to confirm the tour or regenerate the tour plan "
    )
    sources_used: List[str] = Field(
        description="Names of attractions/hotels/travel info used"
    )


class MissingConstraints(BaseModel):
    response: str


class TourConstraints(BaseModel):
    days: int | None = None
    from_city: str | None = None
    to_city: str | None = None
