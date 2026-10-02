import { createContext, useContext, useEffect, useState } from "react";
import { getCurrentUser, login as loginRequest, logout as logoutRequest } from "../services/authService";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    const clearSession = () => {
      logoutRequest();
      if (active) setUser(null);
    };
    window.addEventListener("movietrack:unauthorized", clearSession);

    if (!localStorage.getItem("access_token")) {
      setLoading(false);
    } else {
      getCurrentUser()
        .then((currentUser) => active && setUser(currentUser))
        .catch(clearSession)
        .finally(() => active && setLoading(false));
    }

    return () => {
      active = false;
      window.removeEventListener("movietrack:unauthorized", clearSession);
    };
  }, []);

  async function login(email, password) {
    const data = await loginRequest(email, password);
    setUser(data.user);
    return data.user;
  }

  function logout() {
    logoutRequest();
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider.");
  return context;
}