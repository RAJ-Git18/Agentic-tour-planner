import json

from fastapi import HTTPException
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from utils.logger import logger
from sentence_transformers import CrossEncoder
from typing import Dict, List, Any
from pydantic import BaseModel, Field


class DayPlan(BaseModel):
    day: int
    title: str
    schedule: List[str] = Field(description="Bullet-like steps with times")
    hotel: str
    transport: List[str]
    tips: List[str]


class TourPlan(BaseModel):
    summary: str = Field(description="Summary of the tour plan")
    days: List[DayPlan]
    sources_used: List[str] = Field(
        description="Names of attractions/hotels/travel info used"
    )


class MissingConstraints(BaseModel):
    summary: str = Field(description="Summary of the missing constraints")


class TourConstraints(BaseModel):
    days: int | None = None
    from_city: str | None = None
    to_city: str | None = None


class RagService:
    def __init__(self, pc_index: Any, llm):
        self.pc_index = pc_index
        self.emb_model = HuggingFaceEmbeddings(model_name="all-mpnet-base-v2")
        self.cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")
        self.vector_store = PineconeVectorStore(
            index=self.pc_index, embedding=self.emb_model
        )
        self.llm = llm

    def policy_service(self, user_query: str) -> str:
        """
        This service provides the information related to the company policies on the basis
        of the user query
        """

        self.retriever = self.vector_store.similarity_search_by_vector_with_score(
            embedding=self.emb_model.embed_query(user_query),
            k=6,
            filter={"filename": "company_info.txt"},
        )

        retrieved_doc_list = []
        score_list = []
        for doc, score in self.retriever:
            logger.info(f"doc---->{doc.page_content}")
            score = self.cross_encoder.predict([(user_query, doc.page_content)])
            logger.info(f"Score----->{score}")

            retrieved_doc_list.append(doc.page_content)
            score_list.append(score)

        pairs = list(zip(score_list, retrieved_doc_list))
        pairs.sort(reverse=True)
        scores, retrieved_docs = zip(*pairs)

        logger.info(f"The reranked retrieved docs-------> \n{retrieved_docs}")

        top_3_docs = retrieved_docs[:3]

        logger.info(f"final reranked top 3 docs---> {top_3_docs}")
        prompt = f"""
                You are an assistant specialized in addreasing user query about company policies, cancellations, and refunds.

                RULES:
                1. Use ONLY the information provided in the Documents section.
                2. Do NOT use prior knowledge or assumptions.
                3. Keep the answer short, precise, and factual. Make sure to provide the answer
                within a single paragraph without any kind of styling.
                4. If the documents do not contain the answer, reply exactly:
                "I am unable to answer that question based on the available information."

                User query:
                {user_query}

                Documents:
                {"".join(top_3_docs)}
                         """

        response = self.llm.invoke(prompt)
        return response.text

    def tour_planning_service(self, user_query: str, message_history: list):
        """
        This service plan a tour on that best fit the user query.
        """

        prompt = self.entity_retriever_prompt(
            user_query=user_query, message_history=message_history
        )
        structured_llm = self.llm.with_structured_output(TourConstraints)
        entity = structured_llm.invoke(prompt)
        entity_metadata = entity.model_dump()
        missing_constraints = [k for k, v in entity_metadata.items() if v is None]

        logger.info(f"missing constraints---->{missing_constraints}")
        logger.info(f"entity from llm invoke---->{entity_metadata}")

        if missing_constraints:
            missing_constraints_prompt = self.missing_constraints_prompt(
                missing_constraints
            )
            structured_llm = self.llm.with_structured_output(MissingConstraints)
            missing_constraints = structured_llm.invoke(missing_constraints_prompt)
            response = missing_constraints.model_dump()
            return response

        self.travel_hour_retriever = self.fetch_travel_hour(user_query, entity_metadata)
        self.hotel_retriever = self.fetch_hotels(user_query, entity_metadata)
        self.tour_attraction_retriever = self.fetch_tour_attraction(
            user_query, entity_metadata
        )

        tour_attraction_list = [
            docs.page_content for docs, score in self.tour_attraction_retriever
        ]
        tour_travel_hour_list = [
            docs.page_content for docs, score in self.travel_hour_retriever
        ]
        tour_hotel_list = [docs.page_content for docs, score in self.hotel_retriever]

        prompt = f"""
You are an expert tour planner. Based on the user's query and the provided information, create a comprehensive {entity_metadata["days"]}-day tour plan from {entity_metadata["from_city"]} to {entity_metadata["to_city"]}.

USER QUERY:
{user_query}

TOUR INFORMATION:

Attractions in {entity_metadata["to_city"]}:
{tour_attraction_list}

Travel Information:
{tour_travel_hour_list}

Available Hotels:
{tour_hotel_list}

INSTRUCTIONS:
1. Create a detailed day-by-day itinerary for {entity_metadata["days"]} days
2. Include specific attractions to visit each day with recommended timings
3. Suggest the best hotel option based on the provided information
4. Include travel time and mode of transportation
5. Provide practical tips and recommendations
6. Make the plan engaging and well-structured
7. Use ONLY the information provided above - do not add information not present in the data
8. Format the response in a clear, readable manner with proper sections


        """
        structured_llm = self.llm.with_structured_output(TourPlan)
        response = structured_llm.invoke(prompt)
        logger.info(f"tour plan from llm invoke---->{response.model_dump()}")
        return response.model_dump()

    def entity_retriever_prompt(self, user_query: str, message_history: list):
        return f"""
                INPUT:
                user query : {user_query}
                message history: {message_history}

                Role: You are an AI assistant to retrieve the necessary entity
                from the above given user query and provide in the following json 
                format. We have got only 5 cities in the database, so make sure to consider the full form of the city name
                and they are "kathmandu", "pokhara", "chitwan", "lumbini", "nagarkot".

                EXAMPLE:
                user query: Plan a 5-day trip to XYZ from ABC.

                also make sure to consider the full form like "ktm" instead of "kathmandu" and understand the intent of the user query 
                to list the above cities only.

                Note: also check for the message history to identify whether any of the entity are already provided by the user or not if yes add that entity to the output.
                """

    def missing_constraints_prompt(self, missing_constraints: list):
        return f"""
        If any missing constraints are found respond to the user politely to fill the missing constraints to continue the tour planning.
        MISSING CONSTRAINTS:
        {missing_constraints}
        """

    def fetch_tour_attraction(self, user_query, entity_metadata):
        return self.vector_store.similarity_search_by_vector_with_score(
            embedding=self.emb_model.embed_query(user_query),
            k=3,
            filter={
                "city": entity_metadata["to_city"].strip().lower(),
                "type": "attraction",
            },
        )

    def fetch_travel_hour(self, user_query, entity_metadata):
        return self.vector_store.similarity_search_by_vector_with_score(
            embedding=self.emb_model.embed_query(user_query),
            k=3,
            filter={
                "to_city": entity_metadata["to_city"].strip().lower(),
                "from_city": entity_metadata["from_city"].strip().lower(),
                "type": "travel_hour",
            },
        )

    def fetch_hotels(self, user_query, entity_metadata):
        return self.vector_store.similarity_search_by_vector_with_score(
            embedding=self.emb_model.embed_query(user_query),
            k=3,
            filter={
                "city": entity_metadata["to_city"].strip().lower(),
                "type": "hotels",
            },
        )
