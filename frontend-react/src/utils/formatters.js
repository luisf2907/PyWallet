/**
 * Formatting utility functions for dates and numbers
 */

/**
 * Formats a date to DD/MM/YYYY
 * @param {Date|string} date - Date to format
 * @returns {string} Formatted date string
 */
export const formatDate = (date) => {
  if (!date) return '';
  
  const d = date instanceof Date ? date : new Date(date);
  
  // Check if date is valid
  if (isNaN(d.getTime())) return '';
  
  return d.toLocaleDateString('pt-BR');
};

/**
 * Formats a date to YYYY-MM-DD (ISO format for inputs)
 * @param {Date|string} date - Date to format
 * @returns {string} Formatted date string
 */
export const formatDateForInput = (date) => {
  if (!date) return '';
  
  const d = date instanceof Date ? date : new Date(date);
  
  // Check if date is valid
  if (isNaN(d.getTime())) return '';
  
  return d.toISOString().split('T')[0];
};

/**
 * Gets the current date formatted as YYYY-MM-DD
 * @returns {string} Today's date in YYYY-MM-DD format
 */
export const getTodayFormatted = () => {
  return formatDateForInput(new Date());
};

/**
 * Gets a date from X days ago formatted as YYYY-MM-DD
 * @param {number} days - Number of days to go back
 * @returns {string} Past date in YYYY-MM-DD format
 */
export const getPastDateFormatted = (days) => {
  const date = new Date();
  date.setDate(date.getDate() - days);
  return formatDateForInput(date);
};

/**
 * Gets a date from X months ago formatted as YYYY-MM-DD
 * @param {number} months - Number of months to go back
 * @returns {string} Past date in YYYY-MM-DD format
 */
export const getPastMonthsFormatted = (months) => {
  const date = new Date();
  date.setMonth(date.getMonth() - months);
  return formatDateForInput(date);
};

/**
 * Gets a date from X years ago formatted as YYYY-MM-DD
 * @param {number} years - Number of years to go back
 * @returns {string} Past date in YYYY-MM-DD format
 */
export const getPastYearsFormatted = (years) => {
  const date = new Date();
  date.setFullYear(date.getFullYear() - years);
  return formatDateForInput(date);
};

/**
 * Formats a file size in bytes to a human-readable format
 * @param {number} bytes - Size in bytes
 * @returns {string} Formatted size string (e.g., "2.5 MB")
 */
export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};
