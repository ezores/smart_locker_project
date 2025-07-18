/**
 * Smart Locker System - Reports Component
 *
 * @author Alp
 * @date 2024-12-XX
 * @description Admin reporting component with date range selection and export functionality
 */

import { useState, useEffect } from "react";
import { useLanguage } from "../contexts/LanguageContext";
import { useDarkMode } from "../contexts/DarkModeContext";
import {
  Download,
  FileText,
  BarChart3,
  TrendingUp,
  RefreshCw,
} from "lucide-react";
import axios from "axios";

const Reports = () => {
  const { t } = useLanguage();
  const { isDarkMode } = useDarkMode();
  const [dateRange, setDateRange] = useState("week");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [reportType, setReportType] = useState("transactions");
  const [loading, setLoading] = useState(false);
  const [reportData, setReportData] = useState(null);

  // Set default date range on component mount
  useEffect(() => {
    const now = new Date();
    const end = new Date(now);
    let start = new Date(now);

    switch (dateRange) {
      case "day":
        start.setDate(now.getDate() - 1);
        break;
      case "week":
        start.setDate(now.getDate() - 7);
        break;
      case "month":
        start.setMonth(now.getMonth() - 1);
        break;
      case "year":
        start.setFullYear(now.getFullYear() - 1);
        break;
      default:
        start.setDate(now.getDate() - 7);
    }

    setStartDate(start.toISOString().split("T")[0]);
    setEndDate(end.toISOString().split("T")[0]);
  }, [dateRange]);

  const generateReport = async () => {
    setLoading(true);
    try {
      const response = await axios.get("/api/admin/reports", {
        params: {
          type: reportType,
          start_date: startDate,
          end_date: endDate,
          range: dateRange,
        },
      });
      setReportData(response.data);
    } catch (error) {
      console.error("Error generating report:", error);
      // Mock data for demo
      setReportData({
        summary: {
          total_transactions: 45,
          borrows: 28,
          returns: 17,
          unique_users: 12,
          unique_items: 15,
        },
        transactions: [
          {
            id: 1,
            user: "john.doe",
            item: "Laptop",
            action: "borrow",
            timestamp: "2024-12-01T10:30:00Z",
            locker: "A1",
          },
          {
            id: 2,
            user: "jane.smith",
            item: "Projector",
            action: "return",
            timestamp: "2024-12-01T14:20:00Z",
            locker: "B3",
          },
        ],
      });
    } finally {
      setLoading(false);
    }
  };

  const exportReport = async (format) => {
    try {
      const response = await axios.get("/api/admin/export", {
        params: {
          type: reportType,
          format: format,
          start_date: startDate,
          end_date: endDate,
          range: dateRange,
        },
        responseType: "blob",
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      // Map format to correct file extension
      const fileExtensions = {
        csv: "csv",
        excel: "xlsx",
        xlsx: "xlsx", // Keep xlsx as xlsx
        pdf: "pdf",
      };
      const extension = fileExtensions[format] || format;
      link.setAttribute(
        "download",
        `smart_locker_report_${reportType}_${startDate}_${endDate}.${extension}`
      );
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error("Error exporting report:", error);
      alert("Failed to export report. Please try again.");
    }
  };

  const getReportIcon = () => {
    switch (reportType) {
      case "transactions":
        return <BarChart3 className="h-5 w-5" />;
      case "users":
        return <TrendingUp className="h-5 w-5" />;
      case "items":
        return <FileText className="h-5 w-5" />;
      default:
        return <BarChart3 className="h-5 w-5" />;
    }
  };

  return (
    <div className={`card ${isDarkMode ? "bg-gray-800" : "bg-white"}`}>
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          {getReportIcon()}
          <h2
            className={`text-xl font-semibold ${
              isDarkMode ? "text-white" : "text-gray-900"
            }`}
          >
            {t("reports") || "Reports"}
          </h2>
        </div>
        <button
          onClick={generateReport}
          disabled={loading}
          className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            loading ? "opacity-50 cursor-not-allowed" : ""
          } ${
            isDarkMode
              ? "bg-blue-600 text-white hover:bg-blue-700"
              : "bg-primary-600 text-white hover:bg-primary-700"
          }`}
        >
          <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          <span>
            {loading
              ? t("generating") || "Generating..."
              : t("generate") || "Generate"}
          </span>
        </button>
      </div>

      {/* Report Configuration */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {/* Report Type */}
        <div>
          <label
            className={`block text-sm font-medium mb-2 ${
              isDarkMode ? "text-gray-300" : "text-gray-700"
            }`}
          >
            {t("report_type") || "Report Type"}
          </label>
          <select
            value={reportType}
            onChange={(e) => setReportType(e.target.value)}
            className={`w-full px-3 py-2 border rounded-md text-sm ${
              isDarkMode
                ? "bg-gray-700 border-gray-600 text-white"
                : "bg-white border-gray-300 text-gray-900"
            }`}
          >
            <option value="transactions">
              {t("transactions") || "Transactions"}
            </option>
            <option value="users">{t("users") || "Users"}</option>
            <option value="items">{t("items") || "Items"}</option>
          </select>
        </div>

        {/* Date Range */}
        <div>
          <label
            className={`block text-sm font-medium mb-2 ${
              isDarkMode ? "text-gray-300" : "text-gray-700"
            }`}
          >
            {t("date_range") || "Date Range"}
          </label>
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className={`w-full px-3 py-2 border rounded-md text-sm ${
              isDarkMode
                ? "bg-gray-700 border-gray-600 text-white"
                : "bg-white border-gray-300 text-gray-900"
            }`}
          >
            <option value="day">{t("daily") || "Daily"}</option>
            <option value="week">{t("weekly") || "Weekly"}</option>
            <option value="month">{t("monthly") || "Monthly"}</option>
            <option value="year">{t("yearly") || "Yearly"}</option>
          </select>
        </div>

        {/* Start Date */}
        <div>
          <label
            className={`block text-sm font-medium mb-2 ${
              isDarkMode ? "text-gray-300" : "text-gray-700"
            }`}
          >
            {t("start_date") || "Start Date"}
          </label>
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className={`w-full px-3 py-2 border rounded-md text-sm ${
              isDarkMode
                ? "bg-gray-700 border-gray-600 text-white"
                : "bg-white border-gray-300 text-gray-900"
            }`}
          />
        </div>

        {/* End Date */}
        <div>
          <label
            className={`block text-sm font-medium mb-2 ${
              isDarkMode ? "text-gray-300" : "text-gray-700"
            }`}
          >
            {t("end_date") || "End Date"}
          </label>
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className={`w-full px-3 py-2 border rounded-md text-sm ${
              isDarkMode
                ? "bg-gray-700 border-gray-600 text-white"
                : "bg-white border-gray-300 text-gray-900"
            }`}
          />
        </div>
      </div>

      {/* Export Buttons */}
      <div className="flex items-center space-x-4 mb-6">
        <button
          onClick={() => exportReport("csv")}
          className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            isDarkMode
              ? "bg-green-600 text-white hover:bg-green-700"
              : "bg-green-600 text-white hover:bg-green-700"
          }`}
        >
          <FileText className="h-4 w-4" />
          <span>Export as CSV</span>
        </button>
        <button
          onClick={() => exportReport("excel")}
          className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            isDarkMode
              ? "bg-blue-600 text-white hover:bg-blue-700"
              : "bg-blue-600 text-white hover:bg-blue-700"
          }`}
        >
          <FileText className="h-4 w-4" />
          <span>Export as Excel</span>
        </button>
        <button
          onClick={() => exportReport("pdf")}
          className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            isDarkMode
              ? "bg-red-600 text-white hover:bg-red-700"
              : "bg-red-600 text-white hover:bg-red-700"
          }`}
        >
          <FileText className="h-4 w-4" />
          <span>Export as PDF</span>
        </button>
      </div>

      {/* Report Summary */}
      {reportData && (
        <div className="mb-6">
          <h3
            className={`text-lg font-semibold mb-4 ${
              isDarkMode ? "text-white" : "text-gray-900"
            }`}
          >
            {t("summary") || "Summary"}
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div
              className={`p-4 rounded-lg ${
                isDarkMode ? "bg-gray-700" : "bg-gray-50"
              }`}
            >
              <p
                className={`text-sm font-medium ${
                  isDarkMode ? "text-gray-300" : "text-gray-600"
                }`}
              >
                {t("total_transactions") || "Total Transactions"}
              </p>
              <p
                className={`text-2xl font-bold ${
                  isDarkMode ? "text-white" : "text-gray-900"
                }`}
              >
                {reportData.summary?.total_transactions || 0}
              </p>
            </div>
            <div
              className={`p-4 rounded-lg ${
                isDarkMode ? "bg-gray-700" : "bg-gray-50"
              }`}
            >
              <p
                className={`text-sm font-medium ${
                  isDarkMode ? "text-gray-300" : "text-gray-600"
                }`}
              >
                {t("borrows") || "Borrows"}
              </p>
              <p className={`text-2xl font-bold text-blue-600`}>
                {reportData.summary?.borrows || 0}
              </p>
            </div>
            <div
              className={`p-4 rounded-lg ${
                isDarkMode ? "bg-gray-700" : "bg-gray-50"
              }`}
            >
              <p
                className={`text-sm font-medium ${
                  isDarkMode ? "text-gray-300" : "text-gray-600"
                }`}
              >
                {t("returns") || "Returns"}
              </p>
              <p className={`text-2xl font-bold text-green-600`}>
                {reportData.summary?.returns || 0}
              </p>
            </div>
            <div
              className={`p-4 rounded-lg ${
                isDarkMode ? "bg-gray-700" : "bg-gray-50"
              }`}
            >
              <p
                className={`text-sm font-medium ${
                  isDarkMode ? "text-gray-300" : "text-gray-600"
                }`}
              >
                {t("unique_users") || "Unique Users"}
              </p>
              <p
                className={`text-2xl font-bold ${
                  isDarkMode ? "text-white" : "text-gray-900"
                }`}
              >
                {reportData.summary?.unique_users || 0}
              </p>
            </div>
            <div
              className={`p-4 rounded-lg ${
                isDarkMode ? "bg-gray-700" : "bg-gray-50"
              }`}
            >
              <p
                className={`text-sm font-medium ${
                  isDarkMode ? "text-gray-300" : "text-gray-600"
                }`}
              >
                {t("unique_items") || "Unique Items"}
              </p>
              <p
                className={`text-2xl font-bold ${
                  isDarkMode ? "text-white" : "text-gray-900"
                }`}
              >
                {reportData.summary?.unique_items || 0}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Report Data Table */}
      {reportData && reportData.transactions && (
        <div>
          <h3
            className={`text-lg font-semibold mb-4 ${
              isDarkMode ? "text-white" : "text-gray-900"
            }`}
          >
            {t("transaction_details") || "Transaction Details"}
          </h3>
          <div
            className={`overflow-x-auto rounded-lg border ${
              isDarkMode ? "border-gray-600" : "border-gray-200"
            }`}
          >
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
                    {t("item") || "Item"}
                  </th>
                  <th
                    className={`px-6 py-3 text-left text-xs font-medium uppercase tracking-wider ${
                      isDarkMode ? "text-gray-300" : "text-gray-500"
                    }`}
                  >
                    {t("action") || "Action"}
                  </th>
                  <th
                    className={`px-6 py-3 text-left text-xs font-medium uppercase tracking-wider ${
                      isDarkMode ? "text-gray-300" : "text-gray-500"
                    }`}
                  >
                    {t("timestamp") || "Timestamp"}
                  </th>
                  <th
                    className={`px-6 py-3 text-left text-xs font-medium uppercase tracking-wider ${
                      isDarkMode ? "text-gray-300" : "text-gray-500"
                    }`}
                  >
                    {t("locker") || "Locker"}
                  </th>
                </tr>
              </thead>
              <tbody
                className={`divide-y ${
                  isDarkMode
                    ? "divide-gray-600 bg-gray-800"
                    : "divide-gray-200 bg-white"
                }`}
              >
                {reportData.transactions.map((transaction) => (
                  <tr key={transaction.id}>
                    <td
                      className={`px-6 py-4 whitespace-nowrap text-sm ${
                        isDarkMode ? "text-white" : "text-gray-900"
                      }`}
                    >
                      {transaction.user}
                    </td>
                    <td
                      className={`px-6 py-4 whitespace-nowrap text-sm ${
                        isDarkMode ? "text-white" : "text-gray-900"
                      }`}
                    >
                      {transaction.item}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          transaction.action === "borrow"
                            ? "bg-blue-100 text-blue-800"
                            : "bg-green-100 text-green-800"
                        }`}
                      >
                        {transaction.action}
                      </span>
                    </td>
                    <td
                      className={`px-6 py-4 whitespace-nowrap text-sm ${
                        isDarkMode ? "text-gray-300" : "text-gray-500"
                      }`}
                    >
                      {new Date(transaction.timestamp).toLocaleString()}
                    </td>
                    <td
                      className={`px-6 py-4 whitespace-nowrap text-sm ${
                        isDarkMode ? "text-white" : "text-gray-900"
                      }`}
                    >
                      {transaction.locker}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default Reports;
