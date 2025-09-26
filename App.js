import React, { useEffect, useRef, useState } from "react";
import "./App.css";

// constants for your Aug-Dec semester (adjust if you want different range)
const MIN_MONTH = 7; // August (0 = Jan)
const MAX_MONTH = 11; // December

const msPerDay = 24 * 60 * 60 * 1000;

function dateOnly(d) {
  return new Date(d.getFullYear(), d.getMonth(), d.getDate());
}
function daysBetween(a, b) {
  return Math.round((dateOnly(b) - dateOnly(a)) / msPerDay);
}

const Calendar = () => {
  // start with a manually controlled date (you can change this)
  const [currentDate, setCurrentDate] = useState(new Date(2025, 7, 7)); // Aug 7, 2025

  // which month is being shown (0-11). default to month of currentDate (clamped to MIN..MAX)
  const [currentMonth, setCurrentMonth] = useState(() => {
    const m = currentDate.getMonth();
    return Math.min(MAX_MONTH, Math.max(MIN_MONTH, m));
  });

  // make calendar fill the width of the wrapper so one month fits perfectly
  const wrapperRef = useRef(null);
  const [wrapperWidth, setWrapperWidth] = useState(900);
  const [cellWidth, setCellWidth] = useState(40); // px per day (computed)

  useEffect(() => {
    function updateWidth() {
      if (!wrapperRef.current) return;
      const w = Math.floor(wrapperRef.current.clientWidth - 20); // padding allowance
      setWrapperWidth(w > 0 ? w : 800);
    }
    updateWidth();
    window.addEventListener("resize", updateWidth);
    return () => window.removeEventListener("resize", updateWidth);
  }, []);

  // when test date changes, make the calendar show that month (so blue line visible)
  useEffect(() => {
    const m = currentDate.getMonth();
    if (m >= MIN_MONTH && m <= MAX_MONTH) setCurrentMonth(m);
  }, [currentDate]);

  // month/day data (your semester)
  const monthNames = [
    "January","February","March","April","May","June","July",
    "August","September","October","November","December"
  ];
  // totalDays only for Aug-Dec (we'll index by month)
  const monthDaysMap = {
    7: 31, // Aug
    8: 30, // Sep
    9: 31, // Oct
    10: 30, // Nov
    11: 31 // Dec
  };

  const daysInMonth = monthDaysMap[currentMonth] ?? 30;

  // compute a cell width so daysInMonth * cellWidth fits wrapperWidth
  useEffect(() => {
    const minCell = 28;
    const maxCell = 120;
    const cw = Math.floor(wrapperWidth / daysInMonth);
    setCellWidth(Math.max(minCell, Math.min(maxCell, cw)));
  }, [wrapperWidth, daysInMonth]);

  // tasks (your provided format) — keep as-is
  const [tasks] = useState([
    { id: 1, startDate: new Date(2025, 7, 10), endDate: new Date(2025, 7, 15), title: "Assignment 1", description: "Finish problem set on algorithms." },
    { id: 2, startDate: new Date(2025, 8, 5), endDate: new Date(2025, 8, 12), title: "Project Review", description: "Team review meeting for software project." },
    { id: 3, startDate: new Date(2025, 9, 1), endDate: new Date(2025, 9, 7), title: "Midterm Exam", description: "Covers chapters 1–6. Study hard!" },
    { id: 4, startDate: new Date(2025, 10, 20), endDate: new Date(2025, 10, 28), title: "Final Project", description: "Submit final capstone project." },
    { id: 5, startDate: new Date(2025, 11, 10), endDate: new Date(2025, 11, 15), title: "Presentation", description: "End-of-semester group presentation." },
    { id: 6, startDate: new Date(2025, 7, 20), endDate: new Date(2025, 7, 22), title: "Quiz", description: "Quick check on week’s topics." },
    { id: 7, startDate: new Date(2025, 8, 15), endDate: new Date(2025, 9, 3), title: "Lab Report", description: "Submit detailed lab findings." },
    { id: 8, startDate: new Date(2025, 8, 25), endDate: new Date(2025, 8, 30), title: "Research Paper", description: "First draft due in more than a week." },
    { id: 9, startDate: new Date(2025, 8, 19), endDate: new Date(2025, 8, 21), title: "Coding Exercise", description: "Solve exercises before weekend deadline." },
    { id: 10, startDate: new Date(2025, 8, 15), endDate: new Date(2025, 8, 17), title: "Math Quiz", description: "Happening very soon – urgent prep needed." },
    { id: 11, startDate: new Date(2025, 8, 10), endDate: new Date(2025, 8, 13), title: "Missed Assignment", description: "Deadline already passed." },
    { id: 12, startDate: new Date(2025, 9, 5), endDate: new Date(2025, 9, 12), title: "Midterm Exam", description: "Covers chapters 1–6. Study hard!" },
    { id: 13, startDate: new Date(2025, 10, 20), endDate: new Date(2025, 10, 28), title: "Final Project", description: "Submit final capstone project." },
  ]);

  const [selectedTask, setSelectedTask] = useState(null);

  // helpers to compute rendering inside the displayed month
  const monthStart = new Date(currentDate.getFullYear(), currentMonth, 1);
  const monthEnd = new Date(currentDate.getFullYear(), currentMonth, daysInMonth);

  const getOverlapForMonth = (task) => {
    const taskStart = dateOnly(task.startDate);
    const taskEnd = dateOnly(task.endDate);

    const start = taskStart < monthStart ? monthStart : taskStart;
    const end = taskEnd > monthEnd ? monthEnd : taskEnd;

    if (end < start) return null; // no overlap with shown month

    const startIdx = daysBetween(monthStart, start); // 0-based
    const duration = daysBetween(start, end) + 1;
    return { startIdx, duration, start, end };
  };

  // color logic uses currentDate (manual) — keep class names that match your CSS
  const getTaskColor = (endDate) => {
    const daysLeft = Math.ceil((dateOnly(endDate) - dateOnly(currentDate)) / msPerDay);
    if (daysLeft > 7) return "task-green";
    if (daysLeft > 3) return "task-yellow";
    return "task-red";
  };

  // grid rendering sizes
  const headerHeight = 40;
  const bodyHeight = 260;
  const gridWidth = daysInMonth * cellWidth;

  return (
    <div className="calendar-page">
      <div className="controls">
        <button
          onClick={() => setCurrentMonth((m) => Math.max(MIN_MONTH, m - 1))}
          disabled={currentMonth <= MIN_MONTH}
        >
          ◀ Prev
        </button>

        <div className="month-label">
          {monthNames[currentMonth]} {monthStart.getFullYear()}
        </div>

        <button
          onClick={() => setCurrentMonth((m) => Math.min(MAX_MONTH, m + 1))}
          disabled={currentMonth >= MAX_MONTH}
        >
          Next ▶
        </button>

        <label className="date-input">
          Test date:
          <input
            type="date"
            value={dateOnly(currentDate).toISOString().split("T")[0]}
            onChange={(e) => {
              const d = new Date(e.target.value);
              setCurrentDate(d);
              // jump to that month so you see the line
              if (d.getMonth() >= MIN_MONTH && d.getMonth() <= MAX_MONTH) setCurrentMonth(d.getMonth());
            }}
          />
        </label>

        <div className="legend">
          <span className="legend-item"><span className="dot green" /> ≥ 7 days</span>
          <span className="legend-item"><span className="dot yellow" /> 4–7 days</span>
          <span className="legend-item"><span className="dot red" /> ≤ 3 days</span>
        </div>
      </div>

      <div className="calendar-wrapper" ref={wrapperRef}>
        {/* inner grid sized to show one month perfectly */}
        <div
          className="calendar-inner"
          style={{
            width: gridWidth,
            height: headerHeight + bodyHeight,
          }}
        >
          {/* header row (days across the entire inner width) */}
          <div
            className="month-header"
            style={{ height: headerHeight, lineHeight: `${headerHeight}px` }}
          >
            {monthNames[currentMonth]} {/* single month header */}
          </div>

          {/* day numbers */}
          {Array.from({ length: daysInMonth }).map((_, i) => (
            <div
              key={`d-${i}`}
              className="day-number"
              style={{
                left: i * cellWidth,
                top: headerHeight,
                width: cellWidth,
                height: 22,
                lineHeight: "22px",
              }}
            >
              {i + 1}
            </div>
          ))}

          {/* vertical day lines */}
          {Array.from({ length: daysInMonth }).map((_, i) => (
            <div
              key={`line-${i}`}
              className="day-line"
              style={{
                left: i * cellWidth,
                top: headerHeight,
                height: bodyHeight,
              }}
            />
          ))}

          {/* blue current-date marker (only show if date in this month) */}
          {currentDate.getMonth() === currentMonth && (
            <div
              className="current-date-marker"
              style={{
                left: (currentDate.getDate() - 1) * cellWidth,
                top: headerHeight,
                height: bodyHeight,
              }}
            />
          )}

          {/* tasks clipped/positioned to this month */}
          {tasks.map((task, idx) => {
            const overlap = getOverlapForMonth(task);
            if (!overlap) return null;

            const left = overlap.startIdx * cellWidth;
            const width = overlap.duration * cellWidth;
            const top = headerHeight + 28 + (idx % 8) * 28; // stack 8 per visual row then wrap (simple)
            const color = getTaskColor(task.endDate);

            return (
              <div
                key={task.id + "-" + idx}
                className={`task-bar ${color}`}
                style={{
                  left,
                  width,
                  top,
                }}
                onClick={() => setSelectedTask(task)}
                title={`${task.title} — ${task.startDate.toDateString()} → ${task.endDate.toDateString()}`}
              >
                {task.title}
              </div>
            );
          })}
        </div>
      </div>

      {/* modal */}
      {selectedTask && (
        <div className="modal-overlay" onClick={() => setSelectedTask(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>{selectedTask.title}</h3>
            <p><b>Start:</b> {selectedTask.startDate.toDateString()}</p>
            <p><b>End:</b> {selectedTask.endDate.toDateString()}</p>
            <p>{selectedTask.description}</p>
            <div style={{ textAlign: "right" }}>
              <button onClick={() => setSelectedTask(null)}>Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Calendar;
