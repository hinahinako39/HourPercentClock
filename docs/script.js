// ====== Utils for time & formatting ======

function pad2(n) {
  return n.toString().padStart(2, "0");
}

function getWeekdayShort(date) {
  const names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  let idx = date.getDay(); // 0-6 (Sun=0)
  if (idx === 0) idx = 7;
  return names[idx - 1];
}

function formatISODateTime(date) {
  const y = date.getFullYear();
  const m = pad2(date.getMonth() + 1);
  const d = pad2(date.getDate());
  const h = pad2(date.getHours());
  const min = pad2(date.getMinutes());
  const s = pad2(date.getSeconds());
  const weekday = getWeekdayShort(date);
  return `${y}-${m}-${d} (${weekday}) ${h}:${min}:${s}`;
}

function toStartOfDay(date) {
  const d = new Date(date);
  d.setHours(0, 0, 0, 0);
  return d;
}

// ====== DOM refs ======

const currentDatetimeEl = document.getElementById("currentDatetime");
const centerMainEl = document.getElementById("centerMain");
const centerSubEl = document.getElementById("centerSub");

const hourRingEl = document.getElementById("hourRing");
const dayRingEl = document.getElementById("dayRing");

const hourProgressTextEl = document.getElementById("hourProgressText");
const dayProgressTextEl = document.getElementById("dayProgressText");
const dayRemainingTextEl = document.getElementById("dayRemainingText");
const daysAliveTextEl = document.getElementById("daysAliveText");
const daysToNextMilestoneTextEl =
  document.getElementById("daysToNextMilestoneText");
const birthdayNoteEl = document.getElementById("birthdayNote");

const birthdayInputEl = document.getElementById("birthdayInput");
const modeToggleEl = document.getElementById("modeToggle");
const themeToggleEl = document.getElementById("themeToggle");

// SVG ring geometry
const hourRadius = 60;
const dayRadius = 80;
const hourCircumference = 2 * Math.PI * hourRadius;
const dayCircumference = 2 * Math.PI * dayRadius;

// Initialize stroke-dasharray
hourRingEl.style.strokeDasharray = `${hourCircumference} ${hourCircumference}`;
dayRingEl.style.strokeDasharray = `${dayCircumference} ${dayCircumference}`;

// ====== Birthday persistence ======

const BIRTHDAY_KEY = "hourPercentClock_birthday";

function loadBirthday() {
  const stored = localStorage.getItem(BIRTHDAY_KEY);
  if (!stored) return null;
  const date = new Date(stored + "T00:00:00");
  if (isNaN(date.getTime())) return null;
  return stored;
}

function saveBirthday(value) {
  if (!value) return;
  localStorage.setItem(BIRTHDAY_KEY, value);
}

// Set initial birthday input value
const initialBirthday = loadBirthday();
if (initialBirthday) {
  birthdayInputEl.value = initialBirthday;
}

// Handle birthday changes
birthdayInputEl.addEventListener("change", (e) => {
  const val = e.target.value; // "YYYY-MM-DD"
  if (val) {
    saveBirthday(val);
  }
});

// ====== Theme persistence (Dark / Light) ======

const THEME_KEY = "hourPercentClock_theme";

function applyTheme(theme) {
  if (theme === "light") {
    document.body.classList.add("light-theme");
  } else {
    document.body.classList.remove("light-theme");
  }
}

function loadTheme() {
  const stored = localStorage.getItem(THEME_KEY);
  if (stored === "light" || stored === "dark") {
    return stored;
  }
  return "dark";
}

function saveTheme(theme) {
  localStorage.setItem(THEME_KEY, theme);
}

// 初始化主题
const initialTheme = loadTheme();
applyTheme(initialTheme);
if (initialTheme === "light") {
  themeToggleEl.checked = true;
}

// 监听主题开关
themeToggleEl.addEventListener("change", (e) => {
  const theme = e.target.checked ? "light" : "dark";
  applyTheme(theme);
  saveTheme(theme);
});

// ====== Compact / Detailed mode ======

modeToggleEl.addEventListener("change", (e) => {
  if (e.target.checked) {
    document.body.classList.add("compact");
  } else {
    document.body.classList.remove("compact");
  }
});

// ====== Core update loop ======

function computeProgresses(now) {
  // Hour progress
  const startOfHour = new Date(now);
  startOfHour.setMinutes(0, 0, 0);
  const endOfHour = new Date(startOfHour);
  endOfHour.setHours(startOfHour.getHours() + 1);
  const hourTotalMs = endOfHour - startOfHour;
  const hourElapsedMs = now - startOfHour;
  const hourProgress = Math.min(
    Math.max(hourElapsedMs / hourTotalMs, 0),
    1
  );

  // Day progress
  const startOfDay = toStartOfDay(now);
  const endOfDay = new Date(startOfDay);
  endOfDay.setDate(startOfDay.getDate() + 1);
  const dayTotalMs = endOfDay - startOfDay;
  const dayElapsedMs = now - startOfDay;
  const dayProgress = Math.min(Math.max(dayElapsedMs / dayTotalMs, 0), 1);

  return { hourProgress, dayProgress };
}

function computeLifeStats(now) {
  const birthdayStr = birthdayInputEl.value || loadBirthday();
  if (!birthdayStr) return null;

  const birthday = new Date(birthdayStr + "T00:00:00");
  if (isNaN(birthday.getTime())) return null;

  const startOfToday = toStartOfDay(now);
  const diffMs = startOfToday - toStartOfDay(birthday);

  const daysAlive = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  if (daysAlive < 0) return null;

  const mod = daysAlive % 100;
  const daysToNext = mod === 0 ? 100 : 100 - mod;

  return { daysAlive, daysToNext };
}

function updateUI() {
  const now = new Date();

  // Datetime
  currentDatetimeEl.textContent = formatISODateTime(now);

  // Progress ratios
  const { hourProgress, dayProgress } = computeProgresses(now);

  const hourPct = hourProgress * 100;
  const dayPct = dayProgress * 100;
  const remainingPct = 100 - dayPct;

  // Update SVG rings
  const hourOffset = hourCircumference * (1 - hourProgress);
  const dayOffset = dayCircumference * (1 - dayProgress);
  hourRingEl.style.strokeDashoffset = hourOffset.toString();
  dayRingEl.style.strokeDashoffset = dayOffset.toString();

  // Center display: day progress as main
  centerMainEl.textContent = `${dayPct.toFixed(1)}%`;
  centerSubEl.textContent = "Day Progress";

  // Text stats
  hourProgressTextEl.textContent = `${hourPct.toFixed(1)}%`;
  dayProgressTextEl.textContent = `${dayPct.toFixed(1)}%`;
  dayRemainingTextEl.textContent = `${remainingPct.toFixed(1)}%`;

  // Life stats
  const lifeStats = computeLifeStats(now);
  if (lifeStats) {
    daysAliveTextEl.textContent = lifeStats.daysAlive.toString();
    daysToNextMilestoneTextEl.textContent =
      lifeStats.daysToNext.toString();
    birthdayNoteEl.style.display = "none";
  } else {
    daysAliveTextEl.textContent = "--";
    daysToNextMilestoneTextEl.textContent = "--";
    birthdayNoteEl.style.display = "block";
  }

  setTimeout(updateUI, 1000);
}

// Start loop
updateUI();
