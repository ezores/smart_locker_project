import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { useLanguage } from "../contexts/LanguageContext";
import { Menu, X, User, LogOut, Globe, ChevronDown } from "lucide-react";

const Header = () => {
  const { user, logout } = useAuth();
  const { t, currentLanguage, changeLanguage, availableLanguages } =
    useLanguage();
  const navigate = useNavigate();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isLanguageOpen, setIsLanguageOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

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

  if (!user) return null;

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and Brand */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-3">
              <img
                src="/static/images/ETS-logo.png"
                alt="ETS Logo"
                className="h-10 w-auto"
              />
              <div className="hidden sm:block">
                <h1 className="text-xl font-bold text-gray-900">LACIME</h1>
                <p className="text-sm text-gray-600">Smart Locker System</p>
              </div>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <Link
              to="/"
              className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              {t("main_menu")}
            </Link>
            <Link
              to="/borrow"
              className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              {t("borrow")}
            </Link>
            <Link
              to="/return"
              className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              {t("return")}
            </Link>
            {user.role === "admin" && (
              <Link
                to="/admin"
                className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              >
                {t("admin")}
              </Link>
            )}
          </nav>

          {/* Right side - Language and User */}
          <div className="flex items-center space-x-4">
            {/* Language Selector */}
            <div className="relative">
              <button
                onClick={() => setIsLanguageOpen(!isLanguageOpen)}
                className="flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-primary-600 transition-colors"
              >
                <Globe className="h-4 w-4" />
                <span className="hidden sm:block">
                  {languageFlags[currentLanguage]}
                </span>
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

            {/* User Menu */}
            <div className="relative">
              <button
                onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                className="flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-primary-600 transition-colors"
              >
                <User className="h-4 w-4" />
                <span className="hidden sm:block">{user.username}</span>
                <ChevronDown className="h-4 w-4" />
              </button>

              {isUserMenuOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg border border-gray-200 py-1 z-50">
                  <div className="px-4 py-2 text-sm text-gray-500 border-b border-gray-100">
                    {user.role === "admin" ? "Administrator" : "User"}
                  </div>
                  <button
                    onClick={handleLogout}
                    className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center space-x-2"
                  >
                    <LogOut className="h-4 w-4" />
                    <span>{t("logout")}</span>
                  </button>
                </div>
              )}
            </div>

            {/* Mobile menu button */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="md:hidden p-2 rounded-md text-gray-700 hover:text-primary-600 hover:bg-gray-100 transition-colors"
            >
              {isMenuOpen ? (
                <X className="h-6 w-6" />
              ) : (
                <Menu className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden border-t border-gray-200 py-4">
            <div className="flex flex-col space-y-2">
              <Link
                to="/"
                className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                onClick={() => setIsMenuOpen(false)}
              >
                {t("main_menu")}
              </Link>
              <Link
                to="/borrow"
                className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                onClick={() => setIsMenuOpen(false)}
              >
                {t("borrow")}
              </Link>
              <Link
                to="/return"
                className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                onClick={() => setIsMenuOpen(false)}
              >
                {t("return")}
              </Link>
              {user.role === "admin" && (
                <Link
                  to="/admin"
                  className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                  onClick={() => setIsMenuOpen(false)}
                >
                  {t("admin")}
                </Link>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Overlay for dropdowns */}
      {(isLanguageOpen || isUserMenuOpen) && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => {
            setIsLanguageOpen(false);
            setIsUserMenuOpen(false);
          }}
        />
      )}
    </header>
  );
};

export default Header;
