/**
 * formatters.ts
 * -------------
 * Utility functions to format numbers, text, etc.
 */

export const formatNumber = (num: number): string =>
  num >= 1000 ? (num / 1000).toFixed(1) + "k" : num.toString();

