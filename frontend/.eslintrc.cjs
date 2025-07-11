module.exports = {
  root: true,
  env: {
    browser: true,
    es2020: true,
    jest: true,
    node: true,
  },
  extends: [
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:react/jsx-runtime",
    "plugin:react-hooks/recommended",
  ],
  ignorePatterns: ["dist", ".eslintrc.cjs", "coverage/**/*"],
  parserOptions: { ecmaVersion: "latest", sourceType: "module" },
  settings: { react: { version: "18.3" } },
  plugins: ["react-refresh"],
  rules: {
    "react-refresh/only-export-components": [
      "warn",
      { allowConstantExport: true },
    ],
    "react/prop-types": "off",
    "react/react-in-jsx-scope": "off",
    "no-unused-vars": [
      "error",
      {
        argsIgnorePattern: "^_",
        varsIgnorePattern: "^_",
        ignoreRestSiblings: true,
        caughtErrorsIgnorePattern: "^_",
      },
    ],
  },
  globals: {
    jest: "readonly",
    describe: "readonly",
    test: "readonly",
    it: "readonly",
    expect: "readonly",
    beforeEach: "readonly",
    afterEach: "readonly",
    beforeAll: "readonly",
    afterAll: "readonly",
    require: "readonly",
    global: "readonly",
  },
  overrides: [
    {
      files: [
        "**/*.test.js",
        "**/*.test.jsx",
        "**/*.spec.js",
        "**/*.spec.jsx",
        "**/__tests__/**/*",
      ],
      rules: {
        "no-unused-vars": "off",
        "react/react-in-jsx-scope": "error",
      },
    },
  ],
};
