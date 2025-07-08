/**
 * Smart Locker System - Lockers Management Page
 *
 * @author Alp
 * @date 2024-12-XX
 * @description Lockers management interface for administrators
 */

import { useState, useEffect } from "react";
import { useLanguage } from "../contexts/LanguageContext";
import { useDarkMode } from "../contexts/DarkModeContext";
import {
  MapPin,
  Plus,
  Edit,
  Trash2,
  Search,
  Package,
  Eye,
  EyeOff,
  Save,
  X,
  Lock,
  Unlock,
  ArrowLeft,
} from "lucide-react";
import axios from "axios";

const Lockers = () => {
  const { t } = useLanguage();
  const { isDarkMode } = useDarkMode();
  const [lockers, setLockers] = useState([]);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingLocker, setEditingLocker] = useState(null);
  const [formData, setFormData] = useState({
    name: "",
    location: "",
    status: "available",
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [lockersResponse, itemsResponse] = await Promise.all([
        axios.get("/api/lockers"),
        axios.get("/api/items"),
      ]);
      setLockers(lockersResponse.data);
      setItems(itemsResponse.data);
    } catch (error) {
      console.error("Error fetching data:", error);
      setLockers([]);
      setItems([]);
    } finally {
      setLoading(false);
    }
  };

  const handleAddLocker = async (e) => {
    e.preventDefault();
    try {
      await axios.post("/api/admin/lockers", formData);
      setShowAddModal(false);
      setFormData({ name: "", location: "", status: "available" });
      fetchData();
    } catch (error) {
      console.error("Error adding locker:", error);
      alert("Failed to add locker");
    }
  };

  const handleEditLocker = async (e) => {
    e.preventDefault();
    try {
      await axios.put(`/api/admin/lockers/${editingLocker.id}`, formData);
      setEditingLocker(null);
      setFormData({ name: "", location: "", status: "available" });
      fetchData();
    } catch (error) {
      console.error("Error updating locker:", error);
      alert("Failed to update locker");
    }
  };

  const handleDeleteLocker = async (lockerId) => {
    if (!confirm("Are you sure you want to delete this locker?")) return;

    try {
      await axios.delete(`/api/admin/lockers/${lockerId}`);
      fetchData();
    } catch (error) {
      console.error("Error deleting locker:", error);
      alert("Failed to delete locker");
    }
  };

  const openEditModal = (locker) => {
    setEditingLocker(locker);
    setFormData({
      name: locker.name,
      location: locker.location || "",
      status: locker.status || "available",
    });
  };

  const closeModal = () => {
    setShowAddModal(false);
    setEditingLocker(null);
    setFormData({ name: "", location: "", status: "available" });
  };

  const filteredLockers = lockers.filter((locker) => {
    const lockerName = locker.name || locker.number || "";
    const matchesSearch = lockerName
      .toLowerCase()
      .includes(searchTerm.toLowerCase());
    const matchesStatus =
      statusFilter === "all" || locker.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getItemsInLocker = (lockerId) => {
    return items.filter((item) => item.locker_id === lockerId);
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      available: {
        color: "bg-green-100 text-green-800",
        icon: <Unlock className="h-3 w-3" />,
        text: t("available"),
      },
      occupied: {
        color: "bg-red-100 text-red-800",
        icon: <Lock className="h-3 w-3" />,
        text: t("occupied"),
      },
      maintenance: {
        color: "bg-yellow-100 text-yellow-800",
        icon: <Package className="h-3 w-3" />,
        text: t("maintenance"),
      },
    };

    const config = statusConfig[status] || statusConfig.available;

    return (
      <span
        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.color}`}
      >
        {config.icon}
        <span className="ml-1">{config.text}</span>
      </span>
    );
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
          {t("lockers_management")}
        </h1>
        <p className={`${isDarkMode ? "text-gray-300" : "text-gray-600"}`}>
          {t("lockers_management_description")}
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
              placeholder={t("search_lockers")}
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
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className={`px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
              isDarkMode
                ? "bg-gray-700 border-gray-600 text-white"
                : "bg-white border-gray-300 text-gray-900"
            }`}
          >
            <option value="all">{t("all_status")}</option>
            <option value="available">{t("available")}</option>
            <option value="occupied">{t("occupied")}</option>
            <option value="maintenance">{t("maintenance")}</option>
          </select>
        </div>

        {/* Add Locker Button */}
        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          <Plus className="h-4 w-4" />
          <span>{t("add_locker")}</span>
        </button>
      </div>

      {/* Lockers Table */}
      <div className={`card ${isDarkMode ? "bg-gray-800" : "bg-white"}`}>
        {filteredLockers.length === 0 ? (
          <div className="text-center py-12">
            <MapPin className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3
              className={`text-lg font-medium mb-2 ${
                isDarkMode ? "text-white" : "text-gray-900"
              }`}
            >
              {t("no_lockers_found")}
            </h3>
            <p className={`${isDarkMode ? "text-gray-300" : "text-gray-600"}`}>
              {searchTerm || statusFilter !== "all"
                ? t("try_adjusting_search")
                : t("get_started_adding_locker")}
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
                    {t("locker") || "Locker"}
                  </th>
                  <th
                    className={`px-6 py-3 text-left text-xs font-medium uppercase tracking-wider ${
                      isDarkMode ? "text-gray-300" : "text-gray-500"
                    }`}
                  >
                    {t("location") || "Location"}
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
                    {t("items") || "Items"}
                  </th>
                  <th
                    className={`px-6 py-3 text-left text-xs font-medium uppercase tracking-wider ${
                      isDarkMode ? "text-gray-300" : "text-gray-500"
                    }`}
                  >
                    {t("actions") || "Actions"}
                  </th>
                </tr>
              </thead>
              <tbody
                className={`divide-y ${
                  isDarkMode ? "divide-gray-700" : "divide-gray-200"
                }`}
              >
                {filteredLockers.map((locker) => {
                  const itemsInLocker = getItemsInLocker(locker.id);
                  return (
                    <tr
                      key={locker.id}
                      className={`${
                        isDarkMode
                          ? "bg-gray-800 hover:bg-gray-700"
                          : "bg-white hover:bg-gray-50"
                      }`}
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10">
                            <div className="h-10 w-10 rounded-full flex items-center justify-center bg-purple-100">
                              <MapPin className="h-4 w-4 text-purple-600" />
                            </div>
                          </div>
                          <div className="ml-4">
                            <div
                              className={`text-sm font-medium ${
                                isDarkMode ? "text-white" : "text-gray-900"
                              }`}
                            >
                              {locker.name || locker.number}
                            </div>
                            <div
                              className={`text-sm ${
                                isDarkMode ? "text-gray-300" : "text-gray-500"
                              }`}
                            >
                              ID: {locker.id}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`text-sm ${
                            isDarkMode ? "text-gray-300" : "text-gray-900"
                          }`}
                        >
                          {locker.location ||
                            t("not_specified") ||
                            "Not specified"}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getStatusBadge(locker.status)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <Package className="h-4 w-4 text-gray-400 mr-2" />
                          <span
                            className={`text-sm ${
                              isDarkMode ? "text-gray-300" : "text-gray-900"
                            }`}
                          >
                            {itemsInLocker.length} {t("items") || "items"}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex space-x-2">
                          <button
                            onClick={() => openEditModal(locker)}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            <Edit className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => handleDeleteLocker(locker.id)}
                            className="text-red-600 hover:text-red-900"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Add Locker Modal */}
      {showAddModal && (
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
                {t("add_new_locker") || "Add New Locker"}
              </h3>
              <button
                onClick={closeModal}
                className={`p-1 rounded-md ${
                  isDarkMode
                    ? "text-gray-400 hover:text-white"
                    : "text-gray-400 hover:text-gray-600"
                }`}
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <form onSubmit={handleAddLocker} className="p-6 space-y-4">
              <div>
                <label
                  className={`block text-sm font-medium mb-2 ${
                    isDarkMode ? "text-white" : "text-gray-700"
                  }`}
                >
                  Locker Name
                </label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                  className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                    isDarkMode
                      ? "bg-gray-700 border-gray-600 text-white"
                      : "bg-white border-gray-300 text-gray-900"
                  }`}
                />
              </div>
              <div>
                <label
                  className={`block text-sm font-medium mb-2 ${
                    isDarkMode ? "text-white" : "text-gray-700"
                  }`}
                >
                  {t("location") || "Location"}
                </label>
                <input
                  type="text"
                  value={formData.location}
                  onChange={(e) =>
                    setFormData({ ...formData, location: e.target.value })
                  }
                  placeholder="e.g., Building A, Floor 2"
                  className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                    isDarkMode
                      ? "bg-gray-700 border-gray-600 text-white"
                      : "bg-white border-gray-300 text-gray-900"
                  }`}
                />
              </div>
              <div>
                <label
                  className={`block text-sm font-medium mb-2 ${
                    isDarkMode ? "text-white" : "text-gray-700"
                  }`}
                >
                  {t("status") || "Status"}
                </label>
                <select
                  value={formData.status}
                  onChange={(e) =>
                    setFormData({ ...formData, status: e.target.value })
                  }
                  className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                    isDarkMode
                      ? "bg-gray-700 border-gray-600 text-white"
                      : "bg-white border-gray-300 text-gray-900"
                  }`}
                >
                  <option value="available">
                    {t("available") || "Available"}
                  </option>
                  <option value="occupied">
                    {t("occupied") || "Occupied"}
                  </option>
                  <option value="maintenance">
                    {t("maintenance") || "Maintenance"}
                  </option>
                </select>
              </div>
              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={closeModal}
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
                  className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
                >
                  {t("add_locker") || "Add Locker"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Locker Modal */}
      {editingLocker && (
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
                {t("edit_locker") || "Edit Locker"}
              </h3>
              <button
                onClick={closeModal}
                className={`p-1 rounded-md ${
                  isDarkMode
                    ? "text-gray-400 hover:text-white"
                    : "text-gray-400 hover:text-gray-600"
                }`}
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <form onSubmit={handleEditLocker} className="p-6 space-y-4">
              <div>
                <label
                  className={`block text-sm font-medium mb-2 ${
                    isDarkMode ? "text-white" : "text-gray-700"
                  }`}
                >
                  Locker Name
                </label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                  className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                    isDarkMode
                      ? "bg-gray-700 border-gray-600 text-white"
                      : "bg-white border-gray-300 text-gray-900"
                  }`}
                />
              </div>
              <div>
                <label
                  className={`block text-sm font-medium mb-2 ${
                    isDarkMode ? "text-white" : "text-gray-700"
                  }`}
                >
                  {t("location") || "Location"}
                </label>
                <input
                  type="text"
                  value={formData.location}
                  onChange={(e) =>
                    setFormData({ ...formData, location: e.target.value })
                  }
                  placeholder="e.g., Building A, Floor 2"
                  className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                    isDarkMode
                      ? "bg-gray-700 border-gray-600 text-white"
                      : "bg-white border-gray-300 text-gray-900"
                  }`}
                />
              </div>
              <div>
                <label
                  className={`block text-sm font-medium mb-2 ${
                    isDarkMode ? "text-white" : "text-gray-700"
                  }`}
                >
                  Status
                </label>
                <select
                  value={formData.status}
                  onChange={(e) =>
                    setFormData({ ...formData, status: e.target.value })
                  }
                  className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                    isDarkMode
                      ? "bg-gray-700 border-gray-600 text-white"
                      : "bg-white border-gray-300 text-gray-900"
                  }`}
                >
                  <option value="available">
                    {t("available") || "Available"}
                  </option>
                  <option value="occupied">
                    {t("occupied") || "Occupied"}
                  </option>
                  <option value="maintenance">
                    {t("maintenance") || "Maintenance"}
                  </option>
                </select>
              </div>
              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={closeModal}
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
                  className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
                >
                  {t("save_changes") || "Save Changes"}
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

export default Lockers;
