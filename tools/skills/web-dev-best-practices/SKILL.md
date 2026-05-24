---
name: web-dev-best-practices
description: >
  Apply web development best practices automatically whenever writing or generating code — frontend, backend, or full-stack. Trigger this skill whenever the user asks Claude to write, scaffold, or produce any kind of web code: React components, API routes, database queries, utility functions, server middleware, hooks, services, controllers, or anything in between. Also trigger when the user asks Claude to "clean up", "refactor", or "improve" existing web code. The skill is stack-agnostic and applies universally — React, Vue, Svelte, Express, Django, FastAPI, Rails, Go, you name it. Claude should apply these principles silently, producing better-structured output without narrating what it's doing.
---

# Web Development Best Practices

When generating or modifying web code, apply the following principles throughout. These aren't rules to follow mechanically — they're design intuitions that lead to code that's easy to understand, change, and trust. Apply them as naturally as a skilled developer would, without calling attention to them.

---

## Core principles (apply everywhere)

**One job per unit.** Every function, module, and component should have a single clear responsibility. If you find yourself writing a function that fetches data, transforms it, *and* renders something, split it. The test: can you name this thing in five words without using "and"?

**Names that make comments unnecessary.** Prefer `parseUserProfileFromApiResponse` over `handleData`. A good name is a free documentation win. Avoid abbreviations that require context to decode.

**Consistency over cleverness.** Follow the patterns already established in the codebase (inferred from context). If you're starting fresh, choose conventions that are idiomatic for the stack and apply them uniformly. A codebase where every file feels the same is far easier to work in than one full of individually clever solutions.

**Explain the why, not the what.** If a comment is necessary, use it to explain a non-obvious decision — not to restate what the code already says. `// retry because this API occasionally returns 503 on first call` is gold. `// increment i` is noise.

---

## Frontend

**Small, focused components.** A component that's hard to name is probably doing too much. Extract child components for distinct UI pieces, and extract logic into custom hooks or composables. Aim for presentational components (just render data passed in) to be as pure and simple as possible.

**Keep state as local as possible.** Don't reach for global state the moment two components need to share data — lift state up first, and only pull in a store when lifting becomes impractical. Premature global state makes data flow opaque.

**Performance by default.** Avoid unnecessary re-renders. In React, be precise with dependency arrays in `useEffect`/`useCallback`/`useMemo`. Lazy-load routes and heavy components. Don't block the main thread — offload heavy computation rather than running it inline.

**Semantic HTML is not optional.** Use `<button>` for buttons, `<nav>` for navigation, `<main>` for content. Proper ARIA attributes where native semantics fall short. Keyboard navigability from the start. Retrofitting accessibility is far more expensive than building it in.

**Consistent error and loading states.** Every data-fetching component should handle loading, error, and empty states — not just the happy path. Define these states explicitly rather than leaving them as implicit `undefined`.

---

## Backend

**Layered architecture.** Separate HTTP concerns from business logic from data access:
- **Router / Controller**: parse the request, call the service, send the response. No business logic here.
- **Service**: business rules, orchestration, decisions. No HTTP objects, no raw SQL.
- **Repository / Data layer**: database interaction. No business logic.

This separation makes each layer independently testable and swappable.

**Never trust input.** Validate and sanitize everything that comes from outside the system — request bodies, query params, headers, file uploads. Use a schema validation library (Zod, Joi, Pydantic, Yup, etc.) and validate at the boundary before the data touches any business logic.

**Centralized error handling.** Define a consistent error model early and handle errors in one place — middleware, not scattered try/catch blocks. Be deliberate about which errors are operational (expected, safe to surface) vs. programmer errors (unexpected, should crash or alert). Return consistent HTTP status codes and error shapes.

**Config from the environment.** Secrets, API keys, database URLs, and environment-specific values belong in environment variables, never hardcoded. A `.env.example` in the repo makes onboarding self-documenting.

**Database discipline.** Use migrations, not manual schema changes. Write readable queries. Watch for N+1 query patterns when traversing relational data — batch or join instead of looping. Use transactions where atomicity matters.

---

## Testing

**Test at the right level.** Unit tests for pure, self-contained logic. Integration tests for service interactions and API endpoints. A small set of end-to-end tests for critical user flows. Don't try to unit-test everything — it creates brittle tests that resist refactoring.

**Tests as living documentation.** A well-named test describes intended behavior: `should return 401 when token is expired` tells the next developer what the system is supposed to do. Prefer descriptive test names over terse ones.

---

## Cross-cutting

**Fail loudly and clearly.** Swallowed errors, empty catch blocks, and silent fallbacks make debugging miserable. If something fails, surface it — log it, throw it, or handle it explicitly. Never let errors disappear silently.

**Prefer boring choices for infrastructure.** Reach for the well-understood, well-documented, battle-tested solution before the novel one — especially on the backend and in data storage. Save creativity for product features.

**Structure is for the next person.** Every structural decision — file layout, naming convention, abstraction boundary — should be made with the question: "Will someone unfamiliar with this code understand the intent immediately?" If the answer is no, simplify or document.
