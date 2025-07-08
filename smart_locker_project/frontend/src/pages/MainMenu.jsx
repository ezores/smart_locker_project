import { Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { useLanguage } from "../contexts/LanguageContext";
import { useDarkMode } from "../contexts/DarkModeContext";
import {
  Package,
  ArrowLeft,
  Settings,
  Users,
  Box,
  Activity,
  User,
  Clock,
} from "lucide-react";
import { useEffect, useState } from "react";
import axios from "axios";

const MainMenu = () => {
  const { user } = useAuth();
  const { t } = useLanguage();
  const { isDarkMode } = useDarkMode();
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalItems: 0,
    totalLockers: 0,
    activeBorrows: 0,
  });

  useEffect(() => {
    if (user.role === "admin") {
      axios.get("/api/admin/stats").then((res) => setStats(res.data));
    }
  }, [user]);

  const menuItems = [
    {
      title: t("borrow_item"),
      description: t("borrow_description"),
      icon: Package,
      href: "/borrow",
      color: "bg-blue-500",
      iconColor: "text-blue-500",
    },
    {
      title: t("return_item"),
      description: t("return_description"),
      icon: ArrowLeft,
      href: "/return",
      color: "bg-green-500",
      iconColor: "text-green-500",
    },
    ...(user.role === "admin"
      ? [
          {
            title: t("admin_panel"),
            description: t("admin_panel_description"),
            icon: Settings,
            href: "/admin",
            color: "bg-purple-500",
            iconColor: "text-purple-500",
          },
          {
            title: t("users"),
            description: t("manage_accounts"),
            icon: Users,
            href: "/users",
            color: "bg-indigo-500",
            iconColor: "text-indigo-500",
          },
          {
            title: t("items"),
            description: t("items_description"),
            icon: Box,
            href: "/items",
            color: "bg-orange-500",
            iconColor: "text-orange-500",
          },
          {
            title: t("lockers"),
            description: t("lockers_description"),
            icon: Activity,
            href: "/lockers",
            color: "bg-red-500",
            iconColor: "text-red-500",
          },
          {
            title: t("logs"),
            description: t("logs_description"),
            icon: Activity,
            href: "/logs",
            color: "bg-gray-500",
            iconColor: "text-gray-500",
          },
          {
            title: t("active_borrows"),
            description: t("active_borrows_menu_description"),
            icon: Clock,
            href: "/actifs",
            color: "bg-teal-500",
            iconColor: "text-teal-500",
          },
        ]
      : []),
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Welcome Section */}
      <div className="text-center mb-12">
        <div className="flex items-center justify-center mb-4">
          <div className="bg-primary-100 p-3 rounded-full">
            <User className="h-8 w-8 text-primary-600" />
          </div>
        </div>
        <h1
          className={`text-4xl font-bold mb-2 ${
            isDarkMode ? "text-white" : "text-gray-900"
          }`}
        >
          {t("welcome")}, {user.username}!
        </h1>
        <p
          className={`text-xl ${
            isDarkMode ? "text-gray-300" : "text-gray-600"
          }`}
        >
          {t("select_option")}
        </p>
      </div>

      {/* Menu Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {menuItems.map((item, index) => {
          const IconComponent = item.icon;
          return (
            <Link key={index} to={item.href} className="group block">
              <div className="card h-full hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 border-2 border-transparent hover:border-primary-200">
                <div className="flex items-start space-x-4">
                  <div className={`p-3 rounded-lg ${item.color} bg-opacity-10`}>
                    <IconComponent className={`h-8 w-8 ${item.iconColor}`} />
                  </div>
                  <div className="flex-1">
                    <h3
                      className={`text-xl font-semibold group-hover:text-primary-600 transition-colors ${
                        isDarkMode ? "text-white" : "text-gray-900"
                      }`}
                    >
                      {item.title}
                    </h3>
                    <p
                      className={`mt-2 ${
                        isDarkMode ? "text-gray-300" : "text-gray-600"
                      }`}
                    >
                      {item.description}
                    </p>
                  </div>
                </div>

                {/* Hover effect indicator */}
                <div className="mt-4 flex items-center text-primary-600 opacity-0 group-hover:opacity-100 transition-opacity">
                  <span className="text-sm font-medium">Get started</span>
                  <ArrowLeft className="h-4 w-4 ml-1 transform rotate-180" />
                </div>
              </div>
            </Link>
          );
        })}
      </div>

      {/* Quick Stats for Admin */}
      {user.role === "admin" && (
        <div className="mt-12">
          <h2
            className={`text-2xl font-bold mb-6 ${
              isDarkMode ? "text-white" : "text-gray-900"
            }`}
          >
            {t("quick_overview")}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="card text-center">
              <div className="text-3xl font-bold text-primary-600">
                {stats.totalUsers}
              </div>
              <div
                className={`${isDarkMode ? "text-gray-300" : "text-gray-600"}`}
              >
                {t("total_users")}
              </div>
            </div>
            <div className="card text-center">
              <div className="text-3xl font-bold text-green-600">
                {stats.totalItems}
              </div>
              <div
                className={`${isDarkMode ? "text-gray-300" : "text-gray-600"}`}
              >
                {t("total_items")}
              </div>
            </div>
            <div className="card text-center">
              <div className="text-3xl font-bold text-blue-600">
                {stats.totalLockers}
              </div>
              <div
                className={`${isDarkMode ? "text-gray-300" : "text-gray-600"}`}
              >
                {t("total_lockers")}
              </div>
            </div>
            <div className="card text-center">
              <div className="text-3xl font-bold text-orange-600">
                {stats.activeBorrows}
              </div>
              <div
                className={`${isDarkMode ? "text-gray-300" : "text-gray-600"}`}
              >
                {t("active_borrows")}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MainMenu;
