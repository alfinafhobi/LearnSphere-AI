import React, { createContext, useContext, useState, useEffect } from "react";
import { api } from "../api/client";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem("learnsphere_token") || null);
  const [loading, setLoading] = useState(true);
  const [selectedSubject, setSelectedSubject] = useState(() => {
    const saved = localStorage.getItem("learnsphere_active_subject");
    return saved ? JSON.parse(saved) : { id: 1, name: "Java Programming", code: "CS-JAVA" };
  });

  const selectSubject = (subj) => {
    setSelectedSubject(subj);
    localStorage.setItem("learnsphere_active_subject", JSON.stringify(subj));
  };

  useEffect(() => {
    const verifyUser = async () => {
      if (token) {
        try {
          const userData = await api.auth.getMe();
          setUser(userData);
        } catch (err) {
          console.error("Token verification failed:", err);
          logout();
        }
      }
      setLoading(false);
    };
    verifyUser();
  }, [token]);

  const login = async (credentials) => {
    const data = await api.auth.login(credentials);
    localStorage.setItem("learnsphere_token", data.access_token);
    setToken(data.access_token);
    setUser(data.user);
    return data;
  };

  const register = async (userData) => {
    const data = await api.auth.register(userData);
    localStorage.setItem("learnsphere_token", data.access_token);
    setToken(data.access_token);
    setUser(data.user);
    return data;
  };

  const demoLogin = async () => {
    const data = await api.auth.demoLogin();
    localStorage.setItem("learnsphere_token", data.access_token);
    setToken(data.access_token);
    setUser(data.user);
    return data;
  };

  const logout = () => {
    localStorage.removeItem("learnsphere_token");
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        login,
        register,
        demoLogin,
        logout,
        selectedSubject,
        selectSubject,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
