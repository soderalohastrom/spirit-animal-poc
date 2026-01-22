# Testing Patterns

**Analysis Date:** 2026-01-21

## Test Framework

**Frontend:**
- No testing framework currently configured (no Jest, Vitest, or similar)
- Type checking via TypeScript (`tsc -b`) used as primary validation
- Manual testing only

**Backend:**
- No unit test framework configured
- Manual test scripts using Python stdlib

**Run Commands:**
```bash
# Frontend: TypeScript compilation check
cd spirit-animal-app
npm run build              # Builds and validates TypeScript

# Frontend: Development (to manually test)
npm run dev                # Start Vite dev server

# Backend: Manual test scripts
cd spirit-animal-backend
python test_interpretation.py       # Test interpretation flow
python test_image_generation.py     # Test image generation
```

## Test File Organization

**Location:**
- Frontend: No test files currently (`*.test.tsx`, `*.spec.tsx` not found)
- Backend: Test scripts at root of `spirit-animal-backend/`:
  - `test_interpretation.py`: Tests spirit animal interpretation
  - `test_image_generation.py`: Tests image generation with different providers

**Naming:**
- Backend test scripts: `test_*.py` convention
- Executable: `#!/usr/bin/env python3` shebang for direct execution

**Structure:**
```
spirit-animal-backend/
├── test_interpretation.py      # Manual test for interpretation flow
├── test_image_generation.py    # Manual test for image generation
└── main.py                     # FastAPI application
```

## Test Structure

**Backend Test Script Pattern** (`test_interpretation.py`):

```python
#!/usr/bin/env python3
"""
Detailed docstring explaining:
- Phase/purpose
- What it tests
- Expected inputs/outputs
- Usage instructions
"""

# Environment setup
import os
import sys
import json
from dotenv import load_dotenv

# Load .env from parent directories
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv()

# Verify dependencies (API keys, etc.)
if not os.getenv("OPENAI_API_KEY"):
    print("❌ Error: OPENAI_API_KEY not found...")
    sys.exit(1)

# Define test data
TEST_SUMMARY = """Sample input data..."""

# Core test function
def interpret_personality(summary: str, verbose: bool = True) -> dict:
    """Function with Args/Returns documentation."""
    # Logic with emoji-prefixed console output for clarity
    print(f"\n{'='*60}")
    print(f"🔮 OPERATION HEADER")
    return result

# Main execution
def main():
    if len(sys.argv) > 1:
        data = " ".join(sys.argv[1:])
    else:
        data = TEST_SUMMARY

    result = interpret_personality(data)

    # Save results to file
    with open("output_file.json", "w") as f:
        json.dump(result, f, indent=2)

    return result

if __name__ == "__main__":
    main()
```

**Patterns:**
- Emoji-prefixed output for visual scanning (`🔮`, `✅`, `❌`, `📝`, `🤔`, `✨`)
- Verbose parameter controls output detail
- Environment variable validation before execution
- Test data as constants (`TEST_SUMMARY`)
- JSON serialization for result inspection
- Exit codes for error detection (`sys.exit(1)`)

## Error Testing

**Frontend Pattern** (from `ErrorBoundary.tsx`):
```typescript
// Component renders fallback UI on error
if (this.state.hasError) {
  return (
    <div className="...">
      <h2>Something went wrong</h2>
      <p>{errorMessage}</p>
      {isDevelopment && <details>Technical details...</details>}
      <button onClick={this.handleReset}>Try Again</button>
    </div>
  );
}
```

**Error Serialization Helper:**
```typescript
const serializeError = (error: unknown): string => {
  if (error instanceof Error) {
    return error.message;
  }
  if (typeof error === 'string') {
    return error;
  }
  try {
    return JSON.stringify(error, null, 2);
  } catch {
    return 'An unknown error occurred';
  }
};
```

**Async Error Handling** (from `SpiritAnimalCard.tsx`):
```typescript
const handleDownload = async () => {
  setIsDownloading(true);
  try {
    const response = await fetch(result.image_url);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const blob = await response.blob();
    // Process blob...
    showNotification('success', 'Download started!');
  } catch (err) {
    console.error('Download failed:', err);
    showNotification('error', 'Failed to download image. Please try again.');
  } finally {
    setIsDownloading(false);
  }
};
```

## Type Validation

**TypeScript Compile-Time Checking:**
- Strict mode enforced via `tsconfig.json`
- All component props have interface definitions
- Function parameters and returns must be typed
- `tsc -b` command validates entire codebase before build

**Runtime Schema Validation** (Backend):
```python
from pydantic import BaseModel

class SpiritRequest(BaseModel):
    name: str
    interests: str = ""
    values: str = ""
    socialHandles: list[SocialHandle] = []
    image_provider: str = "gemini"
```

**Zod Schema Validation** (Frontend):
```typescript
import { z } from "zod";

const spiritRequestV2Schema = z.object({
  personality_summary: z.string(),
  image_provider: z.enum(["openai", "gemini"]).optional(),
  skip_image: z.boolean().optional(),
});
```

## Integration Testing

**Manual API Testing:**
- Backend test scripts call production code directly
- `test_interpretation.py` invokes `interpret_personality()` with sample data
- Results saved to `test_interpretation_result.json` for inspection

