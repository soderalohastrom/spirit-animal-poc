# Spirit Animal POC

Discover your spirit animal through AI-guided conversation. Chat with a mystical Spirit Animal Guide who asks 7 questions about your personality, then reveals your perfect spirit animal with custom AI-generated artwork.

![Spirit Animal Example](assets/example-raven.png)

## Features

- **Conversational Discovery** - 7-turn guided conversation via Tambo AI SDK
- **Personality Interpretation** - GPT-4o analyzes your responses to find the perfect match
- **AI-Generated Artwork** - Gemini creates unique spirit animal portraits in various art styles
- **Multiple Choice + Freeform** - Quick A/B/C/D options with "Other" for custom responses

## Quick Start

```bash
# 1. Clone and setup backend
cd spirit-animal-backend
python -m venv .venv311
source .venv311/bin/activate
pip install -r requirements.txt

# 2. Add API keys to .env
cat > .env << EOF
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...
IMGBB_API_KEY=...
EOF

# 3. Start backend
python main.py  # http://localhost:8000

# 4. In new terminal, start frontend
cd spirit-animal-app
pnpm install
pnpm dev  # http://localhost:5173
```

## How It Works

```
User answers 7 questions
        │
        ▼
Tambo assembles personality summary
        │
        ▼
GPT-4o interprets → Spirit Animal + Art Medium
        │
        ▼
Gemini generates image → imgBB hosts it
        │
        ▼
Beautiful result card with your spirit animal
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | React 18 + Vite + TypeScript + Tailwind |
| AI Chat | Tambo SDK |
| Backend | FastAPI + Python 3.11 |
| LLM | GPT-4o (OpenAI) |
| Image Gen | Gemini (`gemini-2.0-flash-exp-image-generation`) |
| Image Hosting | imgBB |

## The 7 Questions

1. **Name** - What should I call you?
2. **Energy Mode** - Leader, adapter, or observer?
3. **Social Pattern** - Solitude, close circle, or crowd?
4. **Self-Description** - How would someone who knows you describe you?
5. **Joy Source** - What brings you genuine joy?
6. **Aspirations** - What matters most right now?
7. **Element Affinity** - Fire, water, earth, or air?

## API Keys Required

| Key | Purpose | Get it at |
|-----|---------|-----------|
| `OPENAI_API_KEY` | GPT-4o personality analysis | [platform.openai.com](https://platform.openai.com) |
| `GEMINI_API_KEY` | Image generation | [aistudio.google.com](https://aistudio.google.com) |
| `IMGBB_API_KEY` | Image hosting | [api.imgbb.com](https://api.imgbb.com) |

## Development

See [CLAUDE.md](CLAUDE.md) for architecture details and [STATUS.md](STATUS.md) for project status.

**Debug Panel:** Press `Ctrl+Shift+D` to see Tambo conversation internals.

## License

MIT
