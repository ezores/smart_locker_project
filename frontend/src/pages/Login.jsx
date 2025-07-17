import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { useLanguage } from "../contexts/LanguageContext";
import { useDarkMode } from "../contexts/DarkModeContext";
import {
  Eye,
  EyeOff,
  Lock,
  User,
  Globe,
  ChevronDown,
  CreditCard,
  Zap,
} from "lucide-react";

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [rfidTag, setRfidTag] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [rfidLoading, setRfidLoading] = useState(false);
  const [simulateLoading, setSimulateLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [rerender, setRerender] = useState(0);
  const [loginMode, setLoginMode] = useState("password"); // "password" or "rfid"

  const [isLanguageOpen, setIsLanguageOpen] = useState(false);

  const { login, loginWithRFID, simulateRFIDLogin } = useAuth();
  const { t, currentLanguage, changeLanguage, availableLanguages } =
    useLanguage();
  const { isDarkMode } = useDarkMode();
  const navigate = useNavigate();

  const languageFlags = {
    en: "🇺🇸",
    fr: "🇫🇷",
    es: "🇪🇸",
    tr: "🇹🇷",
  };

  const languageNames = {
    en: "English",
    fr: "Français",
    es: "Español",
    tr: "Türkçe",
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
          (result.error.toLowerCase().includes("network") ||
            result.error.toLowerCase().includes("fetch"))
        ) {
          errorMessage = t("network_error");
        } else if (
          result.error &&
          result.error.toLowerCase().includes("server")
        ) {
          errorMessage = t("server_error");
        } else if (!result.error) {
          errorMessage = t("login_failed");
        }
        setError(errorMessage);
      }
      setLoading(false);
    } else if (loginMode === "rfid") {
      if (!rfidTag.trim()) {
        setError("Please scan your RFID card or enter RFID tag");
        setRfidLoading(false);
        setResult({ success: false, error: "RFID tag required" });
        setRerender((r) => r + 1);
        return;
      }
      setError("");
      setRfidLoading(true);
      const result = await loginWithRFID(rfidTag.trim());
      setResult(result);
      if (result.success) {
        navigate("/");
      } else {
        setError(result.error || "RFID login failed");
      }
      setRfidLoading(false);
    }
  };

  const handleSimulateRFID = async () => {
    setError("");
    setSimulateLoading(true);
    const result = await simulateRFIDLogin();
    setResult(result);
    if (result.success) {
      navigate("/");
    } else {
      setError(result.error || "RFID simulation failed");
    }
    setSimulateLoading(false);
  };

  return (
    <div className="min-h-screen transition-colors duration-200 bg-gray-900 text-white">
      <main className="pt-8 pb-8">
        {/* Language Selector - Fixed positioning */}
        <div className="fixed top-4 right-4 z-50">
          <div className="relative">
            <button
              onClick={() => setIsLanguageOpen(!isLanguageOpen)}
              className="flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors shadow-sm text-gray-300 hover:text-white bg-gray-800 hover:bg-gray-700 border border-gray-600"
              aria-label={`Current language: ${languageNames[currentLanguage]}`}
            >
              <Globe className="h-4 w-4" />
              <span>{languageFlags[currentLanguage]}</span>
              <ChevronDown
                className={`h-4 w-4 transition-transform ${
                  isLanguageOpen ? "rotate-180" : ""
                }`}
              />
            </button>

            {isLanguageOpen && (
              <div className="absolute right-0 mt-2 w-48 rounded-md shadow-lg border py-1 z-50 bg-gray-800 border-gray-600">
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
                    aria-label={`Switch to ${languageNames[lang]}`}
                  >
                    <span>{languageFlags[lang]}</span>
                    <span>{languageNames[lang]}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
          <div className="max-w-md w-full space-y-8">
            <div className="text-center">
              <img
                src="/ETS-logo.png"
                alt="ETS Logo"
                className="mx-auto h-16 w-auto mb-6"
              />
              <h2 className="text-3xl font-bold mb-2 text-white">
                {t("login")}
              </h2>
              <p className="text-gray-300">{t("login_description")}</p>
            </div>

            <div className="card">
              {/* Login Mode Toggle */}
              <div className="flex rounded-lg bg-gray-800 p-1 mb-6">
                <button
                  type="button"
                  onClick={() => setLoginMode("password")}
                  className={`flex-1 flex items-center justify-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                    loginMode === "password"
                      ? "bg-primary-600 text-white"
                      : "text-gray-400 hover:text-white"
                  }`}
                >
                  <Lock className="h-4 w-4 mr-2" />
                  Username/Password
                </button>
                <button
                  type="button"
                  onClick={() => setLoginMode("rfid")}
                  className={`flex-1 flex items-center justify-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                    loginMode === "rfid"
                      ? "bg-primary-600 text-white"
                      : "text-gray-400 hover:text-white"
                  }`}
                >
                  <CreditCard className="h-4 w-4 mr-2" />
                  RFID Card
                </button>
              </div>

              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Error message */}
                <div data-testid="login-error-message">
                  {error && (
                    <div className="bg-red-900/50 border border-red-500 text-red-200 px-4 py-3 rounded-md text-sm">
                      {error}
                    </div>
                  )}
                </div>

                {loginMode === "password" ? (
                  <>
                    <div>
                      <label
                        htmlFor="username"
                        className="block text-sm font-medium mb-2 text-white"
                      >
                        {t("username")}
                      </label>
                      <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none z-20">
                          <User className="h-5 w-5 text-gray-400" />
                        </div>
                        <input
                          id="username"
                          name="username"
                          type="text"
                          required
                          value={username}
                          onChange={(e) => setUsername(e.target.value)}
                          className="appearance-none relative block w-full px-3 py-2 border rounded-md placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm pl-10 bg-gray-700 border-gray-600 text-white"
                          placeholder={t("enter_username")}
                          aria-describedby="username-icon"
                        />
                      </div>
                    </div>

                    <div>
                      <label
                        htmlFor="password"
                        className="block text-sm font-medium mb-2 text-white"
                      >
                        {t("password")}
                      </label>
                      <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none z-20">
                          <Lock className="h-5 w-5 text-gray-400" />
                        </div>
                        <input
                          id="password"
                          name="password"
                          type={showPassword ? "text" : "password"}
                          required
                          value={password}
                          onChange={(e) => setPassword(e.target.value)}
                          className="appearance-none relative block w-full px-3 py-2 border rounded-md placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm pl-10 pr-10 bg-gray-700 border-gray-600 text-white"
                          placeholder={t("enter_password")}
                          aria-describedby="password-icon password-toggle"
                        />
                        <button
                          type="button"
                          id="password-toggle"
                          className="absolute inset-y-0 right-0 pr-3 flex items-center z-10 hover:text-gray-300 transition-colors"
                          onClick={() => setShowPassword(!showPassword)}
                          aria-label={
                            showPassword ? "Hide password" : "Show password"
                          }
                        >
                          {showPassword ? (
                            <EyeOff className="h-5 w-5 text-gray-400 hover:text-gray-300" />
                          ) : (
                            <Eye className="h-5 w-5 text-gray-400 hover:text-gray-300" />
                          )}
                        </button>
                      </div>
                    </div>

                    <button
                      type="submit"
                      disabled={loading}
                      className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed focus:ring-offset-gray-800"
                    >
                      {loading ? (
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      ) : (
                        t("login_button")
                      )}
                    </button>
                  </>
                ) : (
                  <>
                    <div>
                      <label
                        htmlFor="rfid"
                        className="block text-sm font-medium mb-2 text-white"
                      >
                        RFID Card
                      </label>
                      <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none z-20">
                          <CreditCard className="h-5 w-5 text-gray-400" />
                        </div>
                        <input
                          id="rfid"
                          name="rfid"
                          type="text"
                          required
                          value={rfidTag}
                          onChange={(e) => setRfidTag(e.target.value)}
                          className="appearance-none relative block w-full px-3 py-2 border rounded-md placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm pl-10 bg-gray-700 border-gray-600 text-white"
                          placeholder="Scan your RFID card or enter tag"
                          aria-describedby="rfid-icon"
                        />
                      </div>
                      <p className="mt-2 text-xs text-gray-400">
                        Place your RFID card near the reader or manually enter
                        the tag
                      </p>
                    </div>

                    <button
                      type="submit"
                      disabled={rfidLoading}
                      className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed focus:ring-offset-gray-800"
                    >
                      {rfidLoading ? (
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      ) : (
                        <>
                          <CreditCard className="h-4 w-4 mr-2" />
                          Login with RFID
                        </>
                      )}
                    </button>

                    {/* Simulate RFID Button */}
                    <div className="relative">
                      <div className="absolute inset-0 flex items-center">
                        <div className="w-full border-t border-gray-600" />
                      </div>
                      <div className="relative flex justify-center text-sm">
                        <span className="px-2 bg-gray-800 text-gray-400">
                          Demo
                        </span>
                      </div>
                    </div>

                    <button
                      type="button"
                      onClick={handleSimulateRFID}
                      disabled={simulateLoading}
                      className="group relative w-full flex justify-center py-2 px-4 border border-gray-600 text-sm font-medium rounded-md text-gray-300 bg-gray-800 hover:bg-gray-700 hover:text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 disabled:opacity-50 disabled:cursor-not-allowed focus:ring-offset-gray-800 transition-colors"
                    >
                      {simulateLoading ? (
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-gray-300"></div>
                      ) : (
                        <>
                          <Zap className="h-4 w-4 mr-2" />
                          Simulate RFID Card (Demo Admin)
                        </>
                      )}
                    </button>
                  </>
                )}
              </form>

              <div className="mt-6 text-center space-y-4">
                <p className="text-sm text-gray-400">{t("demo_credentials")}</p>

                <div className="border-t pt-4">
                  <p className="text-sm text-gray-400">
                    {t("dont_have_account")}{" "}
                    <Link
                      to="/register"
                      className="font-medium text-primary-600 hover:text-primary-500"
                    >
                      {t("register")}
                    </Link>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Login;
