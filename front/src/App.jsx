import React from "react";
import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import MainLayout from "./layouts/MainLayout";

import LoginPage from "./pages/LoginPage";
import HomePage from "./pages/HomePage";
import AnalyticsPage from "./pages/AnalyticsPage";
import RecommendationDetailPage from "./pages/RecommendationDetailPage";
import PromotionPage from "./pages/PromotionPage";
import NicheDescriptionPage from "./pages/NicheDescriptionPage";
import CompetitorDetailPage from "./pages/CompetitorDetailPage";
import PaymentsPage from "./pages/PaymentsPage";
import AccountsPage from "./pages/AccountsPage";
import ServicesPage from "./pages/ServicesPage";
import ProfilePage from "./pages/ProfilePage";
import ContactPage from "./pages/ContactPage";
import { getToken } from "./api/httpClient";

function RequireAuth({ children }) {
  const location = useLocation();
  const token = getToken();

  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      <Route
        path="/"
        element={
          <RequireAuth>
            <MainLayout />
          </RequireAuth>
        }
      >
        <Route index element={<HomePage />} />
        <Route path="analytics" element={<AnalyticsPage />} />
        <Route
          path="analytics/recommendation"
          element={<RecommendationDetailPage />}
        />
        <Route path="promotion" element={<PromotionPage />} />
        <Route path="promotion/niche" element={<NicheDescriptionPage />} />
        <Route
          path="promotion/competitor/:id"
          element={<CompetitorDetailPage />}
        />
        <Route path="payments" element={<PaymentsPage />} />
        <Route path="accounts" element={<AccountsPage />} />
        <Route path="services" element={<ServicesPage />} />
        <Route path="contact" element={<ContactPage />} />
        <Route path="profile" element={<ProfilePage />} />
      </Route>

      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}

export default App;
