import React from "react";
import { Outlet, useLocation } from "react-router-dom";
import BottomNav from "../components/BottomNav";

function MainLayout() {
  const location = useLocation();
  const hideNav = location.pathname === "/login"; // на всякий случай

  return (
    <div className="app-shell">
      <main className="app-content">
        <Outlet />
      </main>
      {!hideNav && <BottomNav />}
    </div>
  );
}

export default MainLayout;
