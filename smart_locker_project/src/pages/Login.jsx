import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { useLanguage } from "../contexts/LanguageContext";
import { Eye, EyeOff, Lock, User, Globe, ChevronDown } from "lucide-react";

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const [isLanguageOpen, setIsLanguageOpen] = useState(false);

  const { login } = useAuth();
  const { t, currentLanguage, changeLanguage, availableLanguages } =
    useLanguage();
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
    setError("");
    setLoading(true);

    if (!username || !password) {
      setError("Please fill in all fields");
      setLoading(false);
      return;
    }

    const result = await login(username, password);

    if (result.success) {
      navigate("/");
    } else {
      setError(result.error);
    }

    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-secondary-50 py-12 px-4 sm:px-6 lg:px-8">
      {/* Language Selector */}
      <div className="absolute top-4 right-4">
        <div className="relative">
          <button
            onClick={() => setIsLanguageOpen(!isLanguageOpen)}
            className="flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-primary-600 transition-colors bg-white shadow-sm"
          >
            <Globe className="h-4 w-4" />
            <span>{languageFlags[currentLanguage]}</span>
            <ChevronDown className="h-4 w-4" />
          </button>

          {isLanguageOpen && (
            <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg border border-gray-200 py-1 z-50">
              {availableLanguages.map((lang) => (
                <button
                  key={lang}
                  onClick={() => {
                    changeLanguage(lang);
                    setIsLanguageOpen(false);
                  }}
                  className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-50 flex items-center space-x-2 ${
                    currentLanguage === lang
                      ? "bg-primary-50 text-primary-700"
                      : "text-gray-700"
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

      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <img
            src="/static/images/ETS-logo.png"
            alt="ETS Logo"
            className="mx-auto h-16 w-auto mb-6"
          />
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            {t("login")}
          </h2>
          <p className="text-gray-600">
            Sign in to access the Smart Locker System
          </p>
        </div>

        <div className="card">
          <form className="space-y-6" onSubmit={handleSubmit}>
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                {error}
              </div>
            )}

            <div>
              <label
                htmlFor="username"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
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
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="input-field pl-10"
                  placeholder="Enter your username"
                />
              </div>
            </div>

            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
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
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="input-field pl-10 pr-10"
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5 text-gray-400" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full flex justify-center items-center"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              ) : (
                t("login_button")
              )}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              Demo credentials: admin/admin123 or employee/employee123
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
