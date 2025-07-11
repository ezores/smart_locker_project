/**
 * Smart Locker System - Admin Dashboard
 *
 * @author Alp
 * @date 2024-12-XX
 * @description Admin dashboard with statistics, recent activity, and reporting functionality
 */

import React from "react";
import { useState, useEffect } from "react";
import { useLanguage } from "../contexts/LanguageContext";
import { useDarkMode } from "../contexts/DarkModeContext";
import {
  Users,
  Package,
  MapPin,
  Activity,
  TrendingUp,
  Clock,
  User,
  BarChart3,
  ChevronRight,
  ArrowLeft,
  Settings,
} from "lucide-react";
import { getStats, getRecentActivity } from "../utils/api";
import Reports from "../components/Reports";

const AdminDashboard = () => {
  const { t } = useLanguage();
  const { isDarkMode } = useDarkMode();
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalItems: 0,
    totalLockers: 0,
    activeBorrows: 0,
  });
  const [recentActivity, setRecentActivity] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsData, activityData] = await Promise.all([
        getStats(),
        getRecentActivity(),
      ]);
      setStats({
        totalUsers: statsData.total_users || 0,
        totalItems: statsData.total_items || 0,
        totalLockers: statsData.total_lockers || 0,
        activeBorrows: statsData.active_borrows || 0,
      });
      setRecentActivity(activityData || []);
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
      setStats({
        totalUsers: 0,
        totalItems: 0,
        totalLockers: 0,
        activeBorrows: 0,
      });
      setRecentActivity([]);
    } finally {
      setLoading(false);
    }
  };

  const getActivityIcon = (type) => {
    switch (type) {
      case "borrow":
      case "check_out":
        return <Package className="h-4 w-4 text-blue-600" />;
      case "return":
      case "check_in":
        return <Activity className="h-4 w-4 text-green-600" />;
      case "login":
        return <User className="h-4 w-4 text-purple-600" />;
      case "maintenance":
        return <Settings className="h-4 w-4 text-orange-600" />;
      default:
        return <Activity className="h-4 w-4 text-gray-600" />;
    }
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInMinutes = Math.floor((now - date) / (1000 * 60));

    if (diffInMinutes < 1) return t("just_now");
    if (diffInMinutes < 60) return `${diffInMinutes} ${t("minutes_ago")}`;
    if (diffInMinutes < 1440)
      return `${Math.floor(diffInMinutes / 60)} ${t("hours_ago")}`;
    return date.toLocaleDateString();
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
          {t("dashboard")}
        </h1>
        <p className={`${isDarkMode ? "text-gray-300" : "text-gray-600"}`}>
          {t("dashboard_description")}
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="mb-8">
        <nav className="flex space-x-8">
          <button
            onClick={() => setActiveTab("overview")}
            className={`py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === "overview"
                ? isDarkMode
                  ? "border-primary-400 text-primary-400"
                  : "border-primary-500 text-primary-600"
                : isDarkMode
                ? "border-transparent text-gray-300 hover:text-gray-200"
                : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
          >
            {t("overview") || "Overview"}
          </button>
          <button
            onClick={() => setActiveTab("reports")}
            className={`py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === "reports"
                ? isDarkMode
                  ? "border-primary-400 text-primary-400"
                  : "border-primary-500 text-primary-600"
                : isDarkMode
                ? "border-transparent text-gray-300 hover:text-gray-200"
                : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
          >
            {t("reports") || "Reports"}
          </button>
        </nav>
      </div>

      {/* Overview Tab */}
      {activeTab === "overview" && (
        <>
          {/* Statistics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className={`card ${isDarkMode ? "bg-gray-800" : "bg-white"}`}>
              <div className="flex items-center">
                <div className="bg-blue-100 p-3 rounded-lg">
                  <Users className="h-6 w-6 text-blue-600" />
                </div>
                <div className="ml-4">
                  <p
                    className={`text-sm font-medium ${
                      isDarkMode ? "text-gray-300" : "text-gray-600"
                    }`}
                  >
                    {t("total_users")}
                  </p>
                  <p
                    className={`text-2xl font-bold ${
                      isDarkMode ? "text-white" : "text-gray-900"
                    }`}
                  >
                    {stats.totalUsers}
                  </p>
                </div>
              </div>
            </div>

            <div className={`card ${isDarkMode ? "bg-gray-800" : "bg-white"}`}>
              <div className="flex items-center">
                <div className="bg-green-100 p-3 rounded-lg">
                  <Package className="h-6 w-6 text-green-600" />
                </div>
                <div className="ml-4">
                  <p
                    className={`text-sm font-medium ${
                      isDarkMode ? "text-gray-300" : "text-gray-600"
                    }`}
                  >
                    {t("total_items")}
                  </p>
                  <p
                    className={`text-2xl font-bold ${
                      isDarkMode ? "text-white" : "text-gray-900"
                    }`}
                  >
                    {stats.totalItems}
                  </p>
                </div>
              </div>
            </div>

            <div className={`card ${isDarkMode ? "bg-gray-800" : "bg-white"}`}>
              <div className="flex items-center">
                <div className="bg-purple-100 p-3 rounded-lg">
                  <MapPin className="h-6 w-6 text-purple-600" />
                </div>
                <div className="ml-4">
                  <p
                    className={`text-sm font-medium ${
                      isDarkMode ? "text-gray-300" : "text-gray-600"
                    }`}
                  >
                    {t("total_lockers")}
                  </p>
                  <p
                    className={`text-2xl font-bold ${
                      isDarkMode ? "text-white" : "text-gray-900"
                    }`}
                  >
                    {stats.totalLockers}
                  </p>
                </div>
              </div>
            </div>

            <div className={`card ${isDarkMode ? "bg-gray-800" : "bg-white"}`}>
              <div className="flex items-center">
                <div className="bg-orange-100 p-3 rounded-lg">
                  <TrendingUp className="h-6 w-6 text-orange-600" />
                </div>
                <div className="ml-4">
                  <p
                    className={`text-sm font-medium ${
                      isDarkMode ? "text-gray-300" : "text-gray-600"
                    }`}
                  >
                    {t("active_borrows")}
                  </p>
                  <p
                    className={`text-2xl font-bold ${
                      isDarkMode ? "text-white" : "text-gray-900"
                    }`}
                  >
                    {stats.activeBorrows}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className={`card ${isDarkMode ? "bg-gray-800" : "bg-white"}`}>
              <div className="flex items-center justify-between mb-6">
                <h2
                  className={`text-xl font-semibold ${
                    isDarkMode ? "text-white" : "text-gray-900"
                  }`}
                >
                  {t("recent_activity")}
                </h2>
                <Clock className="h-5 w-5 text-gray-400" />
              </div>

              <div className="space-y-4">
                {recentActivity.map((activity) => (
                  <div
                    key={activity.id}
                    className={`flex items-center space-x-3 p-3 rounded-lg ${
                      isDarkMode ? "bg-gray-700" : "bg-gray-50"
                    }`}
                  >
                    {getActivityIcon(activity.action_type)}
                    <div className="flex-1 min-w-0">
                      <p
                        className={`text-sm font-medium ${
                          isDarkMode ? "text-white" : "text-gray-900"
                        }`}
                      >
                        {activity.user_name}
                      </p>
                      <p
                        className={`text-sm ${
                          isDarkMode ? "text-gray-300" : "text-gray-500"
                        }`}
                      >
                        {activity.description || t("unknown")}
                      </p>
                    </div>
                    <div className="text-right">
                      <p
                        className={`text-xs ${
                          isDarkMode ? "text-gray-400" : "text-gray-500"
                        }`}
                      >
                        {formatTimestamp(activity.timestamp)}
                      </p>
                      <span
                        className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          activity.action_type === "return" ||
                          activity.action_type === "check_in"
                            ? "bg-green-100 text-green-800"
                            : "bg-blue-100 text-blue-800"
                        }`}
                      >
                        {activity.action_type}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Actions */}
            <div className={`card ${isDarkMode ? "bg-gray-800" : "bg-white"}`}>
              <div className="flex items-center justify-between mb-6">
                <h2
                  className={`text-xl font-semibold ${
                    isDarkMode ? "text-white" : "text-gray-900"
                  }`}
                >
                  {t("quick_actions") || "Quick Actions"}
                </h2>
                <BarChart3 className="h-5 w-5 text-gray-400" />
              </div>

              <div className="space-y-4">
                <button
                  onClick={() => setActiveTab("reports")}
                  className={`w-full flex items-center justify-between p-4 rounded-lg border transition-colors ${
                    isDarkMode
                      ? "border-gray-600 hover:bg-gray-700"
                      : "border-gray-200 hover:bg-gray-50"
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <BarChart3 className="h-5 w-5 text-blue-600" />
                    <div className="text-left">
                      <p
                        className={`font-medium ${
                          isDarkMode ? "text-white" : "text-gray-900"
                        }`}
                      >
                        {t("generate_report") || "Generate Report"}
                      </p>
                      <p
                        className={`text-sm ${
                          isDarkMode ? "text-gray-300" : "text-gray-500"
                        }`}
                      >
                        {t("view_transactions") ||
                          "View transactions and analytics"}
                      </p>
                    </div>
                  </div>
                  <ChevronRight className="h-4 w-4 text-gray-400" />
                </button>

                <button
                  onClick={() => (window.location.href = "/actifs")}
                  className={`w-full flex items-center justify-between p-4 rounded-lg border transition-colors ${
                    isDarkMode
                      ? "border-gray-600 hover:bg-gray-700"
                      : "border-gray-200 hover:bg-gray-50"
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <Clock className="h-5 w-5 text-orange-600" />
                    <div className="text-left">
                      <p
                        className={`font-medium ${
                          isDarkMode ? "text-white" : "text-gray-900"
                        }`}
                      >
                        {t("active_borrows")}
                      </p>
                      <p
                        className={`text-sm ${
                          isDarkMode ? "text-gray-300" : "text-gray-500"
                        }`}
                      >
                        {t("view_current_borrows")}
                      </p>
                    </div>
                  </div>
                  <ChevronRight className="h-4 w-4 text-gray-400" />
                </button>

                <button
                  onClick={() => (window.location.href = "/logs")}
                  className={`w-full flex items-center justify-between p-4 rounded-lg border transition-colors ${
                    isDarkMode
                      ? "border-gray-600 hover:bg-gray-700"
                      : "border-gray-200 hover:bg-gray-50"
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <Activity className="h-5 w-5 text-purple-600" />
                    <div className="text-left">
                      <p
                        className={`font-medium ${
                          isDarkMode ? "text-white" : "text-gray-900"
                        }`}
                      >
                        {t("system_logs")}
                      </p>
                      <p
                        className={`text-sm ${
                          isDarkMode ? "text-gray-300" : "text-gray-500"
                        }`}
                      >
                        {t("view_activity_logs")}
                      </p>
                    </div>
                  </div>
                  <ChevronRight className="h-4 w-4 text-gray-400" />
                </button>

                <button
                  onClick={() => (window.location.href = "/users")}
                  className={`w-full flex items-center justify-between p-4 rounded-lg border transition-colors ${
                    isDarkMode
                      ? "border-gray-600 hover:bg-gray-700"
                      : "border-gray-200 hover:bg-gray-50"
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <Users className="h-5 w-5 text-green-600" />
                    <div className="text-left">
                      <p
                        className={`font-medium ${
                          isDarkMode ? "text-white" : "text-gray-900"
                        }`}
                      >
                        {t("manage_users")}
                      </p>
                      <p
                        className={`text-sm ${
                          isDarkMode ? "text-gray-300" : "text-gray-500"
                        }`}
                      >
                        {t("add_edit_users")}
                      </p>
                    </div>
                  </div>
                  <ChevronRight className="h-4 w-4 text-gray-400" />
                </button>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Reports Tab */}
      {activeTab === "reports" && <Reports />}

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

export default AdminDashboard;
