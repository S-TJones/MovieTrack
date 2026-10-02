import { useEffect, useState } from "react";
import { Sparkles } from "lucide-react";
import { useSearchParams } from "react-router-dom";
import ErrorMessage from "../components/ErrorMessage";
import LoadingSpinner from "../components/LoadingSpinner";
import MovieGrid from "../components/MovieGrid";
import SearchBar from "../components/SearchBar";
import { searchWithAI } from "../services/aiService";
import { searchMovies } from "../services/movieService";

function describeFilters(filters) {
  if (!filters) return [];
  const chips = [...filters.genres, ...filters.cast.map((name) => `Cast: ${name}`), ...filters.keywords.map((word) => `“${word}”`)];
  if (filters.director) chips.push(`Director: ${filters.director}`);
  if (filters.year_from || filters.year_to) chips.push(`${filters.year_from || "Any year"}–${filters.year_to || "Now"}`);
  return chips;
}

export default function Search() {
  const [searchParams] = useSearchParams();
  const [mode, setMode] = useState(searchParams.get("mode") === "ai" ? "ai" : "normal");
  const [query, setQuery] = useState(searchParams.get("q") || "");
  const [results, setResults] = useState([]);
  const [filters, setFilters] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [error, setError] = useState(null);

  async function submitSearch(event) {
    event?.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    setSearched(true);
    setFilters(null);
    try {
      const data = mode === "ai"
        ? await searchWithAI(query.trim())
        : await searchMovies(query.trim());
      setResults(data.results || []);
      setFilters(data.filters || null);
    } catch (requestError) {
      setError(requestError);
      setResults([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    const initialQuery = searchParams.get("q");
    if (initialQuery) submitSearch();
  }, []);

  return (
    <div className="page">
      <header className="page-heading"><div><p className="eyebrow">THE MOVIE INDEX</p><h1>Discover</h1></div><span className="heading-note">SEARCH / 01</span></header>
      <div className="mode-switch" role="group" aria-label="Search mode">
        <button type="button" className={mode === "normal" ? "selected" : ""} onClick={() => setMode("normal")}>Movie search</button>
        <button type="button" className={mode === "ai" ? "selected" : ""} onClick={() => setMode("ai")}><Sparkles size={15} /> AI search</button>
      </div>
      <SearchBar value={query} onChange={setQuery} onSubmit={submitSearch} placeholder={mode === "ai" ? "Describe the kind of film you want" : "Search titles, cast, or directors"} />
      {mode === "ai" && <p className="inline-note">Describe a mood, genre, cast member, or time period. The results are matched against the movie catalog.</p>}
      {filters && <div className="filter-summary"><span className="eyebrow">AI READ</span>{describeFilters(filters).map((filter) => <span className="filter-chip" key={filter}>{filter}</span>)}</div>}
      <ErrorMessage error={error} />
      <section className="section-block search-results">
        <div className="section-heading"><div><p className="eyebrow">{searched ? (mode === "ai" ? "AI-ASSISTED RESULTS" : "CATALOG RESULTS") : "START WITH A TITLE"}</p><h2>{searched ? `Matches for “${query}”` : "What are you looking for?"}</h2></div></div>
        {loading ? <LoadingSpinner label="Searching the catalog" /> : searched ? (
          <MovieGrid movies={results} emptyTitle="No matching films" emptyMessage="Try a broader title, genre, or date range." />
        ) : <p className="inline-note">Search the movie catalog or switch to AI search for a natural-language query.</p>}
      </section>
    </div>
  );
}