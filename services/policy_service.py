from services.base_rag import BaseRagService
from utils.logger import logger


class PolicyService(BaseRagService):
    async def run(self, user_query: str) -> str:
        """
        Handles policy-related queries using RAG and re-ranking.
        """
        retriever_results = await self.similarity_search(
            query=user_query, k=6, filter={"filename": "company_info.txt"}
        )

        retrieved_doc_list = [doc.page_content for doc, score in retriever_results]

        top_3_docs = await self.ranking_service.rank_documents(
            user_query, retrieved_doc_list
        )

        logger.info(f"Top 3 docs ----> {top_3_docs}")

        prompt = self._get_policy_prompt(user_query, top_3_docs)
        response = await self.llm.ainvoke(prompt)
        return response.content

    def _get_policy_prompt(self, user_query: str, docs: list) -> str:
        return f"""
        You are an assistant specialized in addressing user query about company policies, cancellations, and refunds.

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
        {"".join(docs)}
        """
