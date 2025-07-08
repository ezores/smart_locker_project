/**
 * Smart Locker System - Active Borrows (Emprunts) Management Page
 *
 * @author Alp
 * @date 2024-12-XX
 * @description Active borrows management interface for administrators
 */

import { useState, useEffect } from "react";
import { useLanguage } from "../contexts/LanguageContext";
import { useDarkMode } from "../contexts/DarkModeContext";
import {
  Package,
  Search,
  Filter,
  Calendar,
  User,
  MapPin,
  Clock,
  Eye,
  EyeOff,
  Save,
  X,
  FileText,
  ArrowLeft,
  CheckCircle,
  AlertCircle,
} from "lucide-react";
import axios from "axios";

const Emprunts = () => {
  const { t } = useLanguage();
  const { isDarkMode } = useDarkMode();
  const [borrows, setBorrows] = useState([]);
  const [users, setUsers] = useState([]);
  const [items, setItems] = useState([]);
  const [lockers, setLockers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [userFilter, setUserFilter] = useState("all");
  const [itemFilter, setItemFilter] = useState("all");
  const [dateFilter, setDateFilter] = useState("");
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [borrowsResponse, usersResponse, itemsResponse, lockersResponse] =
        await Promise.all([
          axios.get("/api/admin/active-borrows"),
          axios.get("/api/admin/users"),
          axios.get("/api/items"),
          axios.get("/api/lockers"),
        ]);
      setBorrows(borrowsResponse.data);
      setUsers(usersResponse.data);
      setItems(itemsResponse.data);
      setLockers(lockersResponse.data);
    } catch (error) {
      console.error("Error fetching data:", error);
      setBorrows([]);
      setUsers([]);
      setItems([]);
      setLockers([]);
    } finally {
      setLoading(false);
    }
  };

  const filteredBorrows = borrows.filter((borrow) => {
    const matchesSearch =
      borrow.user_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      borrow.item_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      borrow.locker_name?.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesUser = userFilter === "all" || borrow.user_id == userFilter;
    const matchesItem = itemFilter === "all" || borrow.item_id == itemFilter;

    let matchesDate = true;
    if (dateFilter) {
      const borrowDate = new Date(borrow.borrowed_at)
        .toISOString()
        .split("T")[0];
      matchesDate = borrowDate === dateFilter;
    }

    return matchesSearch && matchesUser && matchesItem && matchesDate;
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

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleDateString() + " " + date.toLocaleTimeString();
  };

  const getDuration = (borrowedAt) => {
    const borrowed = new Date(borrowedAt);
    const now = new Date();
    const diffInHours = Math.floor((now - borrowed) / (1000 * 60 * 60));
    const diffInDays = Math.floor(diffInHours / 24);

    if (diffInDays > 0) {
      return `${diffInDays} ${t("days")}`;
    } else if (diffInHours > 0) {
      return `${diffInHours} ${t("hours")}`;
    } else {
      return t("less_than_hour");
    }
  };

  const exportBorrows = async (format) => {
    try {
      const response = await axios.get(
        `/api/admin/borrows/export?format=${format}`,
        {
          responseType: "blob",
        }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute(
        "download",
        `active_borrows_${new Date().toISOString().split("T")[0]}.${format}`
      );
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error("Error exporting borrows:", error);
      alert(t("failed_export_borrows"));
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
          {t("active_borrows")}
        </h1>
        <p className={`${isDarkMode ? "text-gray-300" : "text-gray-600"}`}>
          {t("active_borrows_description")}
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
              placeholder={t("search_borrows")}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className={`pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                isDarkMode
                  ? "bg-gray-700 border-gray-600 text-white"
                  : "bg-white border-gray-300 text-gray-900"
              }`}
            />
          </div>

          {/* Filter Toggle */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`flex items-center space-x-2 px-4 py-2 border rounded-lg transition-colors ${
              isDarkMode
                ? "bg-gray-700 border-gray-600 text-white hover:bg-gray-600"
                : "bg-white border-gray-300 text-gray-700 hover:bg-gray-50"
            }`}
          >
            <Filter className="h-4 w-4" />
            <span>{t("filters")}</span>
            {showFilters ? (
              <EyeOff className="h-4 w-4" />
            ) : (
              <Eye className="h-4 w-4" />
            )}
          </button>
        </div>

        {/* Export Button */}
        <div className="flex space-x-2">
          <button
            onClick={() => exportBorrows("csv")}
            className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            <FileText className="h-4 w-4" />
            <span>CSV</span>
          </button>
          <button
            onClick={() => exportBorrows("xlsx")}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <FileText className="h-4 w-4" />
            <span>Excel</span>
          </button>
          <button
            onClick={() => exportBorrows("pdf")}
            className="flex items-center space-x-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            <FileText className="h-4 w-4" />
            <span>PDF</span>
          </button>
        </div>
      </div>

      {/* Filters */}
      {showFilters && (
        <div
          className={`mb-6 p-4 rounded-lg ${
            isDarkMode ? "bg-gray-700" : "bg-gray-50"
          }`}
        >
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* User Filter */}
            <div>
              <label
                className={`block text-sm font-medium mb-2 ${
                  isDarkMode ? "text-gray-300" : "text-gray-700"
                }`}
              >
                {t("filter_by_user")}
              </label>
              <select
                value={userFilter}
                onChange={(e) => setUserFilter(e.target.value)}
                className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                  isDarkMode
                    ? "bg-gray-600 border-gray-500 text-white"
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

            {/* Item Filter */}
            <div>
              <label
                className={`block text-sm font-medium mb-2 ${
                  isDarkMode ? "text-gray-300" : "text-gray-700"
                }`}
              >
                {t("filter_by_item")}
              </label>
              <select
                value={itemFilter}
                onChange={(e) => setItemFilter(e.target.value)}
                className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                  isDarkMode
                    ? "bg-gray-600 border-gray-500 text-white"
                    : "bg-white border-gray-300 text-gray-900"
                }`}
              >
                <option value="all">{t("all_items")}</option>
                {items.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Date Filter */}
            <div>
              <label
                className={`block text-sm font-medium mb-2 ${
                  isDarkMode ? "text-gray-300" : "text-gray-700"
                }`}
              >
                {t("filter_by_date")}
              </label>
              <input
                type="date"
                value={dateFilter}
                onChange={(e) => setDateFilter(e.target.value)}
                className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                  isDarkMode
                    ? "bg-gray-600 border-gray-500 text-white"
                    : "bg-white border-gray-300 text-gray-900"
                }`}
              />
            </div>
          </div>
        </div>
      )}

      {/* Results Count */}
      <div className="mb-4">
        <p className={`${isDarkMode ? "text-gray-300" : "text-gray-600"}`}>
          {t("showing")} {filteredBorrows.length} {t("of")} {borrows.length}{" "}
          {t("active_borrows")}
        </p>
      </div>

      {/* Borrows Table */}
      <div
        className={`overflow-hidden rounded-lg border ${
          isDarkMode ? "border-gray-600" : "border-gray-200"
        }`}
      >
        <div
          className={`overflow-x-auto ${
            isDarkMode ? "bg-gray-800" : "bg-white"
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
                  {t("user")}
                </th>
                <th
                  className={`px-6 py-3 text-left text-xs font-medium uppercase tracking-wider ${
                    isDarkMode ? "text-gray-300" : "text-gray-500"
                  }`}
                >
                  {t("item")}
                </th>
                <th
                  className={`px-6 py-3 text-left text-xs font-medium uppercase tracking-wider ${
                    isDarkMode ? "text-gray-300" : "text-gray-500"
                  }`}
                >
                  {t("locker")}
                </th>
                <th
                  className={`px-6 py-3 text-left text-xs font-medium uppercase tracking-wider ${
                    isDarkMode ? "text-gray-300" : "text-gray-500"
                  }`}
                >
                  {t("borrowed_at")}
                </th>
                <th
                  className={`px-6 py-3 text-left text-xs font-medium uppercase tracking-wider ${
                    isDarkMode ? "text-gray-300" : "text-gray-500"
                  }`}
                >
                  {t("duration")}
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
              {filteredBorrows.map((borrow) => (
                <tr
                  key={borrow.id}
                  className={`hover:${
                    isDarkMode ? "bg-gray-700" : "bg-gray-50"
                  }`}
                >
                  <td
                    className={`px-6 py-4 whitespace-nowrap ${
                      isDarkMode ? "text-white" : "text-gray-900"
                    }`}
                  >
                    <div className="flex items-center">
                      <User className="h-5 w-5 text-gray-400 mr-2" />
                      {getUserName(borrow.user_id)}
                    </div>
                  </td>
                  <td
                    className={`px-6 py-4 whitespace-nowrap ${
                      isDarkMode ? "text-white" : "text-gray-900"
                    }`}
                  >
                    <div className="flex items-center">
                      <Package className="h-5 w-5 text-blue-500 mr-2" />
                      {getItemName(borrow.item_id)}
                    </div>
                  </td>
                  <td
                    className={`px-6 py-4 whitespace-nowrap ${
                      isDarkMode ? "text-white" : "text-gray-900"
                    }`}
                  >
                    <div className="flex items-center">
                      <MapPin className="h-5 w-5 text-green-500 mr-2" />
                      {getLockerName(borrow.locker_id)}
                    </div>
                  </td>
                  <td
                    className={`px-6 py-4 whitespace-nowrap ${
                      isDarkMode ? "text-gray-300" : "text-gray-500"
                    }`}
                  >
                    <div className="flex items-center">
                      <Clock className="h-4 w-4 text-gray-400 mr-2" />
                      {formatTimestamp(borrow.borrowed_at)}
                    </div>
                  </td>
                  <td
                    className={`px-6 py-4 whitespace-nowrap ${
                      isDarkMode ? "text-gray-300" : "text-gray-500"
                    }`}
                  >
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        isDarkMode
                          ? "bg-blue-900 text-blue-200"
                          : "bg-blue-100 text-blue-800"
                      }`}
                    >
                      {getDuration(borrow.borrowed_at)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Empty State */}
      {filteredBorrows.length === 0 && (
        <div className="text-center py-12">
          <Package className="mx-auto h-12 w-12 text-gray-400" />
          <h3
            className={`mt-2 text-sm font-medium ${
              isDarkMode ? "text-gray-300" : "text-gray-900"
            }`}
          >
            {t("no_active_borrows")}
          </h3>
          <p
            className={`mt-1 text-sm ${
              isDarkMode ? "text-gray-400" : "text-gray-500"
            }`}
          >
            {t("no_active_borrows_description")}
          </p>
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

export default Emprunts;
