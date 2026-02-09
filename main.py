import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from sentence_transformers import CrossEncoder
from redis.asyncio import Redis

from routes import classify_route, document_ingestion_route, user_register_route
from vector_store.pinecone_store import PineconeStore
from workflow.graph import graph
from config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()

    pinecone_api_key = settings.PINECONE_API_KEY
    gemini_api_key = settings.GEMINI_API_KEY

    if not pinecone_api_key or not gemini_api_key:
        raise RuntimeError("Missing API keys in environment.")

    pc_store = PineconeStore(
        api_key=pinecone_api_key, index_name=settings.PINECONE_INDEX
    )
    pc_index = pc_store.get_index()

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", google_api_key=gemini_api_key, temperature=0
    )

    emb_model = HuggingFaceEmbeddings(model_name="all-mpnet-base-v2")
    cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")

    redis_client = Redis(
        host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True
    )

    app.state.pc_index = pc_index
    app.state.llm = llm
    app.state.emb_model = emb_model
    app.state.cross_encoder = cross_encoder
    app.state.graph = graph
    app.state.redis_client = redis_client

    Base.metadata.create_all(bind=engine)

    yield

    await redis_client.close()


app = FastAPI(lifespan=lifespan)

app.include_router(classify_route.router)
app.include_router(document_ingestion_route.router)
app.include_router(user_register_route.router)
