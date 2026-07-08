/** @type {import('jest').Config} */
module.exports = {
  testEnvironment: 'node',
  setupFilesAfterEnv: ['<rootDir>/test/setup.js'],
  testMatch: ['**/test/**/*.test.js'],
  modulePathIgnorePatterns: [
    '<rootDir>/lib/',
    '<rootDir>/wx-charts-master/',
  ],
};
