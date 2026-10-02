import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import AppLayout from "./components/AppLayout";
import LoadingSpinner from "./components/LoadingSpinner";
import ProtectedRoute from "./components/ProtectedRoute";
import AuditHistory from "./pages/AuditHistory";
import Collection from "./pages/Collection";
import Home from "./pages/Home";
import Login from "./pages/Login";
import MovieDetails from "./pages/MovieDetails";
import Recommendations from "./pages/Recommendations";
import Register from "./pages/Register";
import Search from "./pages/Search";
import "./App.css";

function IndexRedirect() {
  const { user, loading } = useAuth();
  if (loading) return <LoadingSpinner label="Preparing your library" />;
  return <Navigate to={user ? "/home" : "/login"} replace />;
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<IndexRedirect />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route element={<ProtectedRoute />}>
            <Route element={<AppLayout />}>
              <Route path="/home" element={<Home />} />
              <Route path="/search" element={<Search />} />
              <Route path="/movies/:id" element={<MovieDetails />} />
              <Route path="/collection" element={<Collection />} />
              <Route path="/recommendations" element={<Recommendations />} />
              <Route path="/audit" element={<AuditHistory />} />
            </Route>
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
