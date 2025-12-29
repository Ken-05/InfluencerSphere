/**
 * alertsSlice.ts
 * ---------------
 * Redux slice for alerts data.
 */

import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import apiClient from "../../services/apiClient";

export const loadAlerts = createAsyncThunk("alerts/load", async () => {
  const response = await apiClient.get("/alerts");
  return response.data.alerts;
});

const alertsSlice = createSlice({
  name: "alerts",
  initialState: { items: [], loading: false },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(loadAlerts.pending, (state) => {
        state.loading = true;
      })
      .addCase(loadAlerts.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(loadAlerts.rejected, (state) => {
        state.loading = false;
      });
  },
});

export default alertsSlice.reducer;
