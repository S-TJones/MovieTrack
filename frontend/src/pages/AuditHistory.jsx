import { useEffect, useState } from "react";
import { getAuditHistory } from "../services/auditService";
import ErrorMessage from "../components/ErrorMessage";
import LoadingSpinner from "../components/LoadingSpinner";

const ACTION_LABELS = {
  USER_REGISTERED: "Account created",
  LOGIN_SUCCESS: "Signed in",
  LOGIN_FAILED: "Sign-in attempt failed",
  MOVIE_SEARCHED: "Movie search",
  MOVIE_VIEWED: "Movie viewed",
  MOVIE_ADDED_TO_COLLECTION: "Added to collection",
  MOVIE_REMOVED_FROM_COLLECTION: "Removed from collection",
  RATING_CREATED: "Rating created",
  RATING_UPDATED: "Rating updated",
  RATING_DELETED: "Rating removed",
  AI_SEARCH_REQUESTED: "AI movie search",
  AI_RECOMMENDATION_REQUESTED: "AI recommendations requested",
};

export default function AuditHistory() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  async function loadEvents() {
    setLoading(true);
    setError(null);
    try {
      const data = await getAuditHistory(100);
      setEvents(data.items || []);
    } catch (requestError) {
      setError(requestError);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadEvents(); }, []);

  return (
    <div className="page">
      <header className="page-heading"><div><p className="eyebrow">APPEND-ONLY RECORD</p><h1>Activity</h1></div><button className="button button-quiet" type="button" onClick={loadEvents} disabled={loading}>Refresh</button></header>
      <p className="page-intro">Your recent account, collection, rating, and discovery activity.</p>
      <ErrorMessage error={error} onRetry={loadEvents} />
      {loading ? <LoadingSpinner label="Loading activity" /> : events.length ? (
        <div className="activity-table-wrap">
          <table className="activity-table">
            <thead><tr><th scope="col">Activity</th><th scope="col">Resource</th><th scope="col">Time</th><th scope="col">Request ID</th></tr></thead>
            <tbody>{events.map((event) => (
              <tr key={event.id}>
                <td><span className="activity-dot" aria-hidden="true" /><strong>{ACTION_LABELS[event.action] || event.action.replaceAll("_", " ").toLowerCase()}</strong></td>
                <td>{event.resource_type}{event.resource_id ? ` · ${event.resource_id}` : ""}</td>
                <td><time dateTime={event.created_at}>{new Date(event.created_at).toLocaleString()}</time></td>
                <td><code title={event.correlation_id}>{event.correlation_id.slice(0, 12)}</code></td>
              </tr>
            ))}</tbody>
          </table>
        </div>
      ) : <div className="empty-state"><h3>No activity yet</h3><p>Your actions will appear here as you use MovieTrack.</p></div>}
    </div>
  );
}