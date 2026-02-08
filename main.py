import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from sentence_transformers import CrossEncoder

from routes import classify_route, document_ingestion_route, user_register_route
from vector_store.pinecone_store import PineconeStore
from database.database_setup import Base, engine
from workflow.graph import graph


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()

    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    gemini_api_key = os.getenv("GEMINI_API_KEY")

    if not pinecone_api_key:
        raise RuntimeError("Missing Pinecone API key. Set PINECONE_API_KEY or api_key.")

    pc_store = PineconeStore(
        api_key=pinecone_api_key, index_name="tour-planner-vector-store"
    )
    pc_index = pc_store.get_index()

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", google_api_key=gemini_api_key, temperature=0
    )

    emb_model = HuggingFaceEmbeddings(model_name="all-mpnet-base-v2")
    cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")

    app.state.pc_index = pc_index
    app.state.llm = llm
    app.state.emb_model = emb_model
    app.state.cross_encoder = cross_encoder
    app.state.graph = graph

    Base.metadata.create_all(bind=engine)

    yield


app = FastAPI(lifespan=lifespan)

app.include_router(classify_route.router)
app.include_router(document_ingestion_route.router)
app.include_router(user_register_route.router)
