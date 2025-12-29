/**
 * influencersSlice.ts
 * ------------------
 * Redux slice for influencer data.
 */

import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { fetchAllInfluencers } from "../../services/influencerApi";

export const loadInfluencers = createAsyncThunk("influencers/load", async () => {
  const data = await fetchAllInfluencers();
  return data.map((i: any) => ({ username: i.username, score: i.quality_score }));
});

const influencersSlice = createSlice({
  name: "influencers",
  initialState: { items: [], loading: false },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(loadInfluencers.pending, (state) => {
        state.loading = true;
      })
      .addCase(loadInfluencers.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(loadInfluencers.rejected, (state) => {
        state.loading = false;
      });
  },
});

export default influencersSlice.reducer;
