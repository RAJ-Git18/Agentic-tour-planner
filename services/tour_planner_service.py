from typing import List, Dict, Any
from services.base_rag import BaseRagService
from schemas.rag_schemas import TourConstraints, MissingConstraints, TourPlan
from utils.logger import logger
from prompts.ai_prompts import AIPrompts
import asyncio
from pinecone_text.sparse import SpladeEncoder
from config import settings

sparse_encoder = SpladeEncoder()


class TourPlannerService(BaseRagService):
    ALLOWED_CITIES = settings.ALLOWED_CITIES

    async def run(self, user_query: str, message_history: list):
        """
        Main entry point for tour planning.
        """
        # 1. Extract constraints
        entity_metadata = await self._get_tour_constraints(user_query, message_history)
        missing_constraints = [k for k, v in entity_metadata.items() if v is None]

        if missing_constraints:
            return await self._handle_missing_constraints(missing_constraints)

        # 2. Fetch relevant data from vector store
        attractions, travel_info, hotels = await asyncio.gather(
            self._fetch_data(user_query, entity_metadata, "tour_attraction"),
            self._fetch_travel_hours(user_query, entity_metadata),
            self._fetch_data(user_query, entity_metadata, "hotels"),
        )

        # 3. Generate the tour plan
        prompt = AIPrompts.get_planning_prompt(
            user_query, entity_metadata, attractions, travel_info, hotels
        )
        structured_llm = self.llm.with_structured_output(TourPlan)
        response = await structured_llm.ainvoke(prompt)

        return response.model_dump()

    async def _get_tour_constraints(
        self, user_query: str, message_history: list
    ) -> Dict[str, Any]:
        prompt = AIPrompts.get_tour_constraint_prompt(
            user_query=user_query,
            message_history=message_history,
            allowed_cities=self.ALLOWED_CITIES,
        )
        structured_llm = self.llm.with_structured_output(TourConstraints)
        entity = await structured_llm.ainvoke(prompt)
        return entity.model_dump()

    async def _handle_missing_constraints(self, missing_constraints: list):
        prompt = AIPrompts.get_missing_constraints_prompt(
            missing_constraints=missing_constraints,
            allowed_cities=self.ALLOWED_CITIES,
        )
        structured_llm = self.llm.with_structured_output(MissingConstraints)
        missing_constraints_resp = await structured_llm.ainvoke(prompt)
        return missing_constraints_resp.model_dump()

    async def _fetch_data(self, query: str, metadata: dict, data_type: str):
        results = await self.hybrid_search(
            query=query,
            k=3,
            filter={
                "city": metadata["to_city"].strip().lower(),
                "type": data_type,
            },
        )
        return [match["metadata"]["content"] for match in results["matches"]]

    async def _fetch_travel_hours(self, query: str, metadata: dict):
        results = await self.hybrid_search(
            query=query,
            k=3,
            filter={
                "to_city": metadata["to_city"].strip().lower(),
                "from_city": metadata["from_city"].strip().lower(),
                "type": "travel_hour",
            },
        )
        return [match["metadata"]["content"] for match in results["matches"]]
