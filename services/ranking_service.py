from concurrent.futures import ThreadPoolExecutor
import asyncio


class RankingService:
    _executor = ThreadPoolExecutor(max_workers=2)

    def __init__(self, model):
        self.model = model

    async def rank_documents(self, query: str, documents: list[str], top_k: int = 3):
        """
        Takes a query and a list of docs, and returns them sorted by relevance.
        """
        if not documents:
            return []

        # Prepare pairs for the cross-encoder
        pairs = [[query, doc] for doc in documents]

        # Use the thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        scores = await loop.run_in_executor(self._executor, self.model.predict, pairs)

        # Sort and return
        scored_docs = sorted(zip(scores, documents), reverse=True, key=lambda x: x[0])
        return [doc for score, doc in scored_docs[:top_k]]
