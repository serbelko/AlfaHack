import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./LoginPage.css";

function LoginPage() {
  const navigate = useNavigate();
  const [login, setLogin] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setError(null);

    setIsLoading(true);

    setTimeout(() => {
      setIsLoading(false);
      if (login === "demo" && password === "demo") {
        navigate("/", { replace: true });
      } else {
        setError("Неверные данные");
      }
    }, 500);
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
