# Coding Conventions

**Analysis Date:** 2026-01-21

## Naming Patterns

**Files:**
- React components: PascalCase with `.tsx` extension (e.g., `SpiritAnimalCard.tsx`, `OnboardingForm.tsx`)
- TypeScript files: camelCase with `.ts` extension (e.g., `utils.ts`, `tambo.ts`)
- Hooks: camelCase starting with `use-` prefix (e.g., `use-mobile.tsx`)
- Index/barrel files: `index.ts` for exporting grouped modules (e.g., `src/components/chat/index.ts`)

**Functions:**
- camelCase for utility functions: `showNotification()`, `handleSubmit()`, `updateSocialHandle()`
- PascalCase for React component functions: `SpiritAnimalCard()`, `ErrorBoundary()`
- Event handlers: `handle` prefix + action (e.g., `handleSubmit`, `handleShare`, `handleDownload`, `handleReset`)

**Variables:**
- camelCase for state and local variables: `notification`, `isDownloading`, `profile`, `userName`
- Boolean variables often prefixed with `is` or `can`: `isMobile`, `isDevelopment`, `canProceedStep1`
- Underscore-prefixed for unused parameters (ESLint rule): `(_, index)` for destructured iterables

**Types & Interfaces:**
- PascalCase with `Interface` suffix or descriptive name: `SpiritAnimalCardProps`, `NotificationType`, `UserProfile`, `SocialHandle`
- Type union aliases: descriptive PascalCase (e.g., `type AppState = "form" | "loading" | "result"`)
- Enum-like constants: SCREAMING_SNAKE_CASE for application constants: `MOBILE_BREAKPOINT`, `API_BASE`, `ALLOWED_ORIGINS`

## Code Style

**Formatting:**
- 2-space indentation (observed throughout all source files)
- No explicit Prettier config found; code follows consistent formatting standards
- Semicolons used throughout (not optional)
- Single quotes for strings in most files, double quotes in some (inconsistent but both acceptable)

**Linting:**
- ESLint with TypeScript support configured in `spirit-animal-app/eslint.config.js`
- Extends: `@eslint/js`, `typescript-eslint/recommended`, React hooks rules, React Refresh rules
- Key rules:
  - `@typescript-eslint/no-unused-vars`: warns on unused variables, ignores params starting with `_`
  - `@typescript-eslint/no-explicit-any`: warns when using `any` type
  - `react-refresh/only-export-components`: warns if exporting non-components from component files

**TypeScript:**
- Strict mode enabled (`tsconfig.json`)
- Path alias `@/*` maps to `src/*` for cleaner imports
- Type annotations required on props, state, and function returns
- Null checking enforced (e.g., `error instanceof Error`)

## Import Organization

**Order:**
1. React and React-related imports: `import React from 'react'`, `import { useState } from 'react'`
2. Third-party library imports: `@radix-ui`, `lucide-react`, `@tambo-ai/react`, `zod`, etc.
3. Local component imports: relative or using `@/` alias
4. Type/interface imports: grouped with component imports

**Path Aliases:**
- `@/*` resolves to `src/*` for readable absolute imports
- Examples: `@/components/...`, `@/lib/...`, `@/hooks/...`

**Barrel Files:**
- `src/components/chat/index.ts` exports `SpiritAnimalChat` for cleaner imports

## Error Handling

**Patterns:**

**Async/Fetch Errors:**
- Try/catch blocks wrapping fetch and async operations
- Status checking before parsing response: `if (!response.ok) throw new Error(...)`
- Error differentiation: `err instanceof Error ? err.message : "fallback message"`
- Examples in `src/App.tsx` (lines 67-90), `src/components/SpiritAnimalCard.tsx` (lines 73-98)

**React Error Handling:**
- ErrorBoundary class component in `src/components/ErrorBoundary.tsx`
- Catches lifecycle errors and renders fallback UI
- Serialization helper for unknown error types (handles Error, string, or JSON)
- Development-only error details exposed in details/summary elements
- Wrapped at app root in `src/main.tsx`

**User-Facing Errors:**
- Notification component with `type: 'success' | 'error'` and auto-dismiss (4s timeout)
- Toast-style notifications (fixed position, dismissible)

