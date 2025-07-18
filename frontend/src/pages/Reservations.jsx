import React, { useState, useEffect, useContext } from "react";
import { useAuth } from "../contexts/AuthContext";
import { useLanguage } from "../contexts/LanguageContext";
import { useDarkMode } from "../contexts/DarkModeContext";
import api from "../utils/api";
import Calendar from "react-calendar";
import "react-calendar/dist/Calendar.css";

// Add custom CSS for datetime inputs in dark mode
const darkModeStyles = `
  input[type="datetime-local"]::-webkit-calendar-picker-indicator {
    filter: invert(1);
  }
  input[type="datetime-local"]::-webkit-inner-spin-button {
    filter: invert(1);
  }
  input[type="datetime-local"]::-webkit-clear-button {
    filter: invert(1);
  }
`;

// Helper to format a date string or Date object to 'YYYY-MM-DDTHH:mm' for datetime-local input
function toDatetimeLocal(dt) {
  if (!dt) return "";
  const date = typeof dt === "string" ? new Date(dt) : dt;
  // Pad with zeros
  const pad = (n) => n.toString().padStart(2, "0");
  // Use local time for datetime-local inputs
  return (
    date.getFullYear() +
    "-" +
    pad(date.getMonth() + 1) +
    "-" +
    pad(date.getDate()) +
    "T" +
    pad(date.getHours()) +
    ":" +
    pad(date.getMinutes())
  );
}

