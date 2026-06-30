import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('auth_token'));
  const [loading, setLoading] = useState(true);

  // On mount, verify token and load user profile
  useEffect(() => {
    const loadUser = async () => {
      if (!token) {
        setLoading(false);
        return;
      }
      try {
        const response = await authAPI.getProfile();
        setUser(response.data.data);
      } catch {
        // Token invalid — clear
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
        setToken(null);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };
    loadUser();
  }, [token]);

  const login = async (email, password) => {
    const response = await authAPI.login({ email, password });
    const newToken = response.data.access_token;
    localStorage.setItem('auth_token', newToken);
    setToken(newToken);

    // Fetch profile
    const profile = await authAPI.getProfile();
    setUser(profile.data.data);
    localStorage.setItem('user', JSON.stringify(profile.data.data));
    return profile.data.data;
  };

  const register = async (name, email, password) => {
    const response = await authAPI.register({ name, email, password });
    const newToken = response.data.access_token;
    localStorage.setItem('auth_token', newToken);
    setToken(newToken);

    // Fetch profile
    const profile = await authAPI.getProfile();
    setUser(profile.data.data);
    localStorage.setItem('user', JSON.stringify(profile.data.data));
    return profile.data.data;
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}

export default AuthContext;
