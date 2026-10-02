import { useEffect, useState } from "react";
import { Sparkles } from "lucide-react";
import ErrorMessage from "../components/ErrorMessage";
import LoadingSpinner from "../components/LoadingSpinner";
import MovieGrid from "../components/MovieGrid";
import { getRecommendations } from "../services/aiService";

export default function Recommendations() {
  const [items, setItems] = useState([]);
  const [fallback, setFallback] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  async function loadRecommendations() {
    setLoading(true);
    setError(null);
    try {
      const data = await getRecommendations();
      setItems(data.recommendations || []);
      setFallback(Boolean(data.fallback));
    } catch (requestError) {
      setError(requestError);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadRecommendations(); }, []);

  return (
    <div className="page">
      <header className="page-heading"><div><p className="eyebrow"><Sparkles size={14} /> PERSONALIZED DISCOVERY</p><h1>AI picks</h1></div><button className="button button-quiet" type="button" onClick={loadRecommendations} disabled={loading}>Refresh picks</button></header>
      <p className="page-intro">Films are matched against your ratings and collection. Suggested titles are checked against TMDB before they appear here.</p>
      {fallback && <p className="inline-note" role="status">Showing popular picks based on your highly rated genres.</p>}
      <ErrorMessage error={error} onRetry={loadRecommendations} />
      {loading ? <LoadingSpinner label="Finding your next film" /> : (
        <MovieGrid
          movies={items}
          emptyTitle="More ratings make better picks"
          emptyMessage="Rate a few films and come back for tailored recommendations."
          renderAction={(movie) => movie.reason && <p className="recommendation-reason">{movie.reason}</p>}
        />
      )}
    </div>
  );
}