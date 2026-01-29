from typing import List, Dict, Any
from services.base_rag import BaseRagService
from schemas.rag_schemas import TourConstraints, MissingConstraints, TourPlan
from utils.logger import logger
import asyncio


class TourPlannerService(BaseRagService):
    ALLOWED_CITIES = ["kathmandu", "pokhara", "chitwan", "lumbini", "nagarkot"]

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
            self._fetch_data(user_query, entity_metadata, "attraction"),
            self._fetch_travel_hours(user_query, entity_metadata),
            self._fetch_data(user_query, entity_metadata, "hotels"),
        )

        # 3. Generate the tour plan
        prompt = self._get_planning_prompt(
            user_query, entity_metadata, attractions, travel_info, hotels
        )
        structured_llm = self.llm.with_structured_output(TourPlan)
        response = await structured_llm.ainvoke(prompt)

        return response.model_dump()

    async def _get_tour_constraints(
        self, user_query: str, message_history: list
    ) -> Dict[str, Any]:
        prompt = f"""
                INPUT:
                user query : {user_query}
                message history: {message_history}

                Role: You are an AI assistant to retrieve the necessary entity
                from the above given user query and provide in the following json 
                format. We have got only 5 cities in the database: {self.ALLOWED_CITIES}.
                Make sure to consider city full names.

                Note: check message history for existing entities.
                """
        structured_llm = self.llm.with_structured_output(TourConstraints)
        entity = await structured_llm.ainvoke(prompt)
        return entity.model_dump()

    async def _handle_missing_constraints(self, missing_constraints: list):
        prompt = f"""
        If any missing constraints are found respond to the user politely to fill the missing constraints to continue the tour planning.
        Promote our tour package for: {", ".join(self.ALLOWED_CITIES)}.
        MISSING CONSTRAINTS: {missing_constraints}
        """
        structured_llm = self.llm.with_structured_output(MissingConstraints)
        missing_constraints_resp = await structured_llm.ainvoke(prompt)
        return missing_constraints_resp.model_dump()

    def _fetch_data(self, query: str, metadata: dict, data_type: str):
        results = self.similarity_search(
            query=query,
            k=3,
            filter={
                "city": metadata["to_city"].strip().lower(),
                "type": data_type,
            },
        )
        return [doc.page_content for doc, score in results]

    def _fetch_travel_hours(self, query: str, metadata: dict):
        results = self.similarity_search(
            query=query,
            k=3,
            filter={
                "to_city": metadata["to_city"].strip().lower(),
                "from_city": metadata["from_city"].strip().lower(),
                "type": "travel_hour",
            },
        )
        return [doc.page_content for doc, score in results]

    def _get_planning_prompt(self, user_query, metadata, attractions, travel, hotels):
        return f"""
        You are an expert tour planner. Create a {metadata["days"]}-day tour plan from {metadata["from_city"]} to {metadata["to_city"]}.
        
        USER QUERY: {user_query}
        
        DATA:
        - Attractions: {attractions}
        - Travel Info: {travel}
        - Hotels: {hotels}

        INSTRUCTIONS:
        1. {metadata["days"]}-day itinerary.
        2. Specific timings.
        3. Best hotel from data.
        4. Travel mode/time.
        5. Use ONLY provided info.
        6. Title: "Tour Plan for {metadata["from_city"]} to {metadata["to_city"]}"
        """
