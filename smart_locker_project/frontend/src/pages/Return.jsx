import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useLanguage } from "../contexts/LanguageContext";
import { useDarkMode } from "../contexts/DarkModeContext";
import {
  CreditCard,
  Package,
  MapPin,
  CheckCircle,
  AlertCircle,
  User,
  ArrowLeft,
} from "lucide-react";
import axios from "axios";

const Return = () => {
  const { t } = useLanguage();
  const { isDarkMode } = useDarkMode();
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [rfidCard, setRfidCard] = useState("");
  const [userId, setUserId] = useState("");
  const [useUserId, setUseUserId] = useState(false);
  const [borrowedItems, setBorrowedItems] = useState([]);
  const [selectedItem, setSelectedItem] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleRfidScan = () => {
    // Simulate RFID scan
    const mockRfid =
      "RFID_" + Math.random().toString(36).substr(2, 9).toUpperCase();
    setRfidCard(mockRfid);
    setUseUserId(false);
    fetchBorrowedItems(mockRfid);
    setStep(2);
  };

  const handleUserIdSubmit = () => {
    if (userId.trim()) {
      setUseUserId(true);
      fetchBorrowedItems(userId);
      setStep(2);
    }
  };

  const fetchBorrowedItems = async (identifier) => {
    try {
      // Simulate fetching borrowed items
      const mockItems = [
        {
          id: 1,
          name: "Laptop Dell XPS 13",
          locker: { number: "A1", location: "Building A" },
          borrowed_at: "2024-01-15T10:30:00Z",
        },
        {
          id: 2,
          name: "Projector Epson",
          locker: { number: "B2", location: "Building B" },
          borrowed_at: "2024-01-14T14:20:00Z",
        },
      ];
      setBorrowedItems(mockItems);
    } catch (error) {
      console.error("Error fetching borrowed items:", error);
      setError(t("error_fetching_items"));
    }
  };

  const handleItemSelect = (item) => {
    setSelectedItem(item);
    setStep(3);
  };

  const handleConfirmReturn = async () => {
    setLoading(true);
    setError("");

    try {
      await axios.post("/api/return", {
        rfid_card: useUserId ? userId : rfidCard,
        item_id: selectedItem.id,
        locker_id: selectedItem.locker.id,
      });

      setSuccess(t("return_success"));
      setTimeout(() => {
        navigate("/");
      }, 2000);
    } catch (error) {
      setError(error.response?.data?.message || t("return_error"));
    } finally {
      setLoading(false);
    }
  };

  const resetProcess = () => {
    setStep(1);
    setRfidCard("");
    setUserId("");
    setSelectedItem(null);
    setError("");
    setSuccess("");
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1
          className={`text-3xl font-bold mb-2 ${
            isDarkMode ? "text-white" : "text-gray-900"
          }`}
        >
          {t("return_item")}
        </h1>
        <p className={`${isDarkMode ? "text-gray-300" : "text-gray-600"}`}>
          {t("follow_steps_return")}
        </p>
      </div>

      {/* Progress Steps */}
      <div className="mb-8">
        <div className="flex items-center justify-center space-x-4">
          {[1, 2, 3].map((stepNumber) => (
            <div key={stepNumber} className="flex items-center">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  step >= stepNumber
                    ? "bg-primary-600 text-white"
                    : "bg-gray-200 text-gray-600"
                }`}
              >
                {stepNumber}
              </div>
              {stepNumber < 3 && (
                <div
                  className={`w-16 h-1 mx-2 ${
                    step > stepNumber ? "bg-primary-600" : "bg-gray-200"
                  }`}
                />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Error/Success Messages */}
      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center">
          <AlertCircle className="h-5 w-5 mr-2" />
          {error}
        </div>
      )}

      {success && (
        <div className="mb-6 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg flex items-center">
          <CheckCircle className="h-5 w-5 mr-2" />
          {success}
        </div>
      )}

      {/* Step 1: Authentication */}
      {step === 1 && (
        <div className="card text-center">
          <div className="mb-6">
            <div className="bg-primary-100 p-4 rounded-full w-20 h-20 mx-auto mb-4 flex items-center justify-center">
              <CreditCard className="h-10 w-10 text-primary-600" />
            </div>
            <h2
              className={`text-2xl font-semibold mb-2 ${
                isDarkMode ? "text-white" : "text-gray-900"
              }`}
            >
              {t("authentication")}
            </h2>
            <p className={`${isDarkMode ? "text-gray-300" : "text-gray-600"}`}>
              {t("choose_authentication_method")}
            </p>
          </div>

          {/* RFID Option */}
          <div className="mb-6">
            <div
              className={`p-4 rounded-lg mb-4 ${
                isDarkMode ? "bg-gray-700" : "bg-gray-50"
              }`}
            >
              <h3
                className={`text-lg font-medium mb-2 ${
                  isDarkMode ? "text-white" : "text-gray-900"
                }`}
              >
                {t("rfid_card")}
              </h3>
              <p
                className={`text-sm ${
                  isDarkMode ? "text-gray-300" : "text-gray-600"
                }`}
              >
                {t("scan_rfid_return_description")}
              </p>
              <button onClick={handleRfidScan} className="btn-primary mt-3">
                {t("simulate_rfid_scan")}
              </button>
            </div>

            {/* User ID Option */}
            <div
              className={`p-4 rounded-lg ${
                isDarkMode ? "bg-gray-700" : "bg-gray-50"
              }`}
            >
              <h3
                className={`text-lg font-medium mb-2 ${
                  isDarkMode ? "text-white" : "text-gray-900"
                }`}
              >
                {t("user_id")}
              </h3>
              <p
                className={`text-sm ${
                  isDarkMode ? "text-gray-300" : "text-gray-600"
                }`}
              >
                {t("enter_user_id_return_description")}
              </p>
              <div className="mt-3 flex space-x-2">
                <input
                  type="text"
                  value={userId}
                  onChange={(e) => setUserId(e.target.value)}
                  placeholder={t("enter_user_id")}
                  className={`flex-1 px-3 py-2 border rounded-md ${
                    isDarkMode
                      ? "bg-gray-700 border-gray-600 text-white"
                      : "bg-white border-gray-300 text-gray-900"
                  }`}
                />
                <button
                  onClick={handleUserIdSubmit}
                  disabled={!userId.trim()}
                  className="btn-primary disabled:opacity-50"
                >
                  {t("continue")}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Step 2: Item Selection */}
      {step === 2 && (
        <div className="card">
          <div className="mb-6">
            <h2
              className={`text-2xl font-semibold mb-2 ${
                isDarkMode ? "text-white" : "text-gray-900"
              }`}
            >
              {t("select_item_return")}
            </h2>
            <p className={`${isDarkMode ? "text-gray-300" : "text-gray-600"}`}>
              {t("choose_item_return")}
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {borrowedItems.map((item) => (
              <button
                key={item.id}
                onClick={() => handleItemSelect(item)}
                className={`p-4 border rounded-lg transition-colors text-left ${
                  isDarkMode
                    ? "border-gray-600 hover:border-primary-400 hover:bg-gray-700"
                    : "border-gray-200 hover:border-primary-300 hover:bg-primary-50"
                }`}
              >
                <div className="flex items-center space-x-3">
                  <Package className="h-6 w-6 text-primary-600" />
                  <div>
                    <h3
                      className={`font-medium ${
                        isDarkMode ? "text-white" : "text-gray-900"
                      }`}
                    >
                      {item.name}
                    </h3>
                    <p
                      className={`text-sm ${
                        isDarkMode ? "text-gray-300" : "text-gray-600"
                      }`}
                    >
                      {t("locker")} {item.locker.number} -{" "}
                      {item.locker.location}
                    </p>
                    <p
                      className={`text-xs ${
                        isDarkMode ? "text-gray-400" : "text-gray-500"
                      }`}
                    >
                      {t("borrowed_on")}:{" "}
                      {new Date(item.borrowed_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Step 3: Confirmation */}
      {step === 3 && (
        <div className="card">
          <div className="mb-6">
            <h2
              className={`text-2xl font-semibold mb-2 ${
                isDarkMode ? "text-white" : "text-gray-900"
              }`}
            >
              {t("confirm_return")}
            </h2>
            <p className={`${isDarkMode ? "text-gray-300" : "text-gray-600"}`}>
              {t("confirm_return_details")}
            </p>
          </div>

          <div
            className={`rounded-lg p-6 mb-6 ${
              isDarkMode ? "bg-gray-700" : "bg-gray-50"
            }`}
          >
            <div className="space-y-4">
              <div className="flex justify-between">
                <span
                  className={`${
                    isDarkMode ? "text-gray-300" : "text-gray-600"
                  }`}
                >
                  {useUserId ? t("user_id") : t("rfid_card")}:
                </span>
                <span
                  className={`font-medium ${
                    isDarkMode ? "text-white" : "text-gray-900"
                  }`}
                >
                  {useUserId ? userId : rfidCard}
                </span>
              </div>
              <div className="flex justify-between">
                <span
                  className={`${
                    isDarkMode ? "text-gray-300" : "text-gray-600"
                  }`}
                >
                  {t("item")}:
                </span>
                <span
                  className={`font-medium ${
                    isDarkMode ? "text-white" : "text-gray-900"
                  }`}
                >
                  {selectedItem?.name}
                </span>
              </div>
              <div className="flex justify-between">
                <span
                  className={`${
                    isDarkMode ? "text-gray-300" : "text-gray-600"
                  }`}
                >
                  {t("locker")}:
                </span>
                <span
                  className={`font-medium ${
                    isDarkMode ? "text-white" : "text-gray-900"
                  }`}
                >
                  {t("locker")} {selectedItem?.locker.number}
                </span>
              </div>
            </div>
          </div>

          <div className="flex space-x-4">
            <button onClick={resetProcess} className="btn-secondary">
              {t("cancel")}
            </button>
            <button
              onClick={handleConfirmReturn}
              disabled={loading}
              className="btn-primary flex-1"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              ) : (
                t("confirm_return")
              )}
            </button>
          </div>
        </div>
      )}

      {/* Back Button */}
      <div className="mt-8 text-center">
        <button
          onClick={() => navigate("/")}
          className={`inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium ${
            isDarkMode
              ? "bg-gray-700 text-white hover:bg-gray-600 border-gray-600"
              : "bg-white text-gray-700 hover:bg-gray-50"
          }`}
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          {t("back_to_main_menu")}
        </button>
      </div>
    </div>
  );
};

export default Return;
