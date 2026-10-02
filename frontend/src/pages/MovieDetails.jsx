import { useEffect, useState } from "react";
import { ArrowLeft, Bookmark, BookmarkCheck, Users } from "lucide-react";
import { Link, useParams } from "react-router-dom";
import ErrorMessage from "../components/ErrorMessage";
import LoadingSpinner from "../components/LoadingSpinner";
import RatingInput from "../components/RatingInput";
import { addToCollection, getCollection, removeFromCollection } from "../services/collectionService";
import { getMovie } from "../services/movieService";
import { createRating, deleteRating, getRating, updateRating } from "../services/ratingService";

const IMAGE_BASE = "https://image.tmdb.org/t/p/w780";

export default function MovieDetails() {
  const { id } = useParams();
  const [movie, setMovie] = useState(null);
  const [savedRating, setSavedRating] = useState(null);
  const [ratingValue, setRatingValue] = useState(0);
  const [inCollection, setInCollection] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [notice, setNotice] = useState("");

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    Promise.all([getMovie(id), getCollection()])
      .then(async ([movieData, collectionData]) => {
        const ratingData = await getRating(movieData.id);
        if (!active) return;
        setMovie(movieData);
        setSavedRating(ratingData.rating);
        setRatingValue(ratingData.rating ?? 0);
        setInCollection((collectionData.items || []).some((item) => item.movie_id === movieData.id));
      })
      .catch((requestError) => active && setError(requestError))
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, [id]);

  async function toggleCollection() {
    if (!movie) return;
    setSaving(true);
    setError(null);
    try {
      if (inCollection) await removeFromCollection(movie.id);
      else await addToCollection(movie.id);
      setInCollection(!inCollection);
      setNotice(inCollection ? "Removed from your collection." : "Added to your collection.");
    } catch (requestError) {
      setError(requestError);
    } finally {
      setSaving(false);
    }
  }

  async function saveRating(event) {
    event.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const result = savedRating == null
        ? await createRating(movie.id, ratingValue)
        : await updateRating(movie.id, ratingValue);
      setSavedRating(result.rating);
      setNotice("Your rating was saved.");
    } catch (requestError) {
      setError(requestError);
    } finally {
      setSaving(false);
    }
  }

  async function clearRating() {
    setSaving(true);
    setError(null);
    try {
      await deleteRating(movie.id);
      setSavedRating(null);
      setRatingValue(0);
      setNotice("Your rating was removed.");
    } catch (requestError) {
      setError(requestError);
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <div className="page"><LoadingSpinner label="Loading movie details" /></div>;
  if (error && !movie) return <div className="page"><Link className="back-link" to="/search"><ArrowLeft size={16} /> Back to search</Link><ErrorMessage error={error} /></div>;
  if (!movie) return null;

  return (
    <div className="page detail-page">
      <Link className="back-link" to="/search"><ArrowLeft size={16} /> Back to discovery</Link>
      <ErrorMessage error={error} />
      {notice && <p className="success-note" role="status">{notice}</p>}
      <section className="detail-hero">
        <div className="detail-poster-wrap">
          {movie.poster_path ? <img className="detail-poster" src={`${IMAGE_BASE}${movie.poster_path}`} alt={`${movie.title} poster`} /> : <div className="detail-poster poster-placeholder">MT</div>}
        </div>
        <div className="detail-copy">
          <p className="eyebrow">MOVIE / {movie.tmdb_id}</p>
          <h1>{movie.title}</h1>
          <p className="detail-subtitle">{movie.release_date?.slice(0, 4) || "Release year unknown"}{movie.original_title && movie.original_title !== movie.title ? ` · ${movie.original_title}` : ""}</p>
          {movie.tmdb_vote_average != null && <p className="detail-score"><span>TMDB</span><strong>{Number(movie.tmdb_vote_average).toFixed(1)}</strong> / 10</p>}
          <p className="detail-overview">{movie.overview || "No overview is available for this film."}</p>
          {!!movie.genres?.length && <div className="genre-list" aria-label="Genres">{movie.genres.map((genre) => <span key={genre.id}>{genre.name}</span>)}</div>}
          <button className={`button ${inCollection ? "button-muted" : "button-accent"}`} type="button" onClick={toggleCollection} disabled={saving}>
            {inCollection ? <BookmarkCheck size={17} /> : <Bookmark size={17} />}
            {inCollection ? "In your collection" : "Add to collection"}
          </button>
        </div>
      </section>
      <section className="detail-lower">
        <form className="rating-panel" onSubmit={saveRating}>
          <p className="eyebrow">YOUR TAKE</p>
          <h2>{savedRating == null ? "Leave a rating" : `Your rating · ${Number(savedRating).toFixed(1)}`}</h2>
          <RatingInput value={ratingValue} onChange={setRatingValue} disabled={saving} />
          <div className="rating-actions">
            <button className="button button-accent" type="submit" disabled={saving}>{savedRating == null ? "Save rating" : "Update rating"}</button>
            {savedRating != null && <button className="button button-quiet" type="button" onClick={clearRating} disabled={saving}>Remove rating</button>}
          </div>
        </form>
        <section className="credits-panel">
          <p className="eyebrow">THE PEOPLE</p>
          <h2><Users size={18} /> Cast &amp; crew</h2>
          <div className="credit-block"><span>DIRECTOR</span><strong>{movie.directors?.map((person) => person.name).join(", ") || "Not listed"}</strong></div>
          <div className="credit-block"><span>CAST</span><strong>{movie.cast?.slice(0, 8).map((person) => person.name).join(", ") || "Not listed"}</strong></div>
        </section>
      </section>
    </div>
  );
}