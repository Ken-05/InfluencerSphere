/**
 * index.ts
 * --------
 * Combines Redux slices into a store.
 */

import { configureStore } from "@reduxjs/toolkit";
import influencersReducer from "./slices/influencersSlice";
import alertsReducer from "./slices/alertsSlice";
import authReducer from "./slices/authSlice";

const store = configureStore({
  reducer: {
    influencers: influencersReducer,
    alerts: alertsReducer,
    auth: authReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
export default store;
