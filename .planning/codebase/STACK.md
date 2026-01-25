# Technology Stack

**Analysis Date:** 2026-01-21

## Languages

**Primary:**
- **TypeScript** ~5.6.2 - Frontend application at `spirit-animal-app/src/`
- **Python** 3.12.8 - Backend API at `spirit-animal-backend/`
- **TSX** - React component files (`.tsx`)

**Configuration Files:**
- JSON (package.json, tsconfig.json, vite.config.ts)
- Environment variables (.env files)

## Runtime

**Environment:**
- **Node.js** v22.20.0 - Runs frontend dev server and build tools
- **Python** 3.12.8 - Runs FastAPI backend server

**Package Manager:**
- **pnpm** 9.15.4 - Primary package manager for Node.js (frontend)
- **npm** 11.5.1 - Available fallback
- **pip** - Python package manager (backend)
- Lockfile: `pnpm-lock.yaml` for frontend (not committed, generated fresh)

## Frameworks

**Frontend:**
- **React** 18.3.1 - UI framework at `spirit-animal-app/src/`
- **Vite** 6.0.1 - Build tool and dev server. Config: `spirit-animal-app/vite.config.ts`
- **React Router** 6 - Client-side routing
- **Tailwind CSS** 3.4.16 - Utility-first CSS framework with plugins
- **@vitejs/plugin-react** 4.3.4 - React JSX support in Vite
- **vite-plugin-source-identifier** 1.1.2 - Development helper for source tracing

**Backend:**
- **FastAPI** 0.109.0 - Async web framework. Entry: `spirit-animal-backend/main.py`
- **Uvicorn** 0.27.0 - ASGI server for FastAPI
- **Pydantic** 2.5.3 - Data validation and request/response serialization

**Testing/Dev:**
- **ESLint** 9.15.0 - Linting, with `@eslint/js` and `typescript-eslint`
- **eslint-plugin-react-hooks** 5.0.0 - React hooks linting
- **eslint-plugin-react-refresh** 0.4.14 - React refresh validation

## Key Dependencies

**Frontend - AI & Chat:**
- **@tambo-ai/react** 0.68.0 - React provider for Tambo conversational AI
- **@tambo-ai/typescript-sdk** 0.80.0 - Tambo API client library
- **@modelcontextprotocol/sdk** 1.25.1 - MCP (Model Context Protocol) support

**Frontend - UI Components:**
- **Radix UI** (v1.x) - Headless component library (accordion, dialog, select, tabs, popover, navigation, etc.)
  - Full list: @radix-ui/react-accordion, @radix-ui/react-alert-dialog, @radix-ui/react-avatar, @radix-ui/react-checkbox, @radix-ui/react-collapsible, @radix-ui/react-context-menu, @radix-ui/react-dialog, @radix-ui/react-dropdown-menu, @radix-ui/react-hover-card, @radix-ui/react-label, @radix-ui/react-menubar, @radix-ui/react-navigation-menu, @radix-ui/react-popover, @radix-ui/react-progress, @radix-ui/react-radio-group, @radix-ui/react-scroll-area, @radix-ui/react-select, @radix-ui/react-separator, @radix-ui/react-slider, @radix-ui/react-slot, @radix-ui/react-switch, @radix-ui/react-tabs, @radix-ui/react-toast, @radix-ui/react-toggle, @radix-ui/react-toggle-group, @radix-ui/react-tooltip
- **lucide-react** 0.364.0 - Icon library
- **sonner** 1.7.2 - Toast notifications
- **next-themes** 0.4.4 - Light/dark theme management

**Frontend - Forms & Validation:**
- **react-hook-form** 7.54.2 - Performant form handling
- **@hookform/resolvers** 3.10.0 - Form validation resolvers
- **zod** 3.25.76 - TypeScript-first schema validation

