import { Outlet } from "react-router-dom";
import Navbar from "./Navbar";

export default function AppLayout() {
  return (
    <div className="app-shell">
      <Navbar />
      <main className="main-content" id="main-content">
        <Outlet />
      </main>
    </div>
  );
}