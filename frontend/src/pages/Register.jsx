/**
 * Smart Locker System - Register Component
 *
 * @author Alp
 * @date 2024-12-XX
 * @description Secure registration form for new users
 */

import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useLanguage } from "../contexts/LanguageContext";
import { useDarkMode } from "../contexts/DarkModeContext";
import { register } from "../utils/api";
import {
  User,
  Mail,
  Lock,
  Eye,
  EyeOff,
  CheckCircle,
  XCircle,
  AlertCircle,
  CreditCard,
  QrCode,
  Globe,
  ChevronDown,
} from "lucide-react";

const Register = () => {
  const { t, currentLanguage, changeLanguage, availableLanguages } =
    useLanguage();
  const { isDarkMode } = useDarkMode();
  const navigate = useNavigate();
  const [isLanguageOpen, setIsLanguageOpen] = useState(false);
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
    first_name: "",
    last_name: "",
    student_id: "",
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [passwordStrength, setPasswordStrength] = useState({
    length: false,
    uppercase: false,
    lowercase: false,
    number: false,
    special: false,
  });

  const validatePassword = (password) => {
    const checks = {
      length: password.length >= 8,
      uppercase: /[A-Z]/.test(password),
      lowercase: /[a-z]/.test(password),
      number: /\d/.test(password),
      special: /[!@#$%^&*(),.?":{}|<>]/.test(password),
    };
    setPasswordStrength(checks);
    return Object.values(checks).every(Boolean);
  };

  const generateTestStudentId = () => {
    // Generate a unique test student ID
    const timestamp = Date.now();
    const random = Math.floor(Math.random() * 1000);
    const testId = `TEST${timestamp}${random}`;
    setFormData((prev) => ({
      ...prev,
      student_id: testId,
    }));
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));

    if (name === "password") {
      validatePassword(value);
    }

    // Clear errors when user starts typing
    if (error) setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSuccess("");

    // Validation
    if (
      !formData.username ||
      !formData.email ||
      !formData.password ||
      !formData.student_id
    ) {
      setError(t("all_fields_required") || "All fields are required");
      setLoading(false);
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError(t("passwords_dont_match") || "Passwords don't match");
      setLoading(false);
      return;
    }

    if (!validatePassword(formData.password)) {
      setError(
        t("password_requirements_not_met") || "Password requirements not met"
      );
      setLoading(false);
      return;
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setError(t("invalid_email") || "Invalid email address");
      setLoading(false);
      return;
    }

    try {
      const response = await register({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        first_name: formData.first_name,
        last_name: formData.last_name,
        student_id: formData.student_id,
        role: "student", // Default role for new registrations
      });

      setSuccess(
        t("registration_successful") ||
          "Registration successful! Please log in."
      );

      // Clear form
      setFormData({
        username: "",
        email: "",
        password: "",
        confirmPassword: "",
        first_name: "",
        last_name: "",
        student_id: "",
      });

      // Redirect to login after 2 seconds
      setTimeout(() => {
        navigate("/login");
      }, 2000);
    } catch (error) {
      console.error("Registration error:", error);
      setError(
        error.response?.data?.error ||
          t("registration_failed") ||
          "Registration failed. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  const getPasswordStrengthColor = () => {
    const validChecks = Object.values(passwordStrength).filter(Boolean).length;
    if (validChecks <= 2) return "text-red-500";
    if (validChecks <= 3) return "text-yellow-500";
    return "text-green-500";
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

  return (
    <div className="min-h-screen transition-colors duration-200 bg-gray-900 text-white">
      <main className="pt-20 pb-8">
        {/* Language Selector */}
        <div className="absolute top-4 right-4">
          <div className="relative">
            <button
              onClick={() => setIsLanguageOpen(!isLanguageOpen)}
              className="flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors shadow-sm text-gray-300 hover:text-white bg-gray-800"
            >
              <Globe className="h-4 w-4" />
              <span>{languageFlags[currentLanguage]}</span>
              <ChevronDown className="h-4 w-4" />
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
                    className={`w-full text-left px-4 py-2 text-sm flex items-center space-x-2 ${
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

        <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
          <div className="max-w-md w-full space-y-8">
            <div>
              <div className="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-primary-100">
                <User className="h-6 w-6 text-primary-600" />
              </div>
              <h2 className="mt-6 text-center text-3xl font-extrabold text-white">
                {t("create_account")}
              </h2>
              <p className="mt-2 text-center text-sm text-gray-300">
                {t("register_description")}
              </p>
            </div>

            <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
              {error && (
                <div className="rounded-md bg-red-50 p-4 border border-red-200">
                  <div className="flex">
                    <XCircle className="h-5 w-5 text-red-400" />
                    <div className="ml-3">
                      <p className="text-sm text-red-800">{error}</p>
                    </div>
                  </div>
                </div>
              )}

              {success && (
                <div className="rounded-md bg-green-50 p-4 border border-green-200">
                  <div className="flex">
                    <CheckCircle className="h-5 w-5 text-green-400" />
                    <div className="ml-3">
                      <p className="text-sm text-green-800">{success}</p>
                    </div>
                  </div>
                </div>
              )}

              <div className="space-y-4">
                {/* Username */}
                <div>
                  <label
                    htmlFor="username"
                    className="block text-sm font-medium text-gray-300"
                  >
                    {t("username")}
                  </label>
                  <div className="mt-1 relative">
                    <input
                      id="username"
                      name="username"
                      type="text"
                      required
                      value={formData.username}
                      onChange={handleInputChange}
                      className="appearance-none relative block w-full px-3 py-2 border rounded-md placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm bg-gray-700 border-gray-600 text-white"
                      placeholder={t("username_placeholder")}
                    />
                  </div>
                </div>

                {/* Email */}
                <div>
                  <label
                    htmlFor="email"
                    className="block text-sm font-medium text-gray-300"
                  >
                    {t("email")}
                  </label>
                  <div className="mt-1 relative">
                    <input
                      id="email"
                      name="email"
                      type="email"
                      required
                      value={formData.email}
                      onChange={handleInputChange}
                      className="appearance-none relative block w-full px-3 py-2 border rounded-md placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm bg-gray-700 border-gray-600 text-white"
                      placeholder={t("email_placeholder")}
                    />
                  </div>
                </div>

                {/* First Name */}
                <div>
                  <label
                    htmlFor="first_name"
                    className="block text-sm font-medium text-gray-300"
                  >
                    {t("first_name")}
                  </label>
                  <div className="mt-1 relative">
                    <input
                      id="first_name"
                      name="first_name"
                      type="text"
                      value={formData.first_name}
                      onChange={handleInputChange}
                      className="appearance-none relative block w-full px-3 py-2 border rounded-md placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm bg-gray-700 border-gray-600 text-white"
                      placeholder={t("first_name_placeholder")}
                    />
                  </div>
                </div>

                {/* Last Name */}
                <div>
                  <label
                    htmlFor="last_name"
                    className="block text-sm font-medium text-gray-300"
                  >
                    {t("last_name")}
                  </label>
                  <div className="mt-1 relative">
                    <input
                      id="last_name"
                      name="last_name"
                      type="text"
                      value={formData.last_name}
                      onChange={handleInputChange}
                      className="appearance-none relative block w-full px-3 py-2 border rounded-md placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm bg-gray-700 border-gray-600 text-white"
                      placeholder={t("last_name_placeholder")}
                    />
                  </div>
                </div>

                {/* Student ID */}
                <div>
                  <label
                    htmlFor="student_id"
                    className="block text-sm font-medium text-gray-300"
                  >
                    {t("student_id")}
                  </label>
                  <div className="mt-1 relative">
                    <input
                      id="student_id"
                      name="student_id"
                      type="text"
                      required
                      value={formData.student_id}
                      onChange={handleInputChange}
                      className="appearance-none relative block w-full px-3 py-2 border rounded-md placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm bg-gray-700 border-gray-600 text-white"
                      placeholder={t("student_id_placeholder")}
                    />
                  </div>
                  <div className="mt-2 flex space-x-2">
                    <button
                      type="button"
                      onClick={generateTestStudentId}
                      className="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded text-primary-600 bg-primary-100 hover:bg-primary-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                    >
                      <QrCode className="h-3 w-3 mr-1" />
                      {t("generate_test_id")}
                    </button>
                    <span className="text-xs text-gray-400 flex items-center">
                      <CreditCard className="h-3 w-3 mr-1" />
                      {t("scan_card_description")}
                    </span>
                  </div>
                </div>

                {/* Password */}
                <div>
                  <label
                    htmlFor="password"
                    className="block text-sm font-medium text-gray-300"
                  >
                    {t("password")}
                  </label>
                  <div className="mt-1 relative">
                    <input
                      id="password"
                      name="password"
                      type={showPassword ? "text" : "password"}
                      required
                      value={formData.password}
                      onChange={handleInputChange}
                      className="appearance-none relative block w-full px-3 py-2 border rounded-md placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm pr-10 bg-gray-700 border-gray-600 text-white"
                      placeholder={t("password_placeholder")}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    >
                      {showPassword ? (
                        <EyeOff className="h-5 w-5 text-gray-400" />
                      ) : (
                        <Eye className="h-5 w-5 text-gray-400" />
                      )}
                    </button>
                  </div>

                  {/* Password Strength Indicator */}
                  <div className="mt-2 space-y-1">
                    <p className="text-xs text-red-500">
                      {t("password_requirements")}
                    </p>
                    <div className="space-y-1">
                      {[
                        {
                          key: "length",
                          label: t("min_8_characters"),
                        },
                        {
                          key: "uppercase",
                          label: t("one_uppercase"),
                        },
                        {
                          key: "lowercase",
                          label: t("one_lowercase"),
                        },
                        { key: "number", label: t("one_number") },
                        {
                          key: "special",
                          label: t("one_special"),
                        },
                      ].map(({ key, label }) => (
                        <div key={key} className="flex items-center text-xs">
                          {passwordStrength[key] ? (
                            <CheckCircle className="h-3 w-3 text-green-500 mr-1" />
                          ) : (
                            <XCircle className="h-3 w-3 text-red-500 mr-1" />
                          )}
                          <span className="text-gray-400">{label}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Confirm Password */}
                <div>
                  <label
                    htmlFor="confirmPassword"
                    className="block text-sm font-medium text-gray-300"
                  >
                    {t("confirm_password")}
                  </label>
                  <div className="mt-1 relative">
                    <input
                      id="confirmPassword"
                      name="confirmPassword"
                      type={showConfirmPassword ? "text" : "password"}
                      required
                      value={formData.confirmPassword}
                      onChange={handleInputChange}
                      className="appearance-none relative block w-full px-3 py-2 border rounded-md placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm pr-10 bg-gray-700 border-gray-600 text-white"
                      placeholder={t("confirm_password_placeholder")}
                    />
                    <button
                      type="button"
                      onClick={() =>
                        setShowConfirmPassword(!showConfirmPassword)
                      }
                      className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    >
                      {showConfirmPassword ? (
                        <EyeOff className="h-5 w-5 text-gray-400" />
                      ) : (
                        <Eye className="h-5 w-5 text-gray-400" />
                      )}
                    </button>
                  </div>
                </div>
              </div>

              <div>
                <button
                  type="submit"
                  disabled={loading}
                  className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed focus:ring-offset-gray-800"
                >
                  {loading ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  ) : (
                    t("register")
                  )}
                </button>
              </div>

              <div className="text-center">
                <p className="text-sm text-gray-300">
                  {t("already_have_account")}{" "}
                  <Link
                    to="/login"
                    className="font-medium text-primary-600 hover:text-primary-500"
                  >
                    {t("sign_in")}
                  </Link>
                </p>
              </div>
            </form>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Register;
