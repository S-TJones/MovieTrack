import { NavLink, useNavigate } from "react-router-dom";
import { Activity, Clapperboard, Compass, Film, LogOut, Search, Sparkles } from "lucide-react";
import { useAuth } from "../context/AuthContext";

const links = [
  { to: "/home", label: "Overview", icon: Compass, end: true },
  { to: "/search", label: "Discover", icon: Search },
  { to: "/collection", label: "My collection", icon: Film },
  { to: "/recommendations", label: "AI picks", icon: Sparkles },
  { to: "/audit", label: "Activity", icon: Activity },
];

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <aside className="sidebar">
      <NavLink className="brand" to="/home" aria-label="MovieTrack home">
        <span className="brand-mark"><Clapperboard size={19} /></span>
        <span>Movie<span className="brand-light">Track</span></span>
      </NavLink>
      <p className="sidebar-label">YOUR SPACE</p>
      <nav className="primary-nav" aria-label="Main navigation">
        {links.map(({ to, label, icon: Icon, end }) => (
          <NavLink key={to} to={to} end={end} className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>
            <Icon size={18} aria-hidden="true" />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>
      <div className="sidebar-bottom">
        <div className="user-block">
          <span className="user-avatar" aria-hidden="true">{user?.email?.[0]?.toUpperCase() || "M"}</span>
          <span className="user-email" title={user?.email}>{user?.email}</span>
        </div>
        <button className="nav-link logout-link" type="button" onClick={handleLogout}>
          <LogOut size={18} aria-hidden="true" />
          <span>Sign out</span>
        </button>
      </div>
    </aside>
  );
}