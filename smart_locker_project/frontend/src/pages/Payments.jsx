/**
 * Smart Locker System - Payments Component
 *
 * @author Alp
 * @date 2024-12-XX
 * @description Payment management component with Stripe integration
 */

import { useState, useEffect } from "react";
import { useLanguage } from "../contexts/LanguageContext";
import { useDarkMode } from "../contexts/DarkModeContext";
import { useAuth } from "../contexts/AuthContext";
import {
  CreditCard,
  DollarSign,
  Calendar,
  ArrowLeft,
  Plus,
  Download,
  FileText,
  Search,
  Filter,
  Wallet,
  PlusCircle,
} from "lucide-react";
import axios from "axios";

const Payments = () => {
  const { t } = useLanguage();
  const { isDarkMode } = useDarkMode();
  const { user } = useAuth();
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showPaymentForm, setShowPaymentForm] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterStatus, setFilterStatus] = useState("all");
  const [balance, setBalance] = useState(0);
  const [showAddMoneyModal, setShowAddMoneyModal] = useState(false);
  const [addAmount, setAddAmount] = useState("");

  useEffect(() => {
    fetchPayments();
  }, []);

  const fetchPayments = async () => {
    try {
      if (user.role === "admin") {
        // Admin sees all payments
        // TODO: Replace with actual API endpoint
        // const response = await axios.get("/api/admin/payments");
        // setPayments(response.data);

        // Mock data for admin
        setPayments([
          {
            id: 1,
            amount: 25.0,
            currency: "USD",
            status: "completed",
            description: "Monthly locker rental",
            date: "2024-12-01T10:30:00Z",
            payment_method: "card",
            user_id: 1,
            user_name: "john.doe",
          },
          {
            id: 2,
            amount: 15.5,
            currency: "USD",
            status: "pending",
            description: "Late return fee",
            date: "2024-12-02T14:20:00Z",
            payment_method: "card",
            user_id: 2,
            user_name: "jane.smith",
          },
        ]);
      } else {
        // Student sees only their own payments
        // TODO: Replace with actual API endpoint
        // const response = await axios.get("/api/payments/my-payments");
        // setPayments(response.data);

        // Mock data for student
        setPayments([
          {
            id: 1,
            amount: 10.0,
            currency: "USD",
            status: "completed",
            description: "Locker deposit",
            date: "2024-12-01T10:30:00Z",
            payment_method: "card",
            user_id: user.id,
            user_name: user.username,
          },
        ]);

        // Mock balance for student
        setBalance(25.5);
      }
    } catch (error) {
      console.error("Error fetching payments:", error);
      setPayments([]);
    } finally {
      setLoading(false);
    }
  };

  const filteredPayments = payments.filter((payment) => {
    const matchesSearch =
      payment.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      payment.user_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      payment.amount?.toString().includes(searchTerm);

    const matchesStatus =
      filterStatus === "all" || payment.status === filterStatus;

    return matchesSearch && matchesStatus;
  });

  const getStatusBadge = (status) => {
    const statusConfig = {
      completed: {
        color: "bg-green-100 text-green-800",
        text: t("completed") || "Completed",
      },
      pending: {
        color: "bg-yellow-100 text-yellow-800",
        text: t("pending") || "Pending",
      },
      failed: {
        color: "bg-red-100 text-red-800",
        text: t("failed") || "Failed",
      },
    };

    const config = statusConfig[status] || statusConfig.pending;

    return (
      <span
        className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${config.color}`}
      >
        {config.text}
      </span>
    );
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + " " + date.toLocaleTimeString();
  };

  const exportPayments = async (format) => {
    try {
      // TODO: Implement export functionality
      console.log(`Exporting payments in ${format} format`);
      alert(`Export functionality will be implemented with Stripe integration`);
    } catch (error) {
      console.error("Error exporting payments:", error);
      alert(t("failed_export_payments") || "Failed to export payments");
    }
  };

  const handleAddMoney = async (e) => {
    e.preventDefault();
    try {
      // TODO: Implement Stripe payment
      console.log(`Adding ${addAmount} to balance`);
      alert(`Stripe payment integration will be implemented`);
      setShowAddMoneyModal(false);
      setAddAmount("");
    } catch (error) {
      console.error("Error adding money:", error);
      alert(t("failed_add_money") || "Failed to add money");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1
          className={`text-3xl font-bold mb-2 ${
            isDarkMode ? "text-white" : "text-gray-900"
          }`}
        >
          {user.role === "admin"
            ? t("payments") || "Payments"
            : t("my_balance") || "My Balance"}
        </h1>
        <p className={`${isDarkMode ? "text-gray-300" : "text-gray-600"}`}>
          {user.role === "admin"
            ? t("payments_description") ||
              "Manage payments and billing information"
            : t("balance_description") ||
              "Manage your account balance and payment history"}
        </p>
      </div>

      {/* Student Balance Section */}
      {user.role !== "admin" && (
        <div
          className={`mb-6 p-6 rounded-lg ${
            isDarkMode ? "bg-gray-700" : "bg-blue-50"
          }`}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="bg-green-100 p-3 rounded-lg">
                <Wallet className="h-8 w-8 text-green-600" />
              </div>
              <div>
                <h3
                  className={`text-lg font-semibold ${
                    isDarkMode ? "text-white" : "text-gray-900"
                  }`}
                >
                  {t("current_balance") || "Current Balance"}
                </h3>
                <p className={`text-2xl font-bold text-green-600`}>
                  ${balance.toFixed(2)} USD
                </p>
              </div>
            </div>
            <button
              onClick={() => setShowAddMoneyModal(true)}
              className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              <PlusCircle className="h-4 w-4" />
              <span>{t("add_money") || "Add Money"}</span>
            </button>
          </div>
        </div>
      )}

      {/* Controls */}
      <div className="mb-6 flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center">
        <div className="flex flex-col sm:flex-row gap-4 flex-1">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder={t("search_payments") || "Search payments..."}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className={`pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                isDarkMode
                  ? "bg-gray-700 border-gray-600 text-white"
                  : "bg-white border-gray-300 text-gray-900"
              }`}
            />
          </div>

          {/* Status Filter */}
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className={`px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
              isDarkMode
                ? "bg-gray-700 border-gray-600 text-white"
                : "bg-white border-gray-300 text-gray-900"
            }`}
          >
            <option value="all">{t("all_statuses") || "All Statuses"}</option>
            <option value="completed">{t("completed") || "Completed"}</option>
            <option value="pending">{t("pending") || "Pending"}</option>
            <option value="failed">{t("failed") || "Failed"}</option>
          </select>
        </div>

        {/* Action Buttons */}
        <div className="flex space-x-2">
          {user.role === "admin" && (
            <button
              onClick={() => setShowPaymentForm(true)}
              className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              <Plus className="h-4 w-4" />
              <span>{t("new_payment") || "New Payment"}</span>
            </button>
          )}
          {user.role === "admin" && (
            <>
              <button
                onClick={() => exportPayments("csv")}
                className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                <Download className="h-4 w-4" />
                <span>CSV</span>
              </button>
              <button
                onClick={() => exportPayments("pdf")}
                className="flex items-center space-x-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                <FileText className="h-4 w-4" />
                <span>PDF</span>
              </button>
            </>
          )}
        </div>
      </div>

      {/* Payment History */}
      <div className={`card ${isDarkMode ? "bg-gray-800" : "bg-white"}`}>
        {filteredPayments.length === 0 ? (
          <div className="text-center py-12">
            <CreditCard className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3
              className={`text-lg font-medium mb-2 ${
                isDarkMode ? "text-white" : "text-gray-900"
              }`}
            >
              {t("no_payments_found") || "No payments found"}
            </h3>
            <p className={`${isDarkMode ? "text-gray-300" : "text-gray-600"}`}>
              {searchTerm || filterStatus !== "all"
                ? t("try_adjusting_search") ||
                  "Try adjusting your search criteria"
                : t("no_payments_yet") || "No payments have been made yet"}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className={`${isDarkMode ? "bg-gray-700" : "bg-gray-50"}`}>
                <tr>
                  <th
                    className={`px-6 py-3 text-left text-xs font-medium uppercase tracking-wider ${
                      isDarkMode ? "text-gray-300" : "text-gray-500"
                    }`}
                  >
                    {t("user") || "User"}
                  </th>
                  <th
                    className={`px-6 py-3 text-left text-xs font-medium uppercase tracking-wider ${
                      isDarkMode ? "text-gray-300" : "text-gray-500"
                    }`}
                  >
                    {t("description") || "Description"}
                  </th>
                  <th
                    className={`px-6 py-3 text-left text-xs font-medium uppercase tracking-wider ${
                      isDarkMode ? "text-gray-300" : "text-gray-500"
                    }`}
                  >
                    {t("amount") || "Amount"}
                  </th>
                  <th
                    className={`px-6 py-3 text-left text-xs font-medium uppercase tracking-wider ${
                      isDarkMode ? "text-gray-300" : "text-gray-500"
                    }`}
                  >
                    {t("status") || "Status"}
                  </th>
                  <th
                    className={`px-6 py-3 text-left text-xs font-medium uppercase tracking-wider ${
                      isDarkMode ? "text-gray-300" : "text-gray-500"
                    }`}
                  >
                    {t("date") || "Date"}
                  </th>
                </tr>
              </thead>
              <tbody
                className={`divide-y ${
                  isDarkMode ? "divide-gray-700" : "divide-gray-200"
                }`}
              >
                {filteredPayments.map((payment) => (
                  <tr
                    key={payment.id}
                    className={`${
                      isDarkMode
                        ? "bg-gray-800 hover:bg-gray-700"
                        : "bg-white hover:bg-gray-50"
                    }`}
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-8 w-8">
                          <div className="h-8 w-8 rounded-full flex items-center justify-center bg-gray-100">
                            <CreditCard className="h-4 w-4 text-gray-600" />
                          </div>
                        </div>
                        <div className="ml-3">
                          <div
                            className={`text-sm font-medium ${
                              isDarkMode ? "text-white" : "text-gray-900"
                            }`}
                          >
                            {payment.user_name}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div
                        className={`text-sm ${
                          isDarkMode ? "text-gray-300" : "text-gray-900"
                        }`}
                      >
                        {payment.description}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <DollarSign className="h-4 w-4 text-green-600 mr-1" />
                        <span
                          className={`text-sm font-medium ${
                            isDarkMode ? "text-white" : "text-gray-900"
                          }`}
                        >
                          {payment.amount} {payment.currency}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getStatusBadge(payment.status)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <Calendar className="h-4 w-4 text-gray-400 mr-2" />
                        <span
                          className={`text-sm ${
                            isDarkMode ? "text-gray-300" : "text-gray-900"
                          }`}
                        >
                          {formatDate(payment.date)}
                        </span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Stripe Integration Notice - Only for Admin */}
      {user.role === "admin" && (
        <div
          className={`mt-8 p-6 rounded-lg ${
            isDarkMode ? "bg-gray-700" : "bg-blue-50"
          }`}
        >
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <CreditCard className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-3">
              <h3
                className={`text-lg font-medium ${
                  isDarkMode ? "text-white" : "text-blue-900"
                }`}
              >
                {t("stripe_integration") || "Stripe Integration"}
              </h3>
              <div
                className={`mt-2 text-sm ${
                  isDarkMode ? "text-gray-300" : "text-blue-700"
                }`}
              >
                <p>
                  {t("stripe_notice") ||
                    "This payment system is designed to integrate with Stripe for secure payment processing. The integration includes:"}
                </p>
                <ul className="mt-2 list-disc list-inside space-y-1">
                  <li>
                    {t("stripe_feature_1") ||
                      "Secure payment processing with Stripe Checkout"}
                  </li>
                  <li>
                    {t("stripe_feature_2") ||
                      "Automatic payment confirmation and webhook handling"}
                  </li>
                  <li>
                    {t("stripe_feature_3") ||
                      "Payment history and receipt generation"}
                  </li>
                  <li>
                    {t("stripe_feature_4") ||
                      "Subscription management for recurring payments"}
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Add Money Modal for Students */}
      {showAddMoneyModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div
            className={`max-w-md w-full mx-4 rounded-lg shadow-xl ${
              isDarkMode ? "bg-gray-800" : "bg-white"
            }`}
          >
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <h3
                className={`text-lg font-medium ${
                  isDarkMode ? "text-white" : "text-gray-900"
                }`}
              >
                {t("add_money") || "Add Money"}
              </h3>
              <button
                onClick={() => setShowAddMoneyModal(false)}
                className={`p-1 rounded-md ${
                  isDarkMode
                    ? "text-gray-400 hover:text-white"
                    : "text-gray-400 hover:text-gray-600"
                }`}
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <form onSubmit={handleAddMoney} className="p-6 space-y-4">
              <div>
                <label
                  className={`block text-sm font-medium mb-2 ${
                    isDarkMode ? "text-white" : "text-gray-700"
                  }`}
                >
                  {t("amount") || "Amount"} (USD)
                </label>
                <input
                  type="number"
                  min="1"
                  step="0.01"
                  required
                  value={addAmount}
                  onChange={(e) => setAddAmount(e.target.value)}
                  className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                    isDarkMode
                      ? "bg-gray-700 border-gray-600 text-white"
                      : "bg-white border-gray-300 text-gray-900"
                  }`}
                />
              </div>
              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowAddMoneyModal(false)}
                  className={`px-4 py-2 border rounded-md ${
                    isDarkMode
                      ? "border-gray-600 text-gray-300 hover:bg-gray-700"
                      : "border-gray-300 text-gray-700 hover:bg-gray-50"
                  }`}
                >
                  {t("cancel") || "Cancel"}
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                >
                  {t("add_money") || "Add Money"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Back Button */}
      <div className="mt-8 text-center">
        <button
          onClick={() => (window.location.href = "/")}
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

export default Payments;