**Frontend - Data & Charts:**
- **recharts** 2.12.4 - Charting library built on React
- **date-fns** 3.0.0 - Date utility library
- **embla-carousel-react** 8.5.2 - Carousel/slider component
- **react-resizable-panels** 2.1.7 - Resizable layout panels
- **vaul** 1.1.2 - Drawer component
- **input-otp** 1.4.2 - OTP input component

**Frontend - Utilities:**
- **class-variance-authority** 0.7.1 - CSS class variant management
- **tailwind-merge** 2.6.0 - Merge Tailwind classes safely
- **tailwindcss-animate** 1.0.7 - Tailwind animation utilities
- **clsx** 2.1.1 - Utility for constructing className strings
- **cmdk** 1.0.0 - Command menu component

**Backend - HTTP & Async:**
- **httpx** 0.26.0 - Async HTTP client library (used for social media fetching and external API calls)
- Built-in **asyncio** - Python's async/await support

**Backend - External APIs:**
- **openai** >=1.50.0 - OpenAI Python client (GPT-4, DALL-E)
- **google-generativeai** >=0.3.0 - Google Generative AI client (Gemini)
- Note: Ideogram API accessed directly via httpx (no SDK)

**Backend - Environment:**
- **python-dotenv** 1.0.0 - Load environment variables from .env files

## Configuration

**Frontend Build Configuration:**
- `spirit-animal-app/vite.config.ts` - Vite configuration with React plugin and path aliases
  - Alias: `@` → `./src`
  - Source identifier plugin enabled in dev mode (disabled in prod)
  - BUILD_MODE environment variable controls production optimization

**Frontend TypeScript Configuration:**
- `spirit-animal-app/tsconfig.json` - Master config with references to app and node configs
- `spirit-animal-app/tsconfig.app.json` - App-specific settings
- `spirit-animal-app/tsconfig.node.json` - Node-specific settings for build tools

**Frontend Styling:**
- `postcss.config.js` (implicit) - PostCSS with Autoprefixer for CSS vendor prefixing
- Tailwind CSS v3.4.16 - Configured via tailwind.config.js (in project root or inferred)

**Backend FastAPI Configuration:**
- `spirit-animal-backend/main.py` - Server entry point with lifespan setup, CORS configuration
- CORS allowed origins: localhost:5173, localhost:3000, configurable via FRONTEND_URL env var

## Environment Configuration

**Frontend Environment Variables:**
- `VITE_API_URL` - Backend API base URL (default: http://localhost:8000)
- `VITE_TAMBO_API_KEY` - Tambo API authentication key
- Example: `spirit-animal-app/.env.example`

**Backend Environment Variables:**
- `OPENAI_API_KEY` - Required for GPT-4 personality analysis and DALL-E image generation
- `GEMINI_API_KEY` - Optional, for Gemini image generation (required if image_provider="gemini")
- `IDEOGRAM_API_KEY` - Optional, for Ideogram image generation (required if image_provider="ideogram")
- `TWITTER_BEARER_TOKEN` - Optional, for Twitter API social data fetching
- `FRONTEND_URL` - Optional, for production frontend domain in CORS config
- Example: `spirit-animal-backend/.env` (in repo root)

## Platform Requirements

**Development:**
- Node.js 20+ (running with 22.20.0)
- Python 3.12+
- pnpm 9+ (recommended) or npm
- macOS/Linux/Windows with standard development tools
- No database required for local development

**Production:**
- Node.js 20+ for frontend deployment
- Python 3.12+ with pip for backend deployment
- FastAPI server (Uvicorn) listening on port 8000 (configurable)
- Frontend served from Vite build output (static files)
- Environment variables configured for:
  - OpenAI API access
  - Frontend origin for CORS
  - Optional: Gemini, Ideogram, Twitter APIs

**Deployment Architecture:**
- Frontend: Static files (compiled React) served from CDN or web server
- Backend: Python/Uvicorn application server (serverless or traditional deployment)
- Communication: REST API over HTTP/HTTPS

---

*Stack analysis: 2026-01-21*
