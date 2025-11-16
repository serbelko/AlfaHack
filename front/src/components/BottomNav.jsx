import React from "react";
import { NavLink } from "react-router-dom";
import "./BottomNav.css";

import homeIcon from "../assets/icons/bottom-nav/home.svg";
import paymentsIcon from "../assets/icons/bottom-nav/payments.svg";
import servicesIcon from "../assets/icons/bottom-nav/services.svg";
import contactIcon from "../assets/icons/bottom-nav/chat.svg";
import profileIcon from "../assets/icons/bottom-nav/profile.svg";

function BottomNav() {
  return (
    <nav className="bottom-nav-wrapper">
      <div className="bottom-nav">
        <NavLink
          to="/"
          end
          className={({ isActive }) =>
            "bottom-nav-item" + (isActive ? " bottom-nav-item--active" : "")
          }
        >
          <img src={homeIcon} alt="" className="bottom-nav-icon" />
          <span className="bottom-nav-label">Главный</span>
        </NavLink>

        <NavLink
          to="/payments"
          className={({ isActive }) =>
            "bottom-nav-item" + (isActive ? " bottom-nav-item--active" : "")
          }
        >
          <img src={paymentsIcon} alt="" className="bottom-nav-icon" />
          <span className="bottom-nav-label">Платежи</span>
        </NavLink>

        <NavLink
          to="/services"
          className={({ isActive }) =>
            "bottom-nav-item" + (isActive ? " bottom-nav-item--active" : "")
          }
        >
          <img src={servicesIcon} alt="" className="bottom-nav-icon" />
          <span className="bottom-nav-label">Сервисы</span>
        </NavLink>

        <NavLink
          to="/contact"
          className={({ isActive }) =>
            "bottom-nav-item" + (isActive ? " bottom-nav-item--active" : "")
          }
        >
          <img src={contactIcon} alt="" className="bottom-nav-icon" />
          <span className="bottom-nav-label">Связь</span>
        </NavLink>

        <NavLink
          to="/profile"
          className={({ isActive }) =>
            "bottom-nav-item" + (isActive ? " bottom-nav-item--active" : "")
          }
        >
          <img src={profileIcon} alt="" className="bottom-nav-icon" />
          <span className="bottom-nav-label">Профиль</span>
        </NavLink>
      </div>

      <div className="bottom-nav-home-indicator" />
    </nav>
  );
}

export default BottomNav;
