from utils.logger import logger
from pydantic import BaseModel


class Intent(BaseModel):
    intent: str


class ClassifyService:
    """
    Classifies the intent of the user query like policy, tour planning, booking or general inquiry
    """

    def __init__(self, emb_model, rag_service, llm):
        self.emb_model = emb_model
        self.rag_service = rag_service
        self.llm = llm

    def classify(self, user_query, message_history):
        prompt = f"""
            user message history: {message_history}
            Help to classify the user intent for the given user query into policy, tour planning, booking or general inquiry.
            user query: {user_query}
            If the question is related to the company policies, cancellations, refunds, or terms of service then return policy
            If the question is related to the tour planning, creating an itinerary, or finding attractions then return planning
            If the question is related to booking a trip, hotel, or flight then return booking
            If the question is related to general inquiry or chitchat then return general inquiry

            note: consider the user message history if any while classifying the intent as the user might be trying to continue the 
            conversation for the certain intent especially tour planning
        """
        structured_llm = self.llm.with_structured_output(Intent)
        response = structured_llm.invoke(prompt)
        intent = response.model_dump()
        logger.info(f"classify service ----> {intent}")
        return intent["intent"]
