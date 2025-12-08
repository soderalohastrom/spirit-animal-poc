# Spirit Animal Backend

FastAPI backend for the Spirit Animal generator app.

## Setup

1. Create a virtual environment:
```bash
cd spirit-animal-backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

4. Run the server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

- `GET /` - Health check
- `GET /api/health` - Detailed health check
- `POST /api/spirit-animal` - Generate spirit animal

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for GPT-4 and DALL-E |
| `TWITTER_BEARER_TOKEN` | No | Twitter API bearer token |
