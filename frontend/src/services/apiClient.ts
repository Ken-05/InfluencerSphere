/**
 * apiClient.ts
 * ------------
 * Axios client configured for backend API calls.
 */

import axios from 'axios';
import { API_BASE_URL } from '../utils/constants';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});
