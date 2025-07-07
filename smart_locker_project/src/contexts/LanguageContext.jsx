import { createContext, useContext, useState, useEffect } from "react";

const LanguageContext = createContext();

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error("useLanguage must be used within a LanguageProvider");
  }
  return context;
};

const translations = {
  en: {
    // Navigation
    main_menu: "Main Menu",
    borrow: "Borrow",
    return: "Return",
    admin: "Admin",
    users: "Users",
    items: "Items",
    lockers: "Lockers",
    logs: "Logs",
    logout: "Logout",

    // Login
    login: "Login",
    username: "Username",
    password: "Password",
    login_button: "Sign In",
    login_error: "Invalid username or password",

    // Main Menu
    welcome: "Welcome",
    select_option: "Please select an option",
    borrow_item: "Borrow an Item",
    return_item: "Return an Item",
    admin_panel: "Admin Panel",

    // Borrow
    scan_rfid: "Scan RFID Card",
    select_item: "Select Item",
    select_locker: "Select Locker",
    confirm_borrow: "Confirm Borrow",
    borrow_success: "Item borrowed successfully",
    borrow_error: "Failed to borrow item",

    // Return
    return_success: "Item returned successfully",
    return_error: "Failed to return item",

    // Admin
    dashboard: "Dashboard",
    total_users: "Total Users",
    total_items: "Total Items",
    total_lockers: "Total Lockers",
    active_borrows: "Active Borrows",
    recent_activity: "Recent Activity",

    // Common
    loading: "Loading...",
    error: "Error",
    success: "Success",
    cancel: "Cancel",
    save: "Save",
    delete: "Delete",
    edit: "Edit",
    add: "Add",
    search: "Search",
    no_data: "No data available",
  },
  fr: {
    main_menu: "Menu Principal",
    borrow: "Emprunter",
    return: "Retourner",
    admin: "Administration",
    users: "Utilisateurs",
    items: "Articles",
    lockers: "Casiers",
    logs: "Journaux",
    logout: "Déconnexion",
    login: "Connexion",
    username: "Nom d'utilisateur",
    password: "Mot de passe",
    login_button: "Se Connecter",
    login_error: "Nom d'utilisateur ou mot de passe invalide",
    welcome: "Bienvenue",
    select_option: "Veuillez sélectionner une option",
    borrow_item: "Emprunter un Article",
    return_item: "Retourner un Article",
    admin_panel: "Panneau d'Administration",
    scan_rfid: "Scanner la Carte RFID",
    select_item: "Sélectionner l'Article",
    select_locker: "Sélectionner le Casier",
    confirm_borrow: "Confirmer l'Emprunt",
    borrow_success: "Article emprunté avec succès",
    borrow_error: "Échec de l'emprunt",
    return_success: "Article retourné avec succès",
    return_error: "Échec du retour",
    dashboard: "Tableau de Bord",
    total_users: "Total Utilisateurs",
    total_items: "Total Articles",
    total_lockers: "Total Casiers",
    active_borrows: "Emprunts Actifs",
    recent_activity: "Activité Récente",
    loading: "Chargement...",
    error: "Erreur",
    success: "Succès",
    cancel: "Annuler",
    save: "Enregistrer",
    delete: "Supprimer",
    edit: "Modifier",
    add: "Ajouter",
    search: "Rechercher",
    no_data: "Aucune donnée disponible",
  },
  es: {
    main_menu: "Menú Principal",
    borrow: "Prestar",
    return: "Devolver",
    admin: "Administración",
    users: "Usuarios",
    items: "Artículos",
    lockers: "Casilleros",
    logs: "Registros",
    logout: "Cerrar Sesión",
    login: "Iniciar Sesión",
    username: "Nombre de Usuario",
    password: "Contraseña",
    login_button: "Iniciar Sesión",
    login_error: "Nombre de usuario o contraseña inválidos",
    welcome: "Bienvenido",
    select_option: "Por favor seleccione una opción",
    borrow_item: "Prestar un Artículo",
    return_item: "Devolver un Artículo",
    admin_panel: "Panel de Administración",
    scan_rfid: "Escanear Tarjeta RFID",
    select_item: "Seleccionar Artículo",
    select_locker: "Seleccionar Casillero",
    confirm_borrow: "Confirmar Préstamo",
    borrow_success: "Artículo prestado exitosamente",
    borrow_error: "Error al prestar artículo",
    return_success: "Artículo devuelto exitosamente",
    return_error: "Error al devolver artículo",
    dashboard: "Panel de Control",
    total_users: "Total de Usuarios",
    total_items: "Total de Artículos",
    total_lockers: "Total de Casilleros",
    active_borrows: "Préstamos Activos",
    recent_activity: "Actividad Reciente",
    loading: "Cargando...",
    error: "Error",
    success: "Éxito",
    cancel: "Cancelar",
    save: "Guardar",
    delete: "Eliminar",
    edit: "Editar",
    add: "Agregar",
    search: "Buscar",
    no_data: "No hay datos disponibles",
  },
  tr: {
    main_menu: "Ana Menü",
    borrow: "Ödünç Al",
    return: "Geri Ver",
    admin: "Yönetim",
    users: "Kullanıcılar",
    items: "Eşyalar",
    lockers: "Dolaplar",
    logs: "Kayıtlar",
    logout: "Çıkış",
    login: "Giriş",
    username: "Kullanıcı Adı",
    password: "Şifre",
    login_button: "Giriş Yap",
    login_error: "Geçersiz kullanıcı adı veya şifre",
    welcome: "Hoş Geldiniz",
    select_option: "Lütfen bir seçenek seçin",
    borrow_item: "Eşya Ödünç Al",
    return_item: "Eşya Geri Ver",
    admin_panel: "Yönetim Paneli",
    scan_rfid: "RFID Kartı Tara",
    select_item: "Eşya Seç",
    select_locker: "Dolap Seç",
    confirm_borrow: "Ödünç Almayı Onayla",
    borrow_success: "Eşya başarıyla ödünç alındı",
    borrow_error: "Eşya ödünç alınamadı",
    return_success: "Eşya başarıyla geri verildi",
    return_error: "Eşya geri verilemedi",
    dashboard: "Kontrol Paneli",
    total_users: "Toplam Kullanıcı",
    total_items: "Toplam Eşya",
    total_lockers: "Toplam Dolap",
    active_borrows: "Aktif Ödünç Almalar",
    recent_activity: "Son Aktiviteler",
    loading: "Yükleniyor...",
    error: "Hata",
    success: "Başarılı",
    cancel: "İptal",
    save: "Kaydet",
    delete: "Sil",
    edit: "Düzenle",
    add: "Ekle",
    search: "Ara",
    no_data: "Veri bulunamadı",
  },
};

export const LanguageProvider = ({ children }) => {
  const [currentLanguage, setCurrentLanguage] = useState("en");

  useEffect(() => {
    const savedLanguage = localStorage.getItem("language");
    if (savedLanguage && translations[savedLanguage]) {
      setCurrentLanguage(savedLanguage);
    }
  }, []);

  const changeLanguage = (language) => {
    if (translations[language]) {
      setCurrentLanguage(language);
      localStorage.setItem("language", language);
    }
  };

  const t = (key) => {
    return translations[currentLanguage][key] || translations.en[key] || key;
  };

  const value = {
    currentLanguage,
    changeLanguage,
    t,
    availableLanguages: Object.keys(translations),
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
};
