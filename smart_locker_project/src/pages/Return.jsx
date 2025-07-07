import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useLanguage } from "../contexts/LanguageContext";
import { CreditCard, CheckCircle, AlertCircle, ArrowLeft } from "lucide-react";
import axios from "axios";

const Return = () => {
  const { t } = useLanguage();
  const navigate = useNavigate();
  const [rfidCard, setRfidCard] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleRfidScan = async () => {
    setLoading(true);
    setError("");

    // Simulate RFID scan
    const mockRfid =
      "RFID_" + Math.random().toString(36).substr(2, 9).toUpperCase();
    setRfidCard(mockRfid);

    try {
      await axios.post("/api/return", {
        rfid_card: mockRfid,
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

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          {t("return_item")}
        </h1>
        <p className="text-gray-600">
          Scan your RFID card to return your borrowed item
        </p>
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

      {/* RFID Scan Section */}
      <div className="card text-center">
        <div className="mb-8">
          <div className="bg-primary-100 p-6 rounded-full w-24 h-24 mx-auto mb-6 flex items-center justify-center">
            <CreditCard className="h-12 w-12 text-primary-600" />
          </div>
          <h2 className="text-2xl font-semibold text-gray-900 mb-2">
            {t("scan_rfid")}
          </h2>
          <p className="text-gray-600">
            Please scan your RFID card to return your item
          </p>
        </div>

        {rfidCard && (
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-600 mb-1">Scanned RFID:</p>
            <p className="font-mono text-lg font-medium text-gray-900">
              {rfidCard}
            </p>
          </div>
        )}

        <div className="space-y-4">
          <button
            onClick={handleRfidScan}
            disabled={loading}
            className="btn-primary w-full"
          >
            {loading ? (
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
            ) : (
              "Simulate RFID Scan & Return"
            )}
          </button>

          <button
            onClick={() => navigate("/")}
            className="btn-secondary w-full"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Main Menu
          </button>
        </div>
      </div>
    </div>
  );
};

export default Return;
