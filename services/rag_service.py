import json
from typing import Dict, List, Any, Optional
from utils.logger import logger

from services.policy_service import PolicyService
from services.tour_planner_service import TourPlannerService


class RagService:
    """
    Gold Standard: True Dependency Injection.
    This class is now 'decoupled'. It doesn't care how PolicyService
    or TourPlannerService are built; it just uses them.
    """

    def __init__(self, policy_service: PolicyService, tour_planner: TourPlannerService):
        self.policy_service_impl = policy_service
        self.tour_planner_impl = tour_planner

    async def policy_service(self, user_query: str) -> str:
        return await self.policy_service_impl.run(user_query)

    async def tour_planning_service(self, user_query: str, message_history: list):
        return await self.tour_planner_impl.run(user_query, message_history)
