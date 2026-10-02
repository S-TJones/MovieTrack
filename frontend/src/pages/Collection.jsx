import { useEffect, useState } from "react";
import { Trash2 } from "lucide-react";
import ErrorMessage from "../components/ErrorMessage";
import LoadingSpinner from "../components/LoadingSpinner";
import MovieGrid from "../components/MovieGrid";
import { getCollection, removeFromCollection } from "../services/collectionService";

export default function Collection() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  async function loadCollection() {
    setLoading(true);
    setError(null);
    try {
      const data = await getCollection();
      setItems(data.items || []);
    } catch (requestError) {
      setError(requestError);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadCollection(); }, []);

  async function remove(movieId) {
    try {
      await removeFromCollection(movieId);
      setItems((current) => current.filter((item) => item.movie_id !== movieId));
    } catch (requestError) {
      setError(requestError);
    }
  }

  return (
    <div className="page">
      <header className="page-heading"><div><p className="eyebrow">SAVED FOR LATER</p><h1>My collection</h1></div><span className="count-badge">{items.length} FILMS</span></header>
      <ErrorMessage error={error} onRetry={loadCollection} />
      {loading ? <LoadingSpinner label="Loading your collection" /> : (
        <MovieGrid
          movies={items}
          emptyTitle="Your collection is empty"
          emptyMessage="When a film catches your eye, save it here."
          renderAction={(movie) => (
            <button className="button button-quiet remove-button" type="button" onClick={() => remove(movie.movie_id)} aria-label={`Remove ${movie.title} from collection`}>
              <Trash2 size={15} /> Remove
            </button>
          )}
        />
      )}
    </div>
  );
}