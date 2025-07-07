import { useState, useEffect } from "react";
import { useLanguage } from "../contexts/LanguageContext";
import {
  Users,
  Package,
  MapPin,
  Activity,
  TrendingUp,
  Clock,
  User,
  Calendar,
} from "lucide-react";
import axios from "axios";

const AdminDashboard = () => {
  const { t } = useLanguage();
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalItems: 0,
    totalLockers: 0,
    activeBorrows: 0,
  });
  const [recentActivity, setRecentActivity] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsResponse, activityResponse] = await Promise.all([
        axios.get("/api/admin/stats"),
        axios.get("/api/admin/recent-activity"),
      ]);

      setStats(statsResponse.data);
      setRecentActivity(activityResponse.data);
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
      // Use mock data for demo
      setStats({
        totalUsers: 12,
        totalItems: 45,
        totalLockers: 20,
        activeBorrows: 8,
      });
      setRecentActivity([
        {
          id: 1,
          type: "borrow",
          user: "john.doe",
          item: "Laptop",
          timestamp: new Date().toISOString(),
          status: "completed",
        },
        {
          id: 2,
          type: "return",
          user: "jane.smith",
          item: "Projector",
          timestamp: new Date(Date.now() - 3600000).toISOString(),
          status: "completed",
        },
        {
          id: 3,
          type: "borrow",
          user: "mike.wilson",
          item: "Camera",
          timestamp: new Date(Date.now() - 7200000).toISOString(),
          status: "completed",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const getActivityIcon = (type) => {
    switch (type) {
      case "borrow":
        return <Package className="h-4 w-4 text-blue-600" />;
      case "return":
        return <Activity className="h-4 w-4 text-green-600" />;
      default:
        return <Activity className="h-4 w-4 text-gray-600" />;
    }
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInMinutes = Math.floor((now - date) / (1000 * 60));

    if (diffInMinutes < 1) return "Just now";
    if (diffInMinutes < 60) return `${diffInMinutes} minutes ago`;
    if (diffInMinutes < 1440)
      return `${Math.floor(diffInMinutes / 60)} hours ago`;
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
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          {t("dashboard")}
        </h1>
        <p className="text-gray-600">Overview of the Smart Locker System</p>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="card">
          <div className="flex items-center">
            <div className="bg-blue-100 p-3 rounded-lg">
              <Users className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">
                {t("total_users")}
              </p>
              <p className="text-2xl font-bold text-gray-900">
                {stats.totalUsers}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="bg-green-100 p-3 rounded-lg">
              <Package className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">
                {t("total_items")}
              </p>
              <p className="text-2xl font-bold text-gray-900">
                {stats.totalItems}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="bg-purple-100 p-3 rounded-lg">
              <MapPin className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">
                {t("total_lockers")}
              </p>
              <p className="text-2xl font-bold text-gray-900">
                {stats.totalLockers}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="bg-orange-100 p-3 rounded-lg">
              <TrendingUp className="h-6 w-6 text-orange-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">
                {t("active_borrows")}
              </p>
              <p className="text-2xl font-bold text-gray-900">
                {stats.activeBorrows}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">
              {t("recent_activity")}
            </h2>
            <Clock className="h-5 w-5 text-gray-400" />
          </div>

          <div className="space-y-4">
            {recentActivity.map((activity) => (
              <div
                key={activity.id}
                className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg"
              >
                <div className="flex-shrink-0">
                  {getActivityIcon(activity.type)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900">
                    {activity.user}{" "}
                    {activity.type === "borrow" ? "borrowed" : "returned"}{" "}
                    {activity.item}
                  </p>
                  <p className="text-sm text-gray-500">
                    {formatTimestamp(activity.timestamp)}
                  </p>
                </div>
                <div className="flex-shrink-0">
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      activity.status === "completed"
                        ? "bg-green-100 text-green-800"
                        : "bg-yellow-100 text-yellow-800"
                    }`}
                  >
                    {activity.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">
            Quick Actions
          </h2>

          <div className="space-y-4">
            <button className="w-full p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors text-left">
              <div className="flex items-center space-x-3">
                <User className="h-6 w-6 text-primary-600" />
                <div>
                  <h3 className="font-medium text-gray-900">Add New User</h3>
                  <p className="text-sm text-gray-600">
                    Create a new user account
                  </p>
                </div>
              </div>
            </button>

            <button className="w-full p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors text-left">
              <div className="flex items-center space-x-3">
                <Package className="h-6 w-6 text-primary-600" />
                <div>
                  <h3 className="font-medium text-gray-900">Add New Item</h3>
                  <p className="text-sm text-gray-600">
                    Register a new equipment item
                  </p>
                </div>
              </div>
            </button>

            <button className="w-full p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors text-left">
              <div className="flex items-center space-x-3">
                <MapPin className="h-6 w-6 text-primary-600" />
                <div>
                  <h3 className="font-medium text-gray-900">Manage Lockers</h3>
                  <p className="text-sm text-gray-600">
                    Configure locker settings
                  </p>
                </div>
              </div>
            </button>

            <button className="w-full p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors text-left">
              <div className="flex items-center space-x-3">
                <Calendar className="h-6 w-6 text-primary-600" />
                <div>
                  <h3 className="font-medium text-gray-900">View Reports</h3>
                  <p className="text-sm text-gray-600">
                    Generate system reports
                  </p>
                </div>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
