/**
 * Smart Locker System - Main App Component
 *
 * @author Alp
 * @date 2024-12-XX
 * @description Main application component with routing and dark mode support
 */

import { Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "./contexts/AuthContext";
import { useLanguage } from "./contexts/LanguageContext";
import { useDarkMode } from "./contexts/DarkModeContext";
import Header from "./components/Header";
import Login from "./pages/Login";
import Register from "./pages/Register";
import MainMenu from "./pages/MainMenu";
import Borrow from "./pages/Borrow";
import Return from "./pages/Return";
import AdminDashboard from "./pages/AdminDashboard";
import Users from "./pages/Users";
import Items from "./pages/Items";
import Lockers from "./pages/Lockers";
import Logs from "./pages/Logs";
import Emprunts from "./pages/Emprunts";
import Payments from "./pages/Payments";
import Reservations from "./pages/Reservations";
import ProtectedRoute from "./components/ProtectedRoute";
import AdminRoute from "./components/AdminRoute";

function App() {
  const { user } = useAuth();
  const { currentLanguage } = useLanguage();
  const { isDarkMode } = useDarkMode();

  return (
    <div
      className={`min-h-screen transition-colors duration-200 ${
        isDarkMode ? "bg-gray-900 text-white" : "bg-gray-50 text-gray-900"
      }`}
    >
      <Header />
      <main className="pt-20 pb-8">
        <Routes>
          <Route
            path="/login"
            element={!user ? <Login /> : <Navigate to="/" />}
          />
          <Route
            path="/register"
            element={!user ? <Register /> : <Navigate to="/" />}
          />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <MainMenu />
              </ProtectedRoute>
            }
          />
          <Route
            path="/borrow"
            element={
              <ProtectedRoute>
                <Borrow />
              </ProtectedRoute>
            }
          />
          <Route
            path="/return"
            element={
              <ProtectedRoute>
                <Return />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin"
            element={
              <AdminRoute>
                <AdminDashboard />
              </AdminRoute>
            }
          />
          <Route
            path="/users"
            element={
              <AdminRoute>
                <Users />
              </AdminRoute>
            }
          />
          <Route
            path="/items"
            element={
              <AdminRoute>
                <Items />
              </AdminRoute>
            }
          />
          <Route
            path="/lockers"
            element={
              <AdminRoute>
                <Lockers />
              </AdminRoute>
            }
          />
          <Route
            path="/logs"
            element={
              <AdminRoute>
                <Logs />
              </AdminRoute>
            }
          />
          <Route
            path="/actifs"
            element={
              <AdminRoute>
                <Emprunts />
              </AdminRoute>
            }
          />
          <Route
            path="/payments"
            element={
              <ProtectedRoute>
                <Payments />
              </ProtectedRoute>
            }
          />
          <Route
            path="/reservations"
            element={
              <ProtectedRoute>
                <Reservations />
              </ProtectedRoute>
            }
          />
        </Routes>
      </main>
    </div>
  );
}

export default App;
