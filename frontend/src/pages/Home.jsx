import { useEffect, useState } from "react";
import { ArrowRight, Bookmark, Search, Sparkles } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import ErrorMessage from "../components/ErrorMessage";
import LoadingSpinner from "../components/LoadingSpinner";
import MovieGrid from "../components/MovieGrid";
import { getCollection } from "../services/collectionService";

export default function Home() {
  const [collection, setCollection] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [query, setQuery] = useState("");
  const navigate = useNavigate();

  async function loadCollection() {
    setLoading(true);
    setError(null);
    try {
      const data = await getCollection();
      setCollection(data.items || []);
    } catch (requestError) {
      setError(requestError);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadCollection(); }, []);

  function submitSearch(event) {
    event.preventDefault();
    if (query.trim()) navigate(`/search?q=${encodeURIComponent(query.trim())}`);
  }

  return (
    <div className="page home-page">
      <header className="page-topline"><span className="eyebrow">MOVIETRACK / YOUR LIBRARY</span><span className="today-mark">A FILM AWAITS</span></header>
      <section className="home-intro">
        <div>
          <p className="eyebrow accent-eyebrow">YOUR NEXT FAVORITE IS OUT THERE</p>
          <h1>Keep good<br /><em>stories close.</em></h1>
          <p className="home-description">Find films, build a collection, and keep a record of what stayed with you.</p>
        </div>
        <div className="intro-index" aria-hidden="true"><span>01</span><span>DISCOVER<br />COLLECT<br />REMEMBER</span></div>
      </section>
      <form className="home-search" onSubmit={submitSearch} role="search">
        <Search size={20} aria-hidden="true" />
        <label className="sr-only" htmlFor="home-search">Find a movie</label>
        <input id="home-search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Find a film, performer, or director" />
        <button className="button button-accent" type="submit" disabled={!query.trim()}>Explore <ArrowRight size={16} /></button>
      </form>
      <div className="quick-links">
        <Link to="/search?mode=ai" className="quick-link"><Sparkles size={17} /><span>Ask for an AI-powered search</span><ArrowRight size={15} /></Link>
        <Link to="/recommendations" className="quick-link"><Bookmark size={17} /><span>See picks shaped by your ratings</span><ArrowRight size={15} /></Link>
      </div>
      <section className="section-block">
        <div className="section-heading">
          <div><p className="eyebrow">YOUR SHELF</p><h2>Recently collected <span>{collection.length.toString().padStart(2, "0")}</span></h2></div>
          <Link className="text-link" to="/collection">View collection <ArrowRight size={15} /></Link>
        </div>
        <ErrorMessage error={error} onRetry={loadCollection} />
        {loading ? <LoadingSpinner label="Loading your shelf" /> : (
          <MovieGrid
            movies={collection.slice(0, 4)}
            emptyTitle="Your shelf is waiting"
            emptyMessage="Search for a film and add it to your collection."
          />
        )}
      </section>
    </div>
  );
}