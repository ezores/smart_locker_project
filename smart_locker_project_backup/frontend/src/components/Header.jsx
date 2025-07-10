/**
 * Smart Locker System - Header Component
 *
 * @author Alp
 * @date 2024-12-XX
 * @description Main header with navigation, language selector, dark mode toggle, and user menu
 */

import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { useLanguage } from "../contexts/LanguageContext";
import { useDarkMode } from "../contexts/DarkModeContext";
import {
  Menu,
  X,
  User,
  LogOut,
  Globe,
  ChevronDown,
  Sun,
  Moon,
  Home,
  Package,
  RotateCcw,
  Settings,
} from "lucide-react";

const Header = () => {
  const { user, logout } = useAuth();
  const { t, currentLanguage, changeLanguage, availableLanguages } =
    useLanguage();
  const { isDarkMode, toggleDarkMode } = useDarkMode();
  const navigate = useNavigate();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isLanguageOpen, setIsLanguageOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);

  const handleLogout = () => {
    setIsMenuOpen(false);
    setIsLanguageOpen(false);
    setIsUserMenuOpen(false);
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

  const navigationItems = [
    { to: "/", label: t("main_menu"), icon: Home },
    { to: "/borrow", label: t("borrow"), icon: Package },
    { to: "/return", label: t("return"), icon: RotateCcw },
  ];

  // Add admin items only for admin users
  if (user?.role === "admin") {
    navigationItems.push({ to: "/admin", label: t("admin"), icon: Settings });
  }

  if (!user) return null;

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 shadow-sm border-b transition-colors duration-200 ${
        isDarkMode
          ? "bg-gray-800 border-gray-700 text-white"
          : "bg-white border-gray-200 text-gray-900"
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and Brand */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-3">
              <img src="/ETS-logo.png" alt="ETS Logo" className="h-10 w-auto" />
            </Link>
          </div>

          {/* Centered Brand */}
          <div className="flex-1 flex justify-center">
            <div className="text-center">
              <h1
                className={`text-xl font-bold ${
                  isDarkMode ? "text-white" : "text-gray-900"
                }`}
              >
                LACIME
              </h1>
              <p
                className={`text-sm ${
                  isDarkMode ? "text-gray-300" : "text-gray-600"
                }`}
              >
                Smart Locker System
              </p>
            </div>
          </div>

          {/* Right side - Language, Dark Mode, User, and Hamburger */}
          <div className="flex items-center space-x-4">
            {/* Language Selector */}
            <div className="relative">
              <button
                onClick={() => setIsLanguageOpen(!isLanguageOpen)}
                className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isDarkMode
                    ? "text-gray-300 hover:text-white hover:bg-gray-700"
                    : "text-gray-700 hover:text-primary-600 hover:bg-gray-100"
                }`}
              >
                <Globe className="h-4 w-4" />
                <span className="hidden sm:block">
                  {languageFlags[currentLanguage]}
                </span>
                <ChevronDown className="h-4 w-4" />
              </button>

              {isLanguageOpen && (
                <div
                  className={`absolute right-0 mt-2 w-48 rounded-md shadow-lg border py-1 z-50 ${
                    isDarkMode
                      ? "bg-gray-800 border-gray-600"
                      : "bg-white border-gray-200"
                  }`}
                >
                  {availableLanguages.map((lang) => (
                    <button
                      key={lang}
                      onClick={() => {
                        changeLanguage(lang);
                        setIsLanguageOpen(false);
                      }}
                      className={`w-full text-left px-4 py-2 text-sm flex items-center space-x-2 transition-colors ${
                        currentLanguage === lang
                          ? isDarkMode
                            ? "bg-gray-700 text-white"
                            : "bg-primary-50 text-primary-700"
                          : isDarkMode
                          ? "text-gray-300 hover:bg-gray-700 hover:text-white"
                          : "text-gray-700 hover:bg-gray-50"
                      }`}
                    >
                      <span>{languageFlags[lang]}</span>
                      <span>{languageNames[lang]}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Dark Mode Toggle */}
            <button
              onClick={toggleDarkMode}
              className={`p-2 rounded-md text-sm font-medium transition-colors ${
                isDarkMode
                  ? "text-gray-300 hover:text-white hover:bg-gray-700"
                  : "text-gray-700 hover:text-primary-600 hover:bg-gray-100"
              }`}
              title={
                isDarkMode ? "Switch to light mode" : "Switch to dark mode"
              }
            >
              {isDarkMode ? (
                <Sun className="h-4 w-4" />
              ) : (
                <Moon className="h-4 w-4" />
              )}
            </button>

            {/* User Menu */}
            <div className="relative">
              <button
                onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isDarkMode
                    ? "text-gray-300 hover:text-white hover:bg-gray-700"
                    : "text-gray-700 hover:text-primary-600 hover:bg-gray-100"
                }`}
              >
                <User className="h-4 w-4" />
                <span className="hidden sm:block">{user.username}</span>
                <ChevronDown className="h-4 w-4" />
              </button>

              {isUserMenuOpen && (
                <div
                  className={`absolute right-0 mt-2 w-48 rounded-md shadow-lg border py-1 z-50 ${
                    isDarkMode
                      ? "bg-gray-800 border-gray-600"
                      : "bg-white border-gray-200"
                  }`}
                >
                  <div
                    className={`px-4 py-2 text-sm border-b ${
                      isDarkMode
                        ? "text-gray-400 border-gray-600"
                        : "text-gray-500 border-gray-100"
                    }`}
                  >
                    {user.role === "admin" ? "Administrator" : "User"}
                  </div>
                  <button
                    onClick={handleLogout}
                    className={`w-full text-left px-4 py-2 text-sm flex items-center space-x-2 transition-colors ${
                      isDarkMode
                        ? "text-gray-300 hover:bg-gray-700 hover:text-white"
                        : "text-gray-700 hover:bg-gray-50"
                    }`}
                  >
                    <LogOut className="h-4 w-4" />
                    <span>{t("logout")}</span>
                  </button>
                </div>
              )}
            </div>

            {/* Hamburger menu button */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className={`p-2 rounded-md transition-colors ${
                isDarkMode
                  ? "text-gray-300 hover:text-white hover:bg-gray-700"
                  : "text-gray-700 hover:text-primary-600 hover:bg-gray-100"
              }`}
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
          <div
            className={`border-t py-4 ${
              isDarkMode ? "border-gray-700" : "border-gray-200"
            }`}
          >
            <div className="flex flex-col space-y-2">
              {navigationItems.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.to}
                    to={item.to}
                    className={`flex items-center space-x-3 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      isDarkMode
                        ? "text-gray-300 hover:text-white hover:bg-gray-700"
                        : "text-gray-700 hover:text-primary-600 hover:bg-gray-100"
                    }`}
                    onClick={() => setIsMenuOpen(false)}
                  >
                    <Icon className="h-4 w-4" />
                    <span>{item.label}</span>
                  </Link>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
