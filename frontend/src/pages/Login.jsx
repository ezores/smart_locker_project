/**
 * Smart Locker System - Login Component
 *
 * @author Alp
 * @date 2024-12-XX
 * @description Secure login form with RFID simulation and multi-language support
 */

import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { useLanguage } from "../contexts/LanguageContext";
import { useDarkMode } from "../contexts/DarkModeContext";
import {
  User,
  Lock,
  Eye,
  EyeOff,
  CreditCard,
  QrCode,
  AlertCircle,
  Globe,
  ChevronDown,
} from "lucide-react";

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [loginMode, setLoginMode] = useState("password"); // 'password' or 'rfid'
  const [result, setResult] = useState(null);
  const [rerender, setRerender] = useState(0);
  const [isLanguageOpen, setIsLanguageOpen] = useState(false);

  const { login, loginWithRFID, simulateRFIDLogin } = useAuth();
  const { t, currentLanguage, changeLanguage, availableLanguages } =
    useLanguage();
  const { isDarkMode } = useDarkMode();
  const navigate = useNavigate();

  const languageFlags = {
    en: "🇺🇸",
    fr: "🇫🇷",
    tr: "🇹🇷",
    az: "🇦🇿",
    es: "🇪🇸",
    "pt-BR": "🇧🇷",
  };

  const languageNames = {
    en: "English",
    fr: "Français",
    tr: "Türkçe",
    az: "Azərbaycan",
    es: "Español",
    "pt-BR": "Português (BR)",
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (loginMode === "password") {
      if (!username || !password) {
        setError(t("fill_all_fields"));
        setLoading(false);
        setResult({ success: false, error: t("fill_all_fields") }); // Ensure error state is set for tests
        setRerender((r) => r + 1); // force re-render
        return;
      }
      setError("");
      setLoading(true);
      const result = await login(username, password);
      setResult(result);
      if (result.success) {
        navigate("/");
      } else {
        // Improved error handling with better messages
        let errorMessage = result.error;

        // Always use generic message for authentication errors
        if (
          result.error === "Invalid credentials" ||
          result.error.toLowerCase().includes("invalid") ||
          result.error.toLowerCase().includes("credentials")
        ) {
          errorMessage = t("invalid_credentials");
        } else if (
          result.error &&
          result.error.toLowerCase().includes("server")
        ) {
          errorMessage = t("server_error");
        } else if (
          result.error &&
          result.error.toLowerCase().includes("network")
        ) {
          errorMessage = t("network_error");
        } else if (
          result.error &&
          result.error.toLowerCase().includes("locked")
        ) {
          errorMessage = t("account_locked");
        } else if (
          result.error &&
          result.error.toLowerCase().includes("attempts")
        ) {
          errorMessage = t("too_many_attempts");
        } else if (result.error) {
          errorMessage = t("login_failed");
        }

        setError(errorMessage);
      }
      setLoading(false);
    }
  };

  const handleRFIDLogin = async () => {
    setLoading(true);
    setError("");
    const result = await simulateRFIDLogin();
    setResult(result);
    if (result.success) {
      navigate("/");
    } else {
      setError(result.error || t("login_failed"));
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen transition-colors duration-200 bg-gray-900 text-white">
      <main className="pt-8 pb-8">
        {/* Language Selector - Fixed positioning */}
        <div className="fixed top-4 right-4 z-50">
          <div className="relative">
            <button
              onClick={() => setIsLanguageOpen(!isLanguageOpen)}
              className="flex items-center space-x-2 px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg border border-gray-600 transition-colors"
              aria-label="Current language"
            >
              <Globe className="h-4 w-4" />
              <span className="hidden sm:block">
                {languageFlags[currentLanguage]}
              </span>
              <ChevronDown className="h-4 w-4" />
            </button>
            {isLanguageOpen && (
              <div className="absolute right-0 mt-2 w-48 bg-gray-800 border border-gray-600 rounded-lg shadow-lg z-50">
                {availableLanguages.map((lang) => (
                  <button
                    key={lang}
                    onClick={() => {
                      changeLanguage(lang);
                      setIsLanguageOpen(false);
                    }}
                    className={`w-full text-left px-4 py-2 text-sm flex items-center space-x-2 transition-colors ${
                      currentLanguage === lang
                        ? "bg-gray-700 text-white"
                        : "text-gray-300 hover:bg-gray-700 hover:text-white"
                    }`}
                  >
                    <span>{languageFlags[lang]}</span>
                    <span>{languageNames[lang]}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="flex items-center justify-center min-h-screen px-4 sm:px-6 lg:px-8">
          <div className="max-w-md w-full space-y-8">
            <div>
              <div className="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-primary-600">
                <User className="h-6 w-6 text-white" />
              </div>
              <h2 className="mt-6 text-center text-3xl font-extrabold text-white">
                {t("login")}
              </h2>
              <p className="mt-2 text-center text-sm text-gray-400">
                {t("login_description")}
              </p>
            </div>

            {/* Login Mode Toggle */}
            <div className="flex rounded-lg bg-gray-800 p-1">
              <button
                onClick={() => setLoginMode("password")}
                className={`flex-1 flex items-center justify-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  loginMode === "password"
                    ? "bg-primary-600 text-white"
                    : "text-gray-400 hover:text-white"
                }`}
              >
                <Lock className="h-4 w-4 mr-2" />
                {t("password")}
              </button>
              <button
                onClick={() => setLoginMode("rfid")}
                className={`flex-1 flex items-center justify-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  loginMode === "rfid"
                    ? "bg-primary-600 text-white"
                    : "text-gray-400 hover:text-white"
                }`}
              >
                <CreditCard className="h-4 w-4 mr-2" />
                RFID
              </button>
            </div>

            {error && (
              <div className="bg-red-900/50 border border-red-500 text-red-200 px-4 py-3 rounded-lg flex items-center">
                <AlertCircle className="h-5 w-5 mr-2 flex-shrink-0" />
                <span className="text-sm">{error}</span>
              </div>
            )}

            {loginMode === "password" ? (
              <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                <div className="space-y-4">
                  <div>
                    <label htmlFor="username" className="sr-only">
                      {t("username")}
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <User className="h-5 w-5 text-gray-400" />
                      </div>
                      <input
                        id="username"
                        name="username"
                        type="text"
                        autoComplete="username"
                        required
                        className="appearance-none relative block w-full px-3 py-2 pl-10 border border-gray-600 placeholder-gray-400 text-white rounded-lg bg-gray-800 focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm"
                        placeholder={t("enter_username")}
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                      />
                    </div>
                  </div>
                  <div>
                    <label htmlFor="password" className="sr-only">
                      {t("password")}
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <Lock className="h-5 w-5 text-gray-400" />
                      </div>
                      <input
                        id="password"
                        name="password"
                        type={showPassword ? "text" : "password"}
                        autoComplete="current-password"
                        required
                        className="appearance-none relative block w-full px-3 py-2 pl-10 pr-10 border border-gray-600 placeholder-gray-400 text-white rounded-lg bg-gray-800 focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm"
                        placeholder={t("enter_password")}
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                      />
                      <button
                        type="button"
                        className="absolute inset-y-0 right-0 pr-3 flex items-center"
                        onClick={() => setShowPassword(!showPassword)}
                      >
                        {showPassword ? (
                          <EyeOff className="h-5 w-5 text-gray-400 hover:text-gray-300" />
                        ) : (
                          <Eye className="h-5 w-5 text-gray-400 hover:text-gray-300" />
                        )}
                      </button>
                    </div>
                  </div>
                </div>

                <div>
                  <button
                    type="submit"
                    disabled={loading}
                    className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {loading ? (
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    ) : (
                      t("login_button")
                    )}
                  </button>
                </div>
              </form>
            ) : (
              <div className="mt-8 space-y-6">
                <div className="text-center">
                  <div className="bg-gray-800 rounded-lg p-8">
                    <QrCode className="h-16 w-16 text-primary-500 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-white mb-2">
                      RFID {t("login")}
                    </h3>
                    <p className="text-gray-400 text-sm mb-6">
                      {t("scan_rfid_description")}
                    </p>
                    <button
                      onClick={handleRFIDLogin}
                      disabled={loading}
                      className="w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      {loading ? (
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      ) : (
                        t("simulate_rfid_scan")
                      )}
                    </button>
                  </div>
                </div>
              </div>
            )}

            <div className="text-center">
              <p className="text-sm text-gray-400">
                {t("dont_have_account")}{" "}
                <Link
                  to="/register"
                  className="font-medium text-primary-400 hover:text-primary-300 transition-colors"
                >
                  {t("register")}
                </Link>
              </p>
            </div>

            <div className="mt-6 p-4 bg-gray-800 rounded-lg">
              <p className="text-xs text-gray-400 text-center">
                {t("demo_credentials")}
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Login;
