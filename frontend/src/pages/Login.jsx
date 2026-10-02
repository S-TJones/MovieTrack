import { useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { Clapperboard } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import ErrorMessage from "../components/ErrorMessage";

export default function Login() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  if (user) return <Navigate to="/" replace />;

  async function handleSubmit(event) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login(email, password);
      navigate(location.state?.from?.pathname || "/home", { replace: true });
    } catch (requestError) {
      setError(requestError);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-panel" aria-labelledby="login-title">
        <Link className="brand auth-brand" to="/">
          <span className="brand-mark"><Clapperboard size={19} /></span>
          <span>Movie<span className="brand-light">Track</span></span>
        </Link>
        <p className="eyebrow">YOUR PERSONAL FILM ARCHIVE</p>
        <h1 id="login-title">Welcome back.</h1>
        <p className="auth-copy">Pick up where your watchlist left off.</p>
        {location.state?.notice && <p className="success-note" role="status">{location.state.notice}</p>}
        <form className="stack-form" onSubmit={handleSubmit}>
          <label htmlFor="login-email">Email address</label>
          <input id="login-email" name="email" type="email" autoComplete="email" required value={email} onChange={(event) => setEmail(event.target.value)} />
          <label htmlFor="login-password">Password</label>
          <input id="login-password" name="password" type="password" autoComplete="current-password" required value={password} onChange={(event) => setPassword(event.target.value)} />
          <ErrorMessage error={error} />
          <button className="button button-accent button-wide" type="submit" disabled={submitting}>
            {submitting ? "Signing in…" : "Sign in"}
          </button>
        </form>
        <p className="auth-switch">New to MovieTrack? <Link to="/register">Create an account</Link></p>
      </section>
      <aside className="auth-aside" aria-hidden="true">
        <span className="film-index">MT / 001</span>
        <div className="auth-aside-copy"><span>COLLECT WHAT MOVES YOU</span><strong>A better home<br />for your film life.</strong></div>
      </aside>
    </main>
  );
}