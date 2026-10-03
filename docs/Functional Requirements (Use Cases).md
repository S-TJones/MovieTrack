**Functional Requirements (Use Cases)**


1\. Account \& Profile Management

* Register Account: User creates a profile using email and password.
* Log In / Log Out: User authenticates or terminates their session securely.



2\. Discovery \& Search Journey

* Search Movies by Filter: User searches for movies using specific criteria (Cast, Director, Genre).
* AI-Assisted Search: User inputs natural language prompts to discover contextually relevant movies.
* View AI Recommendations: User receives a personalized feed of recommended movies based on their collection history.



3\. Collection \& Rating Management

* View Movie Details: User selects a movie to view its synopsis, metadata, and third-party ratings (fetched from an external API).
* Add Movie to Collection: User adds a movie to their personal tracking vault.
* Remove Movie from Collection: User deletes an entry from their personal tracker.
* Submit Personal Rating: User submits a score (1–10) and optional review notes.

  * Constraint: The system must strictly restrict this to one rating per movie per user.
* Edit/Update Personal Rating: User modifies their existing rating or review details.



4\. Sharing \& Social

* Generate Public Collection Link: User exports a shareable link of their movie vault.
* View Public Collection: Anonymous Visitor clicks a link to view a user’s collection without logging in.