const Reservations = () => {
  const { user } = useAuth();
  const { t } = useLanguage();
  const { isDarkMode } = useDarkMode();

  // Add dark mode styles to head
  useEffect(() => {
    if (isDarkMode) {
      const style = document.createElement("style");
      style.textContent = darkModeStyles;
      document.head.appendChild(style);
      return () => {
        document.head.removeChild(style);
      };
    }
  }, [isDarkMode]);

  const [reservations, setReservations] = useState([]);
  const [lockers, setLockers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedReservation, setSelectedReservation] = useState(null);
  const [filterStatus, setFilterStatus] = useState("");
  const [exportLoading, setExportLoading] = useState(false);

  // Form state for create/edit
  const [formData, setFormData] = useState({
    locker_id: "",
    start_time: "",
    end_time: "",
    notes: "",
  });

  useEffect(() => {
    fetchReservations();
    fetchLockers();
  }, [filterStatus]);

  // Debug effect to log lockers when they change
  useEffect(() => {
    console.log("Lockers updated:", lockers);
    console.log(
      "Active lockers:",
      lockers.filter((l) => l.status === "active")
    );
    console.log(
      "All locker statuses:",
      lockers.map((l) => l.status)
    );
  }, [lockers]);

  const fetchReservations = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (filterStatus) {
        params.append("status", filterStatus);
      }

      const response = await api.get(`/reservations?${params.toString()}`);
      setReservations(response.data.reservations || []);
    } catch (err) {
      setError(err.response?.data?.error || "Failed to fetch reservations");
    } finally {
      setLoading(false);
    }
  };

  const fetchLockers = async () => {
    try {
      console.log("Fetching lockers...");
      console.log("Auth token:", localStorage.getItem("token"));
      const response = await api.get("/lockers");
      console.log("Raw response:", response);
      // The backend returns the array directly, not wrapped in a 'lockers' property
      const lockersData = response.data || [];
      console.log("Fetched lockers:", lockersData);
      setLockers(lockersData);
    } catch (err) {
      console.error("Failed to fetch lockers:", err);
      console.error("Error details:", err.response?.data);
      console.error("Error status:", err.response?.status);
      if (err.response?.status === 401) {
        console.error("Authentication failed - user not logged in");
      }
    }
  };

  // Fix time comparison to handle datetime-local format properly
  const isStartTimeInPast = (startTime) => {
    if (!startTime) return false;
    const now = new Date();
    const start = new Date(startTime);
    // Add 1 minute buffer to account for timezone differences and clock drift
    const buffer = new Date(now.getTime() + 60000); // 1 minute buffer
    return start.getTime() < buffer.getTime();
  };

  // Convert local datetime to UTC for API calls (preserve local time)
  const localToUTC = (localDateTime) => {
    if (!localDateTime) return null;
    // Create a date object from the local datetime string
    // This preserves the local time without timezone conversion
    const [datePart, timePart] = localDateTime.split("T");
    const [year, month, day] = datePart.split("-");
    const [hour, minute] = timePart.split(":");

    // Create date in local timezone
    const localDate = new Date(year, month - 1, day, hour, minute);

    // Convert to ISO string but preserve the local time
    const offset = localDate.getTimezoneOffset() * 60000; // offset in milliseconds
    const utcDate = new Date(localDate.getTime() - offset);
    return utcDate.toISOString();
  };

  // Convert UTC datetime to local for display
  const utcToLocal = (utcDateTime) => {
    if (!utcDateTime) return null;
    const date = new Date(utcDateTime);
    return toDatetimeLocal(date);
  };

  const handleCreateReservation = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);

      // Convert local times to UTC for API
      const reservationData = {
        ...formData,
        start_time: localToUTC(formData.start_time),
        end_time: localToUTC(formData.end_time),
      };

      const response = await api.post("/reservations", reservationData);
      setReservations((prev) => [response.data.reservation, ...prev]);
      setShowCreateModal(false);
      // Set default start time to current time + 1 hour
      const defaultStartTime = new Date();
      defaultStartTime.setHours(defaultStartTime.getHours() + 1);
      defaultStartTime.setMinutes(0, 0, 0); // Round to nearest hour
      setFormData({
        locker_id: "",
        start_time: toDatetimeLocal(defaultStartTime),
        end_time: "",
        notes: "",
      });
      setError("");
    } catch (err) {
      setError(err.response?.data?.error || "Failed to create reservation");
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateReservation = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);

      // Convert local times to UTC for API
      const reservationData = {
        ...formData,
        start_time: localToUTC(formData.start_time),
        end_time: localToUTC(formData.end_time),
      };

      const response = await api.put(
        `/reservations/${selectedReservation.id}`,
        reservationData
      );
      setReservations((prev) =>
        prev.map((res) =>
          res.id === selectedReservation.id ? response.data.reservation : res
        )
      );
      setShowEditModal(false);
      setSelectedReservation(null);
      // Set default start time to current time + 1 hour
      const defaultStartTime2 = new Date();
      defaultStartTime2.setHours(defaultStartTime2.getHours() + 1);
      defaultStartTime2.setMinutes(0, 0, 0); // Round to nearest hour
      setFormData({
        locker_id: "",
        start_time: toDatetimeLocal(defaultStartTime2),
        end_time: "",
        notes: "",
      });
      setError("");
    } catch (err) {
      setError(err.response?.data?.error || "Failed to update reservation");
    } finally {
      setLoading(false);
    }
  };

  const handleCancelReservation = async (reservationId) => {
    if (!window.confirm(t("reservations.confirmCancel"))) return;

    try {
      setLoading(true);
      const response = await api.post(`/reservations/${reservationId}/cancel`);
      setReservations((prev) =>
        prev.map((res) =>
          res.id === reservationId ? response.data.reservation : res
        )
      );
      setError("");
    } catch (err) {
      setError(err.response?.data?.error || "Failed to cancel reservation");
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format) => {
    try {
      setExportLoading(true);
      const params = new URLSearchParams();
      params.append("format", format);
      if (filterStatus) {
        params.append("status", filterStatus);
      }

      const response = await api.get(
        `/admin/export/reservations?${params.toString()}`,
        {
          responseType: "blob",
        }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute(
        "download",
        `reservations_${new Date().toISOString().split("T")[0]}.${format}`
      );
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      setError("Failed to export reservations");
    } finally {
      setExportLoading(false);
    }
  };

  const openCreateModal = () => {
    // Set default start time to current time + 1 hour
    const defaultStartTime = new Date();
    defaultStartTime.setHours(defaultStartTime.getHours() + 1);
    defaultStartTime.setMinutes(0, 0, 0); // Round to nearest hour

    setFormData({
      locker_id: "",
      start_time: toDatetimeLocal(defaultStartTime),
      end_time: "",
      notes: "",
    });
    setShowCreateModal(true);
    setError("");
  };

  const openEditModal = (reservation) => {
    console.log("Opening edit modal for reservation:", reservation);
    console.log("Available lockers:", lockers);
    setSelectedReservation(reservation);

    // Convert UTC times to local for the form
    const startTime = reservation.start_time
      ? toDatetimeLocal(new Date(reservation.start_time))
      : "";
    const endTime = reservation.end_time
      ? toDatetimeLocal(new Date(reservation.end_time))
      : "";

    setFormData({
      locker_id: String(reservation.locker_id || ""),
      start_time: startTime,
      end_time: endTime,
      notes: reservation.notes || "",
    });
    setShowEditModal(true);
    setError("");
  };

  // Helper function to ensure locker ID is always a string
  const getLockerValue = (lockerId) => {
    return lockerId?.toString() || "";
  };

  const getReservationsForDate = (date) => {
    return reservations.filter((reservation) => {
      const reservationDate = new Date(reservation.start_time);
      return reservationDate.toDateString() === date.toDateString();
    });
  };

  const formatDateTime = (dateTimeString) => {
    return new Date(dateTimeString).toLocaleString();
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "active":
        return "text-green-600";
      case "cancelled":
        return "text-red-600";
      case "completed":
        return "text-blue-600";
      case "expired":
        return "text-gray-600";
      default:
        return "text-gray-600";
    }
  };

  const getStatusBadge = (status) => {
    const baseClasses = "px-2 py-1 rounded-full text-xs font-medium";
    if (isDarkMode) {
      switch (status) {
        case "active":
          return `${baseClasses} bg-green-900 text-green-200`;
        case "cancelled":
          return `${baseClasses} bg-red-900 text-red-200`;
        case "completed":
          return `${baseClasses} bg-blue-900 text-blue-200`;
        case "expired":
          return `${baseClasses} bg-gray-700 text-gray-300`;
        default:
          return `${baseClasses} bg-gray-700 text-gray-300`;
      }
    } else {
      switch (status) {
        case "active":
          return `${baseClasses} bg-green-100 text-green-800`;
        case "cancelled":
          return `${baseClasses} bg-red-100 text-red-800`;
        case "completed":
          return `${baseClasses} bg-blue-100 text-blue-800`;
        case "expired":
          return `${baseClasses} bg-gray-100 text-gray-800`;
        default:
          return `${baseClasses} bg-gray-100 text-gray-800`;
      }
    }
  };

  // Add a function to check if reservation duration exceeds 7 days
  const isDurationTooLong = (start, end) => {
    if (!start || !end) return false;
    const startDate = new Date(start);
    const endDate = new Date(end);
    return endDate.getTime() - startDate.getTime() > 7 * 24 * 60 * 60 * 1000;
  };

  if (loading && reservations.length === 0) {
    return (
      <div
        className={`min-h-screen ${
          isDarkMode ? "bg-gray-900 text-white" : "bg-gray-50"
        }`}
      >
        <div className="container mx-auto px-4 py-8">
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      className={`min-h-screen ${
        isDarkMode ? "bg-gray-900 text-white" : "bg-gray-50"
      }`}
    >
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1
            className={`text-3xl font-bold mb-4 ${
              isDarkMode ? "text-white" : "text-gray-900"
            }`}
          >
            {t("reservations.title")}
          </h1>
          <div className="flex flex-wrap gap-4 items-center justify-between">
            <div className="flex gap-4">
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className={`px-4 py-2 border rounded-lg ${
                  isDarkMode
                    ? "bg-gray-800 border-gray-600 text-white"
                    : "bg-white border-gray-300"
                }`}
              >
                <option value="">{t("reservations.allStatuses")}</option>
                <option value="active">{t("reservations.active")}</option>
                <option value="cancelled">{t("reservations.cancelled")}</option>
                <option value="completed">{t("reservations.completed")}</option>
                <option value="expired">{t("reservations.expired")}</option>
              </select>

              <button
                onClick={openCreateModal}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
              >
                {t("reservations.createNew")}
              </button>
              <button
                onClick={() => {
                  console.log("Current lockers:", lockers);
                  alert(
                    `Total lockers: ${lockers.length}\nStatuses: ${lockers
                      .map((l) => l.status)
                      .join(", ")}`
                  );
                }}
                className="bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded-lg"
              >
                Debug Lockers
              </button>
            </div>

            {user?.role === "admin" && (
              <div className="flex gap-2">
                <button
                  onClick={() => handleExport("excel")}
                  disabled={exportLoading}
                  className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg disabled:opacity-50"
                >
                  {exportLoading ? "Exporting..." : "Export as Excel"}
                </button>
                <button
                  onClick={() => handleExport("csv")}
                  disabled={exportLoading}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg disabled:opacity-50"
                >
                  {exportLoading ? "Exporting..." : "Export as CSV"}
                </button>
                <button
                  onClick={() => handleExport("pdf")}
                  disabled={exportLoading}
                  className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg disabled:opacity-50"
                >
                  {exportLoading ? "Exporting..." : "Export as PDF"}
                </button>
              </div>
            )}
          </div>
        </div>

        {error && (
          <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
            {error}
          </div>
        )}

        {/* Calendar and List View */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Calendar */}
          <div
            className={`p-6 rounded-lg ${
              isDarkMode ? "bg-gray-800" : "bg-white"
            } shadow-lg`}
          >
            <h2
              className={`text-xl font-semibold mb-4 ${
                isDarkMode ? "text-white" : "text-gray-900"
              }`}
            >
              {t("reservations.calendar")}
            </h2>
            <Calendar
              onChange={setSelectedDate}
              value={selectedDate}
              className={`${isDarkMode ? "text-white" : "text-gray-900"}`}
              tileContent={({ date }) => {
                const dayReservations = getReservationsForDate(date);
                return dayReservations.length > 0 ? (
                  <div className="text-xs text-blue-600 font-bold">
                    {dayReservations.length}
                  </div>
                ) : null;
              }}
            />

            {/* Selected Date Reservations */}
            <div className="mt-4">
              <h3
                className={`font-semibold mb-2 ${
                  isDarkMode ? "text-white" : "text-gray-900"
                }`}
              >
                {t("reservations.reservationsFor")}{" "}
                {selectedDate.toLocaleDateString()}
              </h3>
              <div className="space-y-2">
                {getReservationsForDate(selectedDate).map((reservation) => (
                  <div
                    key={reservation.id}
                    className={`p-3 rounded-lg border ${
                      isDarkMode
                        ? "bg-gray-700 border-gray-600"
                        : "bg-gray-50 border-gray-200"
                    }`}
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-medium">{reservation.locker_name}</p>
                        <p className="text-sm text-gray-600">
                          {formatDateTime(reservation.start_time)} -{" "}
                          {formatDateTime(reservation.end_time)}
                        </p>
                        <p className="text-sm">
                          Code: {reservation.access_code}
                        </p>
                      </div>
                      <span className={getStatusBadge(reservation.status)}>
                        {t(`reservations.${reservation.status}`)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Reservations List */}
          <div
            className={`p-6 rounded-lg ${
              isDarkMode ? "bg-gray-800" : "bg-white"
            } shadow-lg`}
          >
            <h2
              className={`text-xl font-semibold mb-4 ${
                isDarkMode ? "text-white" : "text-gray-900"
              }`}
            >
              {t("reservations.allReservations")}
            </h2>
            <div className="space-y-4 max-h-96 overflow-y-auto">
              {reservations.map((reservation) => (
                <div
                  key={reservation.id}
                  className={`p-4 rounded-lg border ${
                    isDarkMode
                      ? "bg-gray-700 border-gray-600"
                      : "bg-gray-50 border-gray-200"
                  }`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h3 className="font-semibold">
                        {reservation.locker_name}
                      </h3>
                      <p className="text-sm text-gray-600">
                        {t("reservations.reservationCode")}:{" "}
                        {reservation.reservation_code}
                      </p>
                    </div>
                    <span className={getStatusBadge(reservation.status)}>
                      {t(`reservations.${reservation.status}`)}
                    </span>
                  </div>

                  <div className="space-y-1 text-sm">
                    <p>
                      <span className="font-medium">
                        {t("reservations.startTime")}:
                      </span>{" "}
                      {formatDateTime(reservation.start_time)}
                    </p>
                    <p>
                      <span className="font-medium">
                        {t("reservations.endTime")}:
                      </span>{" "}
                      {formatDateTime(reservation.end_time)}
                    </p>
                    <p>
                      <span className="font-medium">
                        {t("reservations.accessCode")}:
                      </span>{" "}
                      {reservation.access_code}
                    </p>
                    {reservation.notes && (
                      <p>
                        <span className="font-medium">
                          {t("reservations.notes")}:
                        </span>{" "}
                        {reservation.notes}
                      </p>
                    )}
                  </div>

                  <div className="flex gap-2 mt-3">
                    {reservation.status === "active" && (
                      <>
                        <button
                          onClick={() => openEditModal(reservation)}
                          className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm"
                        >
                          {t("reservations.edit")}
                        </button>
                        <button
                          onClick={() =>
                            handleCancelReservation(reservation.id)
                          }
                          className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm"
                        >
                          {t("reservations.cancel")}
                        </button>
                      </>
                    )}
                  </div>
                </div>
              ))}

              {reservations.length === 0 && (
                <div
                  className={`text-center py-8 ${
                    isDarkMode ? "text-gray-400" : "text-gray-500"
                  }`}
                >
                  {t("reservations.noReservations")}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Create Reservation Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div
              className={`p-6 rounded-lg w-full max-w-md ${
                isDarkMode ? "bg-gray-800" : "bg-white"
              }`}
            >
              <h2
                className={`text-xl font-semibold mb-4 ${
                  isDarkMode ? "text-white" : "text-gray-900"
                }`}
              >
                {t("reservations.createNew")}
              </h2>
              <form onSubmit={handleCreateReservation} className="space-y-4">
                {/* Debug: Show all lockers */}
                <div className="text-xs text-gray-500 mb-2">
                  Debug: {lockers.length} total lockers, Statuses:{" "}
                  {lockers.map((l) => l.status).join(", ")}
                </div>
                <div>
                  <label
                    className={`block text-sm font-medium mb-1 ${
                      isDarkMode ? "text-white" : "text-gray-700"
                    }`}
                  >
                    {t("reservations.locker")}
                  </label>
                  <select
                    value={formData.locker_id}
                    onChange={(e) =>
                      setFormData({ ...formData, locker_id: e.target.value })
                    }
                    required
                    className={`w-full px-3 py-2 border rounded-lg ${
                      isDarkMode
                        ? "bg-gray-700 border-gray-600 text-white"
                        : "bg-white border-gray-300"
                    }`}
                  >
                    <option value="">{t("reservations.selectLocker")}</option>
                    {lockers
                      .filter((locker) => locker.status === "active")
                      .map((locker) => (
                        <option key={locker.id} value={locker.id}>
                          {locker.name} - {locker.number}
                        </option>
                      ))}
                  </select>
                </div>

                <div>
                  <label
                    className={`block text-sm font-medium mb-1 ${
                      isDarkMode ? "text-white" : "text-gray-700"
                    }`}
                  >
                    {t("reservations.startTime")}
                  </label>
                  <input
                    type="datetime-local"
                    value={formData.start_time}
                    onChange={(e) =>
                      setFormData({ ...formData, start_time: e.target.value })
                    }
                    required
                    className={`w-full px-3 py-2 border rounded-lg ${
                      isDarkMode
                        ? "bg-gray-700 border-gray-600 text-white"
                        : "bg-white border-gray-300"
                    }`}
                  />
                  {isStartTimeInPast(formData.start_time) && (
                    <div className="text-red-500 text-xs mt-1">
                      {t("reservations.startTimePast")}
                    </div>
                  )}
                </div>

                <div>
                  <label
                    className={`block text-sm font-medium mb-1 ${
                      isDarkMode ? "text-white" : "text-gray-700"
                    }`}
                  >
                    {t("reservations.endTime")}
                  </label>
                  <input
                    type="datetime-local"
                    value={formData.end_time}
                    onChange={(e) =>
                      setFormData({ ...formData, end_time: e.target.value })
                    }
                    required
                    className={`w-full px-3 py-2 border rounded-lg ${
                      isDarkMode
                        ? "bg-gray-700 border-gray-600 text-white"
                        : "bg-white border-gray-300"
                    }`}
                  />
                  {isDurationTooLong(
                    formData.start_time,
                    formData.end_time
                  ) && (
                    <div className="text-red-500 text-xs mt-1">
                      Reservation cannot exceed 7 days
                    </div>
                  )}
                </div>

                <div>
                  <label
                    className={`block text-sm font-medium mb-1 ${
                      isDarkMode ? "text-white" : "text-gray-700"
                    }`}
                  >
                    {t("reservations.notes")}
                  </label>
                  <textarea
                    value={formData.notes}
                    onChange={(e) =>
                      setFormData({ ...formData, notes: e.target.value })
                    }
                    rows="3"
                    className={`w-full px-3 py-2 border rounded-lg ${
                      isDarkMode
                        ? "bg-gray-700 border-gray-600 text-white"
                        : "bg-white border-gray-300"
                    }`}
                  />
                </div>

                <div className="flex gap-2">
                  <button
                    type="submit"
                    disabled={loading}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg disabled:opacity-50"
                  >
                    {loading
                      ? t("reservations.creating")
                      : t("reservations.create")}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="flex-1 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg"
                  >
                    {t("reservations.cancel")}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Edit Reservation Modal */}
        {showEditModal && selectedReservation && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div
              className={`p-6 rounded-lg w-full max-w-md ${
                isDarkMode ? "bg-gray-800" : "bg-white"
              }`}
            >
              <h2
                className={`text-xl font-semibold mb-4 ${
                  isDarkMode ? "text-white" : "text-gray-900"
                }`}
              >
                {t("reservations.editReservation")}
              </h2>
              <form onSubmit={handleUpdateReservation} className="space-y-4">
                <div>
                  <label
                    className={`block text-sm font-medium mb-1 ${
                      isDarkMode ? "text-white" : "text-gray-700"
                    }`}
                  >
                    {t("reservations.locker")}
                  </label>
                  <select
                    value={formData.locker_id}
                    onChange={(e) =>
                      setFormData({ ...formData, locker_id: e.target.value })
                    }
                    required
                    className={`w-full px-3 py-2 border rounded-lg ${
                      isDarkMode
                        ? "bg-gray-700 border-gray-600 text-white"
                        : "bg-white border-gray-300"
                    }`}
                  >
                    <option value="">{t("reservations.selectLocker")}</option>
                    {/* Show all active lockers plus the current one (even if reserved) */}
                    {[
                      ...lockers.filter(
                        (locker) =>
                          locker.status === "active" ||
                          String(locker.id) === String(formData.locker_id)
                      ),
                    ]
                      // Remove duplicates by locker id
                      .filter(
                        (locker, idx, arr) =>
                          arr.findIndex((l) => l.id === locker.id) === idx
                      )
                      .map((locker) => (
                        <option key={locker.id} value={locker.id}>
                          {locker.name} - {locker.number}
                          {locker.status === "reserved" &&
                          String(locker.id) === String(formData.locker_id)
                            ? " (currently assigned)"
                            : ""}
                        </option>
                      ))}
                  </select>
                </div>

                <div>
                  <label
                    className={`block text-sm font-medium mb-1 ${
                      isDarkMode ? "text-white" : "text-gray-700"
                    }`}
                  >
                    {t("reservations.startTime")}
                  </label>
                  <input
                    type="datetime-local"
                    value={formData.start_time}
                    onChange={(e) =>
                      setFormData({ ...formData, start_time: e.target.value })
                    }
                    required
                    className={`w-full px-3 py-2 border rounded-lg ${
                      isDarkMode
                        ? "bg-gray-700 border-gray-600 text-white"
                        : "bg-white border-gray-300"
                    }`}
                  />
                </div>

                <div>
                  <label
                    className={`block text-sm font-medium mb-1 ${
                      isDarkMode ? "text-white" : "text-gray-700"
                    }`}
                  >
                    {t("reservations.endTime")}
                  </label>
                  <input
                    type="datetime-local"
                    value={formData.end_time}
                    onChange={(e) =>
                      setFormData({ ...formData, end_time: e.target.value })
                    }
                    required
                    className={`w-full px-3 py-2 border rounded-lg ${
                      isDarkMode
                        ? "bg-gray-700 border-gray-600 text-white"
                        : "bg-white border-gray-300"
                    }`}
                  />
                </div>

                <div>
                  <label
                    className={`block text-sm font-medium mb-1 ${
                      isDarkMode ? "text-white" : "text-gray-700"
                    }`}
                  >
                    {t("reservations.notes")}
                  </label>
                  <textarea
                    value={formData.notes}
                    onChange={(e) =>
                      setFormData({ ...formData, notes: e.target.value })
                    }
                    rows="3"
                    className={`w-full px-3 py-2 border rounded-lg ${
                      isDarkMode
                        ? "bg-gray-700 border-gray-600 text-white"
                        : "bg-white border-gray-300"
                    }`}
                  />
                </div>

                <div className="flex gap-2">
                  <button
                    type="submit"
                    disabled={loading}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg disabled:opacity-50"
                  >
                    {loading
                      ? t("reservations.updating")
                      : t("reservations.update")}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowEditModal(false)}
                    className="flex-1 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg"
                  >
                    {t("reservations.cancel")}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Reservations;
