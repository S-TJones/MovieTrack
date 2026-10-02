import { Search } from "lucide-react";

export default function SearchBar({ value, onChange, onSubmit, placeholder = "Search films, cast, or directors" }) {
  return (
    <form className="search-bar" onSubmit={onSubmit} role="search">
      <Search size={19} aria-hidden="true" />
      <label className="sr-only" htmlFor="movie-search">Search movies</label>
      <input
        id="movie-search"
        name="query"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        autoComplete="off"
      />
      <button className="button button-accent" type="submit" disabled={!value.trim()}>
        Search
      </button>
    </form>
  );
}