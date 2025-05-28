import React, { createContext, useContext, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

interface AuthContextType {
  username: string | null;
  token: string | null;
  login: (username: string, token: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [username, setUsername] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const storedToken = sessionStorage.getItem("accessToken");
    const storedUsername = sessionStorage.getItem("username");

    if (storedToken && storedUsername) {
      setUsername(storedUsername);
      setToken(storedToken);
    }
  }, []);

  const login = (username: string, token: string) => {
    sessionStorage.setItem("accessToken", token);
    sessionStorage.setItem("username", username);
    setUsername(username);
    setToken(token);
    navigate("/dashboard");
  };

  const logout = () => {
    sessionStorage.removeItem("accessToken");
    sessionStorage.removeItem("username");
    setUsername(null);
    setToken(null);
    navigate("/login");
  };

  return (
    <AuthContext.Provider value={{ username, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
