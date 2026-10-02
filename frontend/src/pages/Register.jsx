import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { Clapperboard } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { register } from "../services/authService";
import ErrorMessage from "../components/ErrorMessage";

export default function Register() {
  const { user } = useAuth();
  const navigate = useNavigate();
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
      await register(email, password);
      navigate("/login", { replace: true, state: { notice: "Account created. Sign in to continue." } });
    } catch (requestError) {
      setError(requestError);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-panel" aria-labelledby="register-title">
        <Link className="brand auth-brand" to="/">
          <span className="brand-mark"><Clapperboard size={19} /></span>
          <span>Movie<span className="brand-light">Track</span></span>
        </Link>
        <p className="eyebrow">START YOUR COLLECTION</p>
        <h1 id="register-title">Make it yours.</h1>
        <p className="auth-copy">One account for everything you watch, rate, and recommend.</p>
        <form className="stack-form" onSubmit={handleSubmit}>
          <label htmlFor="register-email">Email address</label>
          <input id="register-email" name="email" type="email" autoComplete="email" required value={email} onChange={(event) => setEmail(event.target.value)} />
          <label htmlFor="register-password">Password</label>
          <input id="register-password" name="password" type="password" autoComplete="new-password" minLength={8} required value={password} onChange={(event) => setPassword(event.target.value)} />
          <span className="field-hint">Use at least 8 characters.</span>
          <ErrorMessage error={error} />
          <button className="button button-accent button-wide" type="submit" disabled={submitting}>
            {submitting ? "Creating account…" : "Create account"}
          </button>
        </form>
        <p className="auth-switch">Already have an account? <Link to="/login">Sign in</Link></p>
      </section>
      <aside className="auth-aside" aria-hidden="true">
        <span className="film-index">MT / 002</span>
        <div className="auth-aside-copy"><span>KEEP THE CREDITS ROLLING</span><strong>Your taste.<br />All in one place.</strong></div>
      </aside>
    </main>
  );
}