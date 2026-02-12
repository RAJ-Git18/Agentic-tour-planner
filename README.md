# 🌍 AI Tour Planner

An intelligent tour planning assistant powered by AI that helps users plan trips, get policy information, and make bookings through natural conversation.

## What Does It Do?

This system answers travel-related questions and helps plan tours by:
- **Answering policy questions** (cancellations, refunds, company info)
- **Creating personalized tour plans** based on your preferences
- **Managing bookings** for tours
- **Providing general travel information**

Just ask a question in plain English, and the AI figures out what you need and responds accordingly.

## How It Works

1. **You ask a question**: "What's your cancellation policy?" or "Plan a 3-day trip to Kathmandu"
2. **AI classifies your intent**: Determines if it's about policy, planning, booking, or general info
3. **Retrieves relevant information**: Searches through company documents and tour data
4. **Generates a response**: Uses AI to create a helpful, accurate answer

## Tech Stack

- **Backend**: FastAPI (Python)
- **AI**: Google Gemini 2.5 Flash + LangGraph
- **Search**: Pinecone (vector database with hybrid search)
- **Cache**: Redis
- **Database**: PostgreSQL
- **Authentication**: JWT tokens

## Quick Start

### 1. Install Dependencies
```bash
# Clone the repo
git clone https://github.com/RAJ-Git18/agentic-tour-planner.git
cd tour_planner

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Set Up Environment
Create a `.env` file:
```env
PINECONE_API_KEY=your_pinecone_key
GEMINI_API_KEY=your_google_ai_key
REDIS_HOST=localhost
REDIS_PORT=6379
DATABASE_URL=postgresql://user:password@localhost:5432/tour_planner
SECRET_KEY=your_secret_key
```

### 3. Initialize Database
```bash
alembic upgrade head
```

### 4. Run the Server
```bash
uvicorn main:app --reload
```

Visit http://localhost:8000/docs to see the API documentation.

## How to Use

### Register a User
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "password": "password123"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john&password=password123"
```

### Ask a Question
```bash
curl -X POST "http://localhost:8000/api/user-1/classify" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "user_query": "What is your cancellation policy?",
    "title": "Policy Question"
  }'
```

## Project Structure

```
tour_planner/
├── services/          # Business logic (RAG, embeddings, ranking)
├── routes/            # API endpoints
├── workflow/          # LangGraph workflow (classify → route → respond)
├── models/            # Database models
├── documents/         # Knowledge base (company info, hotels, attractions)
├── config.py          # Settings
└── main.py            # App entry point
```

## Key Features

### 🔍 Smart Search
Uses **hybrid search** combining:
- Semantic search (understands meaning)
- Keyword search (exact matches)
- AI reranking (picks the best results)

### 💬 Conversation Memory
Remembers your conversation using Redis cache.

### 🎯 Accurate Responses
Uses a two-step process:
1. Find 6 relevant documents
2. Rerank to get the top 3 best matches
3. Generate answer using only those documents

### ⚡ Fast Performance
- Caches embeddings in Redis
- Parallel processing
- Async operations

## API Endpoints

| Endpoint | Method | What It Does |
|----------|--------|--------------|
| `/auth/register` | POST | Create new user |
| `/auth/token` | POST | Login and get token |
| `/api/{user_id}/classify` | POST | Ask any question |
| `/api/v1/vector-db/upload` | POST | Upload documents |

## Docker Deployment

```bash
# Build and run
docker-compose up -d
```

This starts the app, PostgreSQL, and Redis together.

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `PINECONE_API_KEY` | Pinecone API key | `abc123...` |
| `GEMINI_API_KEY` | Google AI API key | `xyz789...` |
| `REDIS_HOST` | Redis server host | `localhost` |
| `DATABASE_URL` | PostgreSQL connection | `postgresql://...` |
| `SECRET_KEY` | JWT secret key | `your-secret` |

## Contributing

1. Fork the repo
2. Create a branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -m 'Add feature'`)
4. Push (`git push origin feature/new-feature`)
5. Open a Pull Request

## License

MIT License - feel free to use this project.

## Author

**Raj Simkhada** - [GitHub](https://github.com/RAJ-Git18)