## Logging

**Framework:** Native `console` object (no logger library)

**Patterns:**
- `console.error()` for errors and unexpected failures
- `console.log()` for debug information and flow tracking
- Context-prefixed logs in Tambo integration: `console.log("[Tambo Tool V2] message")`
- Verbose parameter toggles detailed output (e.g., `test_interpretation.py`: `verbose=True`)

**Examples:**
- `console.error('ErrorBoundary caught an error:', error, errorInfo);` (line 45, ErrorBoundary.tsx)
- `console.log("[Tambo Tool V2] generateSpiritAnimal called with:", params);` (tambo.ts)
- Python backend uses emoji-prefixed messages for clarity: `print("✅ OpenAI API key configured")`

## Comments

**When to Comment:**
- Complex algorithm or non-obvious logic
- Business logic that explains "why" not "what"
- Workarounds or temporary solutions
- Section dividers for multi-step processes (Python backend: `# ============================================================================`)

**JSDoc/TSDoc:**
- File-level comments describe purpose: `@file`, `@description`
- Function docstrings in Python: triple-quoted with Args/Returns sections
- Python test scripts include detailed docstrings and examples

**Examples:**
- `src/App.tsx` (lines 1-6): File-level description with purpose and functionality
- `test_interpretation.py` (lines 2-17): Detailed docstring with usage examples
- Inline comments for non-obvious behavior: `// Auto-dismiss after 4 seconds`

## Function Design

**Size:** Functions kept focused and under 50 lines typically. Larger functions (e.g., `interpret_personality()` in Python) documented with clear sections.

**Parameters:**
- Props interfaces for React component parameters
- Single object destructuring for multiple params (e.g., `{ result, userName, onReset }`)
- Optional parameters marked with `?` in types
- Default values in function signatures or state initialization

**Return Values:**
- Type-annotated return types: `Promise<dict>`, `SpiritResult | null`, `React.ReactNode`
- Components return JSX
- Utility functions return typed values

## Module Design

**Exports:**
- Named exports for components: `export function SpiritAnimalCard(...)`
- Named exports for utilities: `export function cn(...)`
- Default exports for React component modules in some cases (e.g., `export default App`)

**Barrel Files:**
- `src/components/chat/index.ts` re-exports from children for grouped access

## State Management

**Frontend:**
- React hooks only: `useState`, `useEffect`, `useRef`, `useContext` (from custom hooks)
- Local state for form data, loading states, errors
- Props drilling for simple cases (no Redux/Context Provider needed yet)
- Controlled components with state + onChange handlers

**Backend:**
- Stateless FastAPI endpoints returning models
- Request/Response models defined with Pydantic (`BaseModel`)
- V2 endpoints receive conversation data, generate results stateless

## Styling

**Framework:** Tailwind CSS with PostCSS and Autoprefixer

**Patterns:**
- Utility-first approach: `className="px-4 py-3 rounded-lg border border-gray-300"`
- Responsive prefixes: none observed in current codebase (mobile-first)
- Dark mode class: `darkMode: ['class']` configured but not actively used
- Custom theme colors defined in `tailwind.config.js`: primary (green), secondary (blue), accent (orange)

**Animation:**
- Tailwind built-in: `animate-fadeIn`, `animate-bounce`
- Custom keyframes for accordion: accordion-down, accordion-up

## Third-Party Integration Patterns

**API Integration:**
- Environment variables for endpoints: `VITE_API_URL`, `VITE_TAMBO_API_KEY`
- Fetch API for HTTP requests
- Request models (Pydantic) for type safety

**UI Components:**
- Radix UI primitives for accessible components (Dialog, Select, Toast, etc.)
- shadcn/ui pattern observed (uses clsx + tailwind-merge utility)

**Form Handling:**
- React Hook Form with Zod validation schema
- Manual step-based form (OnboardingForm.tsx): progress tracking with state

**Validation:**
- Zod schemas for runtime type checking: `spiritRequestV2Schema.parse()`
- TypeScript compile-time checking as primary validation

---

*Convention analysis: 2026-01-21*