**Frontend-Backend Integration:**
- Manual testing through browser at `http://localhost:5173`
- Two modes available: chat (Tambo) and form-based
- Toggle between modes to verify both flows work

**Environment Validation:**
- Startup checks in `main.py` verify API keys are configured
- Print statements indicate which optional APIs are available:
  ```python
  if not os.getenv("OPENAI_API_KEY"):
      print("⚠️  Warning: OPENAI_API_KEY not set...")
  else:
      print("✅ OpenAI API key configured")
  ```

## Mocking

**No Mocking Framework Detected** - No Jest/Vitest mocks configured

**Alternative Approach - Environment Variables:**
- API endpoints changed via `VITE_API_URL` for pointing to test servers
- Image providers can be disabled: `skip_image: true` in requests
- Conversation data can be injected directly for API testing

**Frontend Manual Stubs:**
- LoadingState component for testing loading UI
- Hardcoded test data in components for visual testing

## Coverage

**No Coverage Reporting** - Not configured or enforced

**Type Coverage via TypeScript:**
- TypeScript compiler ensures type safety
- `@typescript-eslint/no-explicit-any` warns against untyped values
- Interface enforcement on all props and function signatures

## Test Data & Fixtures

**Backend Test Data** (`test_interpretation.py`):
```python
TEST_SUMMARY = """I'm a mix of introspective and social. I enjoy quiet time with a good book or a game of chess, but I also value being around people I care about and genuinely enjoy getting to know others. My sense of humor is understated—more dry observations and well-timed comments than big performances. I appreciate simple things done well, like a good meal or an easy weekend with family, and I tend to bring a calm, thoughtful presence into the spaces I'm part of."""
```

**Test Script Flexibility:**
```bash
# Use default test data
python test_interpretation.py

# Pass custom input as argument
python test_interpretation.py "Your custom summary here..."
```

**Output Inspection:**
- Test results saved to JSON files: `test_interpretation_result.json`, `test_image_gemini_*.json`
- Can be inspected manually or in other tooling

## Frontend Error Boundary

**Location:** `src/components/ErrorBoundary.tsx`

**How to Test:**
1. ErrorBoundary is wrapped around entire app in `src/main.tsx`
2. Manually trigger error in component (e.g., accessing undefined property)
3. Fallback UI appears with error message and "Try Again" button
4. Dev mode shows technical details in collapsible details element

**Limitations:**
- Only catches React lifecycle errors
- Does not catch async errors (use try/catch in handlers)
- Does not catch event listener errors (need component-level try/catch)

## TypeScript Type Safety

**Compile-Time Validation:**
```bash
npm run build       # Runs `tsc -b` before bundling
```

**Strict Mode Rules:**
- Null checks required: `value !== null`
- Type guards required: `error instanceof Error`
- No implicit `any` types

**Example Type Flow** (App.tsx):
```typescript
type AppState = "form" | "loading" | "result";
type AppMode = "form" | "chat";

const [mode, setMode] = useState<AppMode>("chat");
const [appState, setAppState] = useState<AppState>("form");
const [result, setResult] = useState<SpiritResult | null>(null);
```

## Async Testing Pattern

**Frontend Async Flow:**
```typescript
const handleSubmit = async (profile: UserProfile) => {
  setUserName(profile.name);
  setAppState("loading");
  setError(null);

  try {
    const response = await fetch(`${API_BASE}/api/spirit-animal`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(profile),
    });

    if (!response.ok) {
      throw new Error("Failed to generate spirit animal");
    }

    const data: SpiritResult = await response.json();
    setResult(data);
    setAppState("result");
  } catch (err) {
    console.error("Error:", err);
    setError(err instanceof Error ? err.message : "Something went wrong");
    setAppState("form");
  }
};
```

## Manual Test Workflow

**Recommended Testing Approach:**

1. **Type Validation:** `npm run build` (catches TypeScript errors)
2. **Linting:** `npm run lint` (checks code style)
3. **Development Testing:** `npm run dev` (start server, test manually in browser)
4. **Backend Script Testing:**
   ```bash
   cd spirit-animal-backend
   python test_interpretation.py         # Verify interpretation logic
   python test_image_generation.py       # Verify image generation
   ```
5. **Visual/Integration:** Open `http://localhost:5173` in browser, test both chat and form modes
6. **Cross-Origin:** Verify CORS headers work correctly (check browser console)

## Debugging

**Frontend:**
- Browser DevTools console for `console.log()` and `console.error()` output
- React DevTools browser extension for component inspection
- Network tab to verify API calls and responses
- ErrorBoundary fallback UI indicates runtime errors

**Backend:**
- Print statements in test scripts with emoji prefixes for scanning
- JSON output files for detailed inspection
- FastAPI docs at `http://localhost:8000/docs` (Swagger UI)
- Console output from `python -u main.py` for real-time logging

**Tambo Integration:**
- DebugPanel component in chat view (visible in development)
- Conversation state logging in tambo.ts with `console.log()` prefixes
- Renders actual API requests/responses for inspection

---

*Testing analysis: 2026-01-21*
