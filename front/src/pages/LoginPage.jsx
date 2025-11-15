import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./LoginPage.css";
import { loginRequest } from "../api/authApi";

function LoginPage() {
  const navigate = useNavigate();
  const [login, setLogin] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      await loginRequest(login, password);
      navigate("/", { replace: true });
    } catch (err) {
      console.error(err);
      if (err.status === 401) {
        // ТЗ: wrong login or password
        setError("Неверный логин или пароль");
      } else if (err.status === 404) {
        setError("Сервис авторизации не найден (404)");
      } else {
        setError("Техническая ошибка. Попробуйте позже");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleForgotPassword = () => {
    alert("Здесь будет восстановление логина/пароля");
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
      </div>
    </div>
  );
}

export default LoginPage;
