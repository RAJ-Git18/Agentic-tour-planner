import json

from fastapi import HTTPException
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from utils.logger import logger
from sentence_transformers import CrossEncoder
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class Confirmation(BaseModel):
    is_confirmed: bool


class ConfirmationService:
    def __init__(self, llm):
        self.llm = llm

    def confirmation_service(self, user_query: str, message_history: list):
        """
        This service provides the information whether the plan is confirmed or not.
        """

        prompt = self.confirmation_prompt(
            user_query=user_query, message_history=message_history
        )
        structured_llm = self.llm.with_structured_output(Confirmation)
        response = structured_llm.invoke(prompt)
        return response.model_dump()

    def confirmation_prompt(self, user_query: str, message_history: list):
        return f"""
                INPUT:
                user query : {user_query}
                message history: {message_history}

                NOTE: On the basis of the message history and the user query provide the boolean output whether the tour plan is confirmed or not. If the tour is confirmed then return True else return False.
                """
