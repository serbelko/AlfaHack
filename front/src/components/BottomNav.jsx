import React from "react";
import { NavLink } from "react-router-dom";
import "./BottomNav.css";

import home from "../assets/icons/bottom-nav/home.svg";
import payments from "../assets/icons/bottom-nav/payments.svg";
import services from "../assets/icons/bottom-nav/services.svg";
import chat from "../assets/icons/bottom-nav/chat.svg";
import profile from "../assets/icons/bottom-nav/profile.svg";

function BottomNav() {
  return (
    <div className="bottom-nav-wrapper">
      <div className="bottom-nav">
        <NavLink
          to="/"
          end
          className={({ isActive }) =>
            "bottom-nav-item" + (isActive ? " bottom-nav-item--active" : "")
          }
        >
          <img src={home} alt="Главный" className="bottom-nav-icon-svg" />
        </NavLink>

        <NavLink
          to="/payments"
          className={({ isActive }) =>
            "bottom-nav-item" + (isActive ? " bottom-nav-item--active" : "")
          }
        >
          <img src={payments} alt="Платежи" className="bottom-nav-icon-svg" />
        </NavLink>

        <NavLink
          to="/services"
          className={({ isActive }) =>
            "bottom-nav-item" + (isActive ? " bottom-nav-item--active" : "")
          }
        >
          <img src={services} alt="Сервисы" className="bottom-nav-icon-svg" />
        </NavLink>

        <NavLink
          to="/contact"
          className={({ isActive }) =>
            "bottom-nav-item" + (isActive ? " bottom-nav-item--active" : "")
          }
        >
          <img src={chat} alt="Связь" className="bottom-nav-icon-svg" />
        </NavLink>

        <NavLink
          to="/profile"
          className={({ isActive }) =>
            "bottom-nav-item" + (isActive ? " bottom-nav-item--active" : "")
          }
        >
          <img src={profile} alt="Профиль" className="bottom-nav-icon-svg" />
        </NavLink>
      </div>

      <div className="bottom-nav-indicator" />
    </div>
  );
}

export default BottomNav;
