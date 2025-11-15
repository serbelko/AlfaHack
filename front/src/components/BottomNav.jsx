import React from "react";
import { NavLink } from "react-router-dom";
import "./BottomNav.css";

const items = [
  {
    to: "/",
    label: "Главный",
    icon: (isActive) => (
      <svg width="26" height="24" viewBox="0 0 26 24" fill="none">
        <path
          d="M0.48239 7.40633L12.4865 0.144409C12.8048 -0.0481552 13.2037 -0.0480975 13.5219 0.144559L25.5179 7.40629C25.8172 7.58747 26 7.91189 26 8.26176V22.7551C26 23.3074 25.5523 23.7551 25 23.7551H17C16.4477 23.7551 16 23.3074 16 22.7551V16.2781C16 15.7258 15.5523 15.2781 15 15.2781H13.0042H11C10.4477 15.2781 10 15.7258 10 16.2781V22.7627C10 23.312 9.55691 23.7585 9.00761 23.7626L1.00761 23.8235C0.452366 23.8277 0 23.3788 0 22.8235V8.26195C0 7.91198 0.182952 7.58748 0.48239 7.40633Z"
          fill={isActive ? "#EF3125" : "#858589"}
        />
      </svg>
    ),
  },
  {
    to: "/payments",
    label: "Платежи",
    icon: (isActive) => (
      <div
        className="ruble-icon"
        style={{ background: isActive ? "#EF3125" : "#858589" }}
      >
        <span>₽</span>
      </div>
    ),
  },
  {
    to: "/services",
    label: "Сервисы",
    icon: (isActive) => (
      <div className="services-icon">
        <div
          className="service-block block-1"
          style={{ background: isActive ? "#EF3125" : "#858589" }}
        ></div>
        <div
          className="service-block block-2"
          style={{ background: isActive ? "#EF3125" : "#858589" }}
        ></div>
        <div
          className="service-block block-3"
          style={{ background: isActive ? "#EF3125" : "#858589" }}
        ></div>
        <div
          className="service-block block-4"
          style={{ background: isActive ? "#EF3125" : "#858589" }}
        ></div>
      </div>
    ),
  },
  {
    to: "/contact",
    label: "Связь",
    icon: (isActive) => (
      <svg width="32" height="24" viewBox="0 0 32 24" fill="none">
        <path
          d="M24 10.5228C24 18.1917 17.3599 23.6256 12.4992 23.9814C12.2238 24.0016 12 23.7761 12 23.5V21.5397C12 21.2656 11.7787 21.0435 11.5049 21.0309C5.1682 20.7391 0 16.146 0 10.5228C0 4.71123 5.37258 0 12 0C18.6274 0 24 4.71123 24 10.5228Z"
          fill={isActive ? "#EF3125" : "#858589"}
        />
        <path
          d="M7 8.41821L17 8.41821"
          stroke="white"
          strokeWidth="2"
          strokeLinecap="round"
        />
        <path
          d="M7 12.4182H13"
          stroke="white"
          strokeWidth="2"
          strokeLinecap="round"
        />
      </svg>
    ),
  },
  {
    to: "/profile",
    label: "Профиль",
    icon: (isActive) => (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <path
          d="M18.0074 6C18.0074 9.31371 15.3179 12 12.0001 12C8.6824 12 5.99286 9.31371 5.99286 6C5.99286 2.68629 8.6824 0 12.0001 0C15.3179 0 18.0074 2.68629 18.0074 6Z"
          fill={isActive ? "#EF3125" : "#858589"}
        />
        <path
          d="M12 14C17.2642 14 21.7979 17.1215 23.8481 21.6122C24.3841 22.7864 23.4281 24 22.1361 24H1.86387C0.571881 24 -0.384072 22.7864 0.151948 21.6123C2.2021 17.1215 6.73587 14 12 14Z"
          fill={isActive ? "#EF3125" : "#858589"}
        />
      </svg>
    ),
  },
];

function BottomNav() {
  return (
    <nav className="bottom-nav">
      {items.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          className={({ isActive }) =>
            "bottom-nav__item" + (isActive ? " bottom-nav__item--active" : "")
          }
          end={item.to === "/"}
        >
          {({ isActive }) => (
            <>
              <div className="nav-icon">{item.icon(isActive)}</div>
              <span className="nav-label">{item.label}</span>
            </>
          )}
        </NavLink>
      ))}
    </nav>
  );
}

export default BottomNav;
