/**
 * Smart Locker System - Logs Management Page
 *
 * @author Alp
 * @date 2024-12-XX
 * @description Logs management interface for administrators
 */

import { useState, useEffect } from "react";
import { useLanguage } from "../contexts/LanguageContext";
import { useDarkMode } from "../contexts/DarkModeContext";
import {
  Activity,
  Search,
  Filter,
  Calendar,
  User,
  Package,
  MapPin,
  Clock,
  Download,
  Eye,
  EyeOff,
  Save,
  X,
  FileText,
  ArrowLeft,
} from "lucide-react";
import axios from "axios";

const Logs = () => {
  const { t } = useLanguage();
  const { isDarkMode } = useDarkMode();
  const [logs, setLogs] = useState([]);
  const [users, setUsers] = useState([]);
  const [items, setItems] = useState([]);
  const [lockers, setLockers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [actionFilter, setActionFilter] = useState("all");
  const [userFilter, setUserFilter] = useState("all");
  const [dateFilter, setDateFilter] = useState("");
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [logsResponse, usersResponse, itemsResponse, lockersResponse] =
        await Promise.all([
          axios.get("/api/logs"),
          axios.get("/api/admin/users"),
          axios.get("/api/items"),
          axios.get("/api/lockers"),
        ]);
      setLogs(logsResponse.data);
      setUsers(usersResponse.data);
      setItems(itemsResponse.data);
      setLockers(lockersResponse.data);
    } catch (error) {
      console.error("Error fetching data:", error);
      setLogs([]);
      setUsers([]);
      setItems([]);
      setLockers([]);
    } finally {
      setLoading(false);
    }
  };

  const filteredLogs = logs.filter((log) => {
    const matchesSearch =
      log.action_type?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.description?.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesAction =
      actionFilter === "all" || log.action_type === actionFilter;
    const matchesUser = userFilter === "all" || log.user_id == userFilter;

    let matchesDate = true;
    if (dateFilter) {
      const logDate = new Date(log.timestamp).toISOString().split("T")[0];
      matchesDate = logDate === dateFilter;
    }

    return matchesSearch && matchesAction && matchesUser && matchesDate;
  });

  const getUserName = (userId) => {
    const user = users.find((u) => u.id === userId);
    return user ? user.username : t("unknown_user");
  };

  const getItemName = (itemId) => {
    const item = items.find((i) => i.id === itemId);
    return item ? item.name : t("unknown_item");
  };

  const getLockerName = (lockerId) => {
    const locker = lockers.find((l) => l.id === lockerId);
    return locker ? locker.name : t("unknown_locker");
  };

  const getActionIcon = (action) => {
    switch (action) {
      case "borrow":
        return <Package className="h-4 w-4 text-blue-600" />;
      case "return":
        return <Activity className="h-4 w-4 text-green-600" />;
      case "login":
        return <User className="h-4 w-4 text-purple-600" />;
      case "logout":
        return <User className="h-4 w-4 text-gray-600" />;
      default:
        return <Activity className="h-4 w-4 text-gray-600" />;
    }
  };

  const getActionBadge = (action) => {
    const actionConfig = {
      borrow: {
        color: "bg-blue-100 text-blue-800",
        text: "Borrow",
      },
      return: {
        color: "bg-green-100 text-green-800",
        text: "Return",
      },
      login: {
        color: "bg-purple-100 text-purple-800",
        text: "Login",
      },
      logout: {
        color: "bg-gray-100 text-gray-800",
        text: "Logout",
      },
    };

    const config = actionConfig[action] || actionConfig.login;

    return (
      <span
        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.color}`}
      >
        {getActionIcon(action)}
        <span className="ml-1">{config.text}</span>
      </span>
    );
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInMinutes = Math.floor((now - date) / (1000 * 60));

    if (diffInMinutes < 1) return t("just_now");
    if (diffInMinutes < 60) return `${diffInMinutes} ${t("minutes_ago")}`;
    if (diffInMinutes < 1440)
      return `${Math.floor(diffInMinutes / 60)} ${t("hours_ago")}`;
    return date.toLocaleDateString() + " " + date.toLocaleTimeString();
  };

  const exportLogs = async (format) => {
    try {
      const response = await axios.get(
        `/api/admin/logs/export?format=${format}`,
        {
          responseType: "blob",
        }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute(
        "download",
        `logs_${new Date().toISOString().split("T")[0]}.${format}`
      );
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error("Error exporting logs:", error);
      alert(t("failed_export_logs"));
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
          {t("logs_title")}
        </h1>
        <p className={`${isDarkMode ? "text-gray-300" : "text-gray-600"}`}>
          {t("logs_description")}
        </p>
      </div>

      {/* Controls */}
      <div className="mb-6 flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center">
        <div className="flex flex-col sm:flex-row gap-4 flex-1">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder={t("search_logs")}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className={`pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                isDarkMode
                  ? "bg-gray-700 border-gray-600 text-white"
                  : "bg-white border-gray-300 text-gray-900"
              }`}
            />
          </div>

          {/* Quick Filters */}
          <select
            value={actionFilter}
            onChange={(e) => setActionFilter(e.target.value)}
            className={`px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
              isDarkMode
                ? "bg-gray-700 border-gray-600 text-white"
                : "bg-white border-gray-300 text-gray-900"
            }`}
          >
            <option value="all">{t("all_actions")}</option>
            <option value="borrow">{t("borrow")}</option>
            <option value="return">{t("return")}</option>
            <option value="login">{t("login")}</option>
            <option value="logout">{t("logout")}</option>
          </select>

          {/* Advanced Filters Button */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`flex items-center space-x-2 px-4 py-2 border rounded-lg ${
              isDarkMode
                ? "border-gray-600 text-gray-300 hover:bg-gray-700"
                : "border-gray-300 text-gray-700 hover:bg-gray-50"
            }`}
          >
            <Filter className="h-4 w-4" />
            <span>{t("filters")}</span>
          </button>
        </div>

        {/* Export Button */}
        <div className="flex space-x-2">
          <button
            onClick={() => exportLogs("csv")}
            className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            <Download className="h-4 w-4" />
            <span>{t("export_csv")}</span>
          </button>
          <button
            onClick={() => exportLogs("excel")}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <FileText className="h-4 w-4" />
            <span>{t("export_excel")}</span>
          </button>
        </div>
      </div>

      {/* Advanced Filters */}
      {showFilters && (
        <div
          className={`mb-6 p-4 rounded-lg border ${
            isDarkMode
              ? "bg-gray-800 border-gray-600"
              : "bg-gray-50 border-gray-200"
          }`}
        >
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label
                className={`block text-sm font-medium mb-2 ${
                  isDarkMode ? "text-white" : "text-gray-700"
                }`}
              >
                {t("user")}
              </label>
              <select
                value={userFilter}
                onChange={(e) => setUserFilter(e.target.value)}
                className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                  isDarkMode
                    ? "bg-gray-700 border-gray-600 text-white"
                    : "bg-white border-gray-300 text-gray-900"
                }`}
              >
                <option value="all">{t("all_users")}</option>
                {users.map((user) => (
                  <option key={user.id} value={user.id}>
                    {user.username}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label
                className={`block text-sm font-medium mb-2 ${
                  isDarkMode ? "text-white" : "text-gray-700"
                }`}
              >
                {t("date")}
              </label>
              <input
                type="date"
                value={dateFilter}
                onChange={(e) => setDateFilter(e.target.value)}
                className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                  isDarkMode
                    ? "bg-gray-700 border-gray-600 text-white"
                    : "bg-white border-gray-300 text-gray-900"
                }`}
              />
            </div>
            <div className="flex items-end">
              <button
                onClick={() => {
                  setUserFilter("all");
                  setDateFilter("");
                  setActionFilter("all");
                }}
                className={`px-4 py-2 border rounded-md ${
                  isDarkMode
                    ? "border-gray-600 text-gray-300 hover:bg-gray-700"
                    : "border-gray-300 text-gray-700 hover:bg-gray-50"
                }`}
              >
                {t("clear_filters")}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Logs Table */}
      <div className={`card ${isDarkMode ? "bg-gray-800" : "bg-white"}`}>
        {filteredLogs.length === 0 ? (
          <div className="text-center py-12">
            <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3
              className={`text-lg font-medium mb-2 ${
                isDarkMode ? "text-white" : "text-gray-900"
              }`}
            >
              {t("no_logs_found")}
            </h3>
            <p className={`${isDarkMode ? "text-gray-300" : "text-gray-600"}`}>
              {searchTerm ||
              actionFilter !== "all" ||
              userFilter !== "all" ||
              dateFilter
                ? t("try_adjusting_search")
                : t("no_activity_logged")}
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
                    Action
                  </th>
                  <th
                    className={`px-6 py-3 text-left text-xs font-medium uppercase tracking-wider ${
                      isDarkMode ? "text-gray-300" : "text-gray-500"
                    }`}
                  >
                    User
                  </th>
                  <th
                    className={`px-6 py-3 text-left text-xs font-medium uppercase tracking-wider ${
                      isDarkMode ? "text-gray-300" : "text-gray-500"
                    }`}
                  >
                    Details
                  </th>
                  <th
                    className={`px-6 py-3 text-left text-xs font-medium uppercase tracking-wider ${
                      isDarkMode ? "text-gray-300" : "text-gray-500"
                    }`}
                  >
                    Timestamp
                  </th>
                </tr>
              </thead>
              <tbody
                className={`divide-y ${
                  isDarkMode ? "divide-gray-700" : "divide-gray-200"
                }`}
              >
                {filteredLogs.map((log) => (
                  <tr
                    key={log.id}
                    className={`${
                      isDarkMode
                        ? "bg-gray-800 hover:bg-gray-700"
                        : "bg-white hover:bg-gray-50"
                    }`}
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getActionBadge(log.action_type)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-8 w-8">
                          <div className="h-8 w-8 rounded-full flex items-center justify-center bg-gray-100">
                            <User className="h-4 w-4 text-gray-600" />
                          </div>
                        </div>
                        <div className="ml-3">
                          <div
                            className={`text-sm font-medium ${
                              isDarkMode ? "text-white" : "text-gray-900"
                            }`}
                          >
                            {getUserName(log.user_id)}
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
                        {log.description || "No description"}
                      </div>
                      {(log.item_id || log.locker_id) && (
                        <div
                          className={`text-xs ${
                            isDarkMode ? "text-gray-400" : "text-gray-500"
                          }`}
                        >
                          {log.item_id && (
                            <span className="inline-flex items-center mr-3">
                              <Package className="h-3 w-3 mr-1" />
                              {getItemName(log.item_id)}
                            </span>
                          )}
                          {log.locker_id && (
                            <span className="inline-flex items-center">
                              <MapPin className="h-3 w-3 mr-1" />
                              {getLockerName(log.locker_id)}
                            </span>
                          )}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <Clock className="h-4 w-4 text-gray-400 mr-2" />
                        <span
                          className={`text-sm ${
                            isDarkMode ? "text-gray-300" : "text-gray-900"
                          }`}
                        >
                          {formatTimestamp(log.timestamp)}
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

export default Logs;
