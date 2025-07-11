module.exports = {
  testEnvironment: "jsdom",
  setupFilesAfterEnv: ["<rootDir>/src/setupTests.js"],
  moduleNameMapper: {
    "\\.(css|less|scss|sass)$": "identity-obj-proxy",
    "\\.(gif|ttf|eot|svg|png)$": "<rootDir>/__mocks__/fileMock.js",
  },
  transform: {
    "^.+\\.(js|jsx)$": "babel-jest",
  },
  testMatch: [
    "<rootDir>/src/**/__tests__/**/*.{js,jsx}",
    "<rootDir>/src/**/*.{test,spec}.{js,jsx}",
  ],
  collectCoverageFrom: [
    "src/**/*.{js,jsx}",
    "!src/**/*.d.ts",
    "!src/main.jsx",
    "!src/index.css",
  ],
  coverageReporters: ["text", "lcov", "html"],
  testPathIgnorePatterns: ["/node_modules/", "/dist/"],
  transformIgnorePatterns: [
    "node_modules/(?!(react-calendar|get-user-locale|memoize|mimic-function|@wojtekmaj/date-utils)/)",
  ],
  moduleFileExtensions: ["js", "jsx", "json"],
  testEnvironmentOptions: {
    url: "http://localhost",
  },
  globals: {
    "ts-jest": {
      useESM: true,
    },
  },
};
