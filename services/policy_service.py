from services.base_rag import BaseRagService
from utils.logger import logger


class PolicyService(BaseRagService):
    async def run(self, user_query: str) -> str:
        """
        Handles policy-related queries using RAG and re-ranking.
        """
        retriever_results = self.similarity_search(
            query=user_query, k=6, filter={"filename": "company_info.txt"}
        )

        retrieved_doc_list = []
        score_list = []

        for doc, score in retriever_results:
            logger.info(f"doc---->{doc.page_content}")
            if self.cross_encoder:
                # Cross-encoder is CPU heavy, we'll keep it sync for now
                # but run in a thread if we wanted true non-blocking
                score = self.cross_encoder.predict([(user_query, doc.page_content)])
                logger.info(f"Score----->{score}")

            retrieved_doc_list.append(doc.page_content)
            score_list.append(score)

        pairs = list(zip(score_list, retrieved_doc_list))
        pairs.sort(reverse=True)
        _, retrieved_docs = zip(*pairs)

        top_3_docs = retrieved_docs[:3]

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
