/**
 * Form validation utility functions
 */

/**
 * Validates if a value is empty
 * @param {string} value - Value to check
 * @returns {boolean} True if value is empty
 */
export const isEmpty = (value) => {
  return value === null || value === undefined || value.trim() === '';
};

/**
 * Validates if a value is a valid number
 * @param {string} value - Value to check
 * @returns {boolean} True if value is a valid number
 */
export const isValidNumber = (value) => {
  if (isEmpty(value)) return false;
  // Replace comma with dot for international number parsing
  const parsedValue = parseFloat(value.toString().replace(',', '.'));
  return !isNaN(parsedValue);
};

/**
 * Validates if a value is a valid integer
 * @param {string} value - Value to check
 * @returns {boolean} True if value is a valid integer
 */
export const isValidInteger = (value) => {
  if (isEmpty(value)) return false;
  const parsedValue = parseInt(value, 10);
  return !isNaN(parsedValue) && Number.isInteger(parsedValue);
};

/**
 * Validates if a value is a valid date in YYYY-MM-DD format
 * @param {string} value - Value to check
 * @returns {boolean} True if value is a valid date
 */
export const isValidDate = (value) => {
  if (isEmpty(value)) return false;
  return /^\d{4}-\d{2}-\d{2}$/.test(value);
};

/**
 * Validates if a value is a valid email
 * @param {string} value - Value to check
 * @returns {boolean} True if value is a valid email
 */
export const isValidEmail = (value) => {
  if (isEmpty(value)) return false;
  // Basic email validation
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
};

/**
 * Validates if a string has minimum length
 * @param {string} value - Value to check
 * @param {number} minLength - Minimum length required
 * @returns {boolean} True if value meets minimum length
 */
export const hasMinLength = (value, minLength) => {
  if (isEmpty(value)) return false;
  return value.length >= minLength;
};

/**
 * Converts a string with comma decimal separator to a number
 * @param {string} value - Value to convert (e.g. "1.234,56" or "1,234.56")
 * @returns {number} Converted number
 */
export const parseNumberWithLocale = (value) => {
  if (isEmpty(value)) return 0;
  // Replace comma with dot for parsing
  return parseFloat(value.toString().replace(',', '.'));
};

/**
 * Format number as currency (BRL)
 * @param {number} value - Number to format
 * @returns {string} Formatted currency string
 */
export const formatCurrency = (value) => {
  if (value === null || value === undefined) return 'R$ 0,00';
  return `R$ ${value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
};

/**
 * Format number as percentage
 * @param {number} value - Number to format
 * @param {number} decimals - Number of decimal places
 * @returns {string} Formatted percentage string
 */
export const formatPercentage = (value, decimals = 2) => {
  if (value === null || value === undefined) return '0,00%';
  return `${value.toLocaleString('pt-BR', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })}%`;
};
