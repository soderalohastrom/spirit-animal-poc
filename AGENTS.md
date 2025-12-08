# Spirit Animal POC

## Overview
Full-stack spirit animal generator with React frontend and FastAPI backend. Uses OpenAI for personality analysis and image generation.

## Architecture
- Frontend: React + Vite + TypeScript + Tailwind CSS + Radix UI
- Backend: FastAPI + Python + Pydantic
- AI: OpenAI GPT-4 for analysis, DALL-E 3 for images
- Package manager: pnpm (frontend), pip (backend)

## Commands

### Frontend (spirit-animal-app/)
```bash
pnpm dev              # Start dev server
pnpm build           # Build for production  
pnpm build:prod      # Build with prod optimizations
pnpm lint            # Run ESLint
pnpm preview         # Preview build
```

### Backend (spirit-animal-backend/)
```bash
python main.py       # Start dev server on :8000
pip install -r requirements.txt  # Install deps
```

## Code Style

### TypeScript/React
- Use `@/*` path aliases for imports
- Component exports: `export function ComponentName()`
- Interface exports: `export interface TypeName`
- Prefer explicit return types for functions
- Use `const` for component declarations
- Error handling: try/catch with user-friendly messages

### Python/FastAPI  
- Type hints required for all functions
- Pydantic models for request/response
- Async/await for I/O operations
- Docstrings for all endpoints
- Environment variables via python-dotenv

### Naming
- Components: PascalCase (e.g., `SpiritAnimalCard`)
- Functions: camelCase (e.g., `handleSubmit`)
- Variables: camelCase
- Constants: UPPER_SNAKE_CASE
- Files: kebab-case for utilities, PascalCase for components

### Import Organization
1. React imports
2. Third-party libraries  
3. Local components (with `@/*` alias)
4. Types/interfaces

## Gotchas
- Frontend expects API at `VITE_API_URL` env var or localhost:8000
- Backend requires OPENAI_API_KEY in .env
- CORS allows all origins - restrict in production
- No test framework configured yet