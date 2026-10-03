**Architecture Decision Record (ADR)**


1.

\# Architecture Decision Record: Server-Side Audit Logging for Analytics

\*\*Status:\*\* Approved



\*\*Context:\*\* 

The application requires a robust product analytics framework to capture principal user journeys (e.g., AI searches, collections updates, ratings). We had to choose between embedding a client-side tracking pixel (like Mixpanel or Google Analytics) or building a custom server-side audit log data pipeline utilizing our primary database.



\*\*Decision:\*\* 

We chose to implement a custom \*\*Server-Side Audit Event Catalogue\*\* handled via Flask middleware/SQLAlchemy, exposing the statistics through endpoints like `/api/analytics/activity`.



\*\*Consequences:\*\*

\* \*\*Pros:\*\* Bypasses client-side browser ad-blockers entirely, ensuring 100% data integrity for KPIs like `total\_events`. It keeps user data private by storing audit trails locally rather than sending them to third-party data brokers.

\* \*\*Cons:\*\* Increases server load and database storage size, as every transaction (e.g., `AI\_SEARCH\_REQUESTED`, `RATING\_CREATED`) commits a row to an audit table.



2\.

\# Architecture Decision Record: Graceful Degradation Strategy for Optional AI Components

\*\*Status:\*\* Approved



\*\*Context:\*\* 

The application implements AI-assisted search (`/api/ai/search`) and recommendations (`/api/ai/recommendations`). However, Large Language Model (LLM) providers introduce risks regarding runtime network timeouts, API key exhaustion, or complete outages. We needed to decide whether the system should fail hard or degrade gracefully when the LLM is unresponsive.



\*\*Decision:\*\* 

We chose to implement a \*\*Graceful Degradation Architecture with Deterministic Fallbacks\*\*. If `LLM\_API\_KEY` is missing or the endpoint throws an `AIProviderError`, the routing layer transparently falls back to native keyword matching via the TMDB discovery search API.



\*\*Consequences:\*\*

\* \*\*Pros:\*\* Highly resilient; the core application remains fully functional for the user even during third-party AI outages. Minimizes API runtime dependency risks during live evaluation or demos.

\* \*\*Cons:\*\* When degrading gracefully, the contextual "mood" or semantic understanding of queries is temporarily lost, presenting a less personalized experience until the AI service resolves.





3\.
# Architecture Decision Record: Database Abstraction using SQLAlchemy ORM

\*\*Status:\*\* Approved



\*\*Context:\*\* 

The platform must execute transaction operations across movie collections, access credentials, and audit footprints. Writing raw SQL queries directly in backend routes increases code duplication and leaves the application vulnerable to SQL injection attacks if not sanitized meticulously.



\*\*Decision:\*\* 

We chose to utilize \*\*SQLAlchemy ORM\*\* coupled with Flask-Migrate to abstract database interactions into clean Python data models.



\*\*Consequences:\*\*

\* \*\*Pros:\*\* Eradicates broad SQL injection threat surfaces via programmatic query parameterization. Simplifies state synchronization and automates table migration structures (`db upgrade`) across local and production hosting platforms.

\* \*\*Cons:\*\* Adds a minor abstraction layer overhead which could slightly impact optimization speeds if performing massive database actions, though negligible for single-user scale.



