/**
 * constants.ts
 * ------------
 * Stores constants like API URLs, routes, etc.
 */

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const ROUTES = {
  LOGIN: '/login',
  BRAND_SEARCH: '/',
  CREATOR_DASHBOARD: '/creator/dashboard',
  INFLUENCER_DETAILS: '/influencers/:id',
  ALERTS: '/alerts',
};



//export const NICHES = ["Fashion", "Travel", "Tech", "Food", "Sports"];
