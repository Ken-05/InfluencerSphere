/**
 * influencerApi.ts
 * ----------------
 * Functions for interacting with influencer-related API endpoints.
 */

import { apiClient } from './apiClient';

export interface InfluencerProfile {
  platform_id: string;
  username: string;
  platform: string;
  niche_tags: string[];
  follower_count: number;
  engagement_rate: number;
  market_score: number;
  market_tier?: string; // from augmentation
}

export interface SearchResult {
    count: number;
    results: InfluencerProfile[];
}

export interface SearchParams {
  q?: string;
  niche?: string;
  min_engagement?: number;
  min_followers?: number;
  limit?: number;
  page?: number;
}

export const searchInfluencers = async (params: SearchParams): Promise<SearchResult> => {
  const response = await apiClient.get<SearchResult>('/search/influencers', { params });
  return response.data;
};

