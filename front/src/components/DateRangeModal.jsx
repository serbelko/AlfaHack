import React, { useState } from "react";
import "./DateRangeModal.css";

function DateRangeModal({ initialFrom, initialTo, onApply, onClose }) {
  const [startDate, setStartDate] = useState(initialFrom);
  const [endDate, setEndDate] = useState(initialTo);

  const today = new Date();
  const currentMonth = today.getMonth();
  const currentYear = today.getFullYear();

  const getDaysInMonth = (month, year) => {
    return new Date(year, month + 1, 0).getDate();
  };

  const getFirstDayOfMonth = (month, year) => {
    return new Date(year, month, 1).getDay();
  };

  const monthNames = [
    "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
  ];

  const renderCalendar = (monthOffset) => {
    const month = currentMonth - monthOffset;
    const year = currentYear;
    const daysInMonth = getDaysInMonth(month, year);
    const firstDay = (getFirstDayOfMonth(month, year) + 6) % 7;

    const days = [];
    
    for (let i = 0; i < firstDay; i++) {
      days.push(<div key={`empty-${i}`} className="calendar-day empty"></div>);
    }

    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(year, month, day);
      const dateStr = date.toISOString().split('T')[0];
      const isStart = dateStr === startDate;
      const isEnd = dateStr === endDate;
      const isInRange = startDate && endDate && dateStr > startDate && dateStr < endDate;
      const isFuture = date > today;

      let className = "calendar-day";
      if (isStart || isEnd) className += " selected";
      else if (isInRange) className += " in-range";
      else if (isFuture) className += " future";

      days.push(
        <div
          key={day}
          className={className}
          onClick={() => handleDateClick(dateStr, isFuture)}
        >
          {day}
        </div>
      );
    }

    return (
      <div className="calendar-month" key={monthOffset}>
        <h3 className="month-title">{monthNames[month]}, {year}</h3>
        <div className="calendar-grid">
          {days}
        </div>
      </div>
    );
  };

  const handleDateClick = (dateStr, isFuture) => {
    if (isFuture) return;

    if (!startDate || (startDate && endDate)) {
      setStartDate(dateStr);
      setEndDate(null);
    } else {
      if (dateStr < startDate) {
        setEndDate(startDate);
        setStartDate(dateStr);
      } else {
        setEndDate(dateStr);
      }
    }
  };

  const handleApply = () => {
    if (startDate && endDate) {
      onApply({ from: startDate, to: endDate });
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="date-modal" onClick={(e) => e.stopPropagation()}>
        <div className="date-modal-header">
          <h2 className="date-modal-title">Укажите период</h2>
          <button className="close-button" onClick={onClose}>
            <svg width="22" height="22" viewBox="0 0 22 22" fill="none">
              <path d="M5 5L17 17" stroke="black" strokeWidth="2" strokeLinecap="round"/>
              <path d="M17 5L5 17" stroke="black" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </button>
        </div>

        <div className="calendars-container">
          {renderCalendar(0)}
          {renderCalendar(1)}
        </div>

        <button className="apply-button" onClick={handleApply} disabled={!startDate || !endDate}>
          Выбрать
        </button>
      </div>
    </div>
  );
}

export default DateRangeModal;
