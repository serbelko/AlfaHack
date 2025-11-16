import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import "./LoginPage.css";
import { loginRequest, isAuthenticated } from "../api/authApi";

function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();

  const [login, setLogin] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (isAuthenticated()) {
      const from = location.state?.from?.pathname || "/";
      navigate(from, { replace: true });
    }
  }, [location.state, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      const trimmedLogin = login.trim();
      const trimmedPassword = password.trim();
      if (!trimmedLogin || !trimmedPassword) {
        setError("Введите логин и пароль");
        setIsLoading(false);
        return;
      }

      await loginRequest(trimmedLogin, trimmedPassword);

      const from = location.state?.from?.pathname || "/";
      navigate(from, { replace: true });
    } catch (err) {
      if (err.status === 401) {
        setError("Неверный логин или пароль");
      } else if (err.status === 404) {
        setError("Пользователь с таким логином не найден");
      } else {
        setError("Техническая ошибка. Попробуйте позже");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleForgotPassword = () => {
    alert(
      "Обратитесь к администратору или в поддержку, чтобы восстановить доступ."
    );
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-logo">
          <div className="logo-icon">
            <span>А</span>
          </div>
        </div>

        <h1 className="login-title">Добро пожаловать в Альфа-Бизнес</h1>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label className="form-label">Логин</label>
            <input
              className="form-input"
              type="text"
              value={login}
              onChange={(e) => setLogin(e.target.value)}
              autoComplete="username"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Пароль</label>
            <input
              className="form-input"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              required
            />
          </div>

          {error && <div className="login-error">{error}</div>}

          <button className="login-button" type="submit" disabled={isLoading}>
            {isLoading ? "Вход..." : "Войти"}
          </button>
        </form>

        <button
          type="button"
          className="forgot-password-link"
          onClick={handleForgotPassword}
        >
          Забыли логин или пароль?
        </button>
        <div className="login-extra-info">
          <h3 className="login-extra-title">Полезная информация</h3>

          <ul className="login-extra-list">
            <li>• Никому не сообщайте пароль и код подтверждения</li>
            <li>• Проверьте, что вы вошли на официальный сайт</li>
            <li>• Восстановление доступа доступно через поддержку</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
