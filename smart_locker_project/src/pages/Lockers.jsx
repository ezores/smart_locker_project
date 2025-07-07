import { useLanguage } from "../contexts/LanguageContext";

const Lockers = () => {
  const { t } = useLanguage();

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          {t("lockers")}
        </h1>
        <p className="text-gray-600">Configure and monitor locker status</p>
      </div>

      <div className="card">
        <div className="text-center py-12">
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Lockers Management
          </h3>
          <p className="text-gray-600">
            This page will contain locker configuration functionality
          </p>
        </div>
      </div>
    </div>
  );
};

export default Lockers;
