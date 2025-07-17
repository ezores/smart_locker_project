import React from "react";
import { createContext, useContext, useState, useEffect } from "react";
import axios from "axios";

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem("token");
    if (token) {
      axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
      checkAuthStatus();
    } else {
      setLoading(false);
    }
  }, []);

  const checkAuthStatus = async () => {
    try {
      const response = await axios.get("/api/user/profile");
      setUser(response.data);
    } catch (error) {
      localStorage.removeItem("token");
      delete axios.defaults.headers.common["Authorization"];
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    try {
      console.log("Attempting login with:", { username, password });
      const response = await axios.post("/api/auth/login", {
        username,
        password,
      });

      console.log("Login response:", response.data);
      const { token, user: userData } = response.data;
      localStorage.setItem("token", token);
      axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
      setUser(userData);
      return { success: true };
    } catch (error) {
      console.error("Login error:", error);
      console.error("Error response:", error.response);

      // Always return a generic error message for security
      // Don't reveal whether username or password is incorrect
      const isAuthError =
        error.response?.status === 401 ||
        error.response?.status === 403 ||
        error.response?.data?.error?.toLowerCase().includes("password") ||
        error.response?.data?.error?.toLowerCase().includes("username") ||
        error.response?.data?.error?.toLowerCase().includes("invalid") ||
        error.response?.data?.error?.toLowerCase().includes("credentials");

      return {
        success: false,
        error: isAuthError
          ? "Invalid credentials"
          : error.message || "Login failed",
        details: null, // Don't expose backend details for security
      };
    }
  };

  const loginWithRFID = async (rfidTag) => {
    try {
      console.log("Attempting RFID login with tag:", rfidTag);
      const response = await axios.post("/api/auth/login", {
        rfid_tag: rfidTag,
      });

      console.log("RFID Login response:", response.data);
      const { token, user: userData } = response.data;
      localStorage.setItem("token", token);
      axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
      setUser(userData);
      return { success: true, loginMethod: response.data.login_method };
    } catch (error) {
      console.error("RFID Login error:", error);
      console.error("Error response:", error.response);

      return {
        success: false,
        error: error.response?.data?.error || "RFID login failed",
        details: error.response?.data?.details || null,
      };
    }
  };

  const simulateRFIDLogin = async () => {
    try {
      console.log("Attempting simulated RFID login");
      const response = await axios.post("/api/auth/simulate-rfid");

      console.log("Simulated RFID Login response:", response.data);
      const { token, user: userData } = response.data;
      localStorage.setItem("token", token);
      axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
      setUser(userData);
      return {
        success: true,
        loginMethod: response.data.login_method,
        message: response.data.message,
      };
    } catch (error) {
      console.error("Simulated RFID Login error:", error);
      console.error("Error response:", error.response);

      return {
        success: false,
        error: error.response?.data?.error || "RFID simulation failed",
        details: error.response?.data?.details || null,
      };
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    delete axios.defaults.headers.common["Authorization"];
    setUser(null);
  };

  const value = {
    user,
    login,
    loginWithRFID,
    simulateRFIDLogin,
    logout,
    loading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
