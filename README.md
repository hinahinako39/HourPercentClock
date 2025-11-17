# HourPercentClock ⏱✨

A clean, modern, and interactive percent-based time visualization tool that shows:

* **Hour progress** (inner ring)
* **Day progress** (outer ring)
* **Daily remaining percentage**
* **Your total days alive**
* **Countdown to your next 100-day milestone**

Built with **Python + PySide6**, packaged via **PyInstaller**.

---

## 🌟 Features

### ⏳ Time Progress Rings

* Outer ring shows **day progress (0–100%)**
* Inner ring shows **hour progress**
* Smooth, anti-aliased circular indicators
* Always drawn as a perfect circle regardless of window shape

### 🎂 Birthday-Based Life Tracking

* User can choose their **birthday** via an integrated date picker
* Automatically calculates:

  * Total days alive
  * Next “full hundred days” milestone
  * Days left until the next milestone
* Birthday is saved into a JSON config file
  (`hour_percent_clock_config.json`)
* Automatically loads saved birthday on next launch

### 🌑 Two Display Modes

* **Detailed Mode** → All statistics + progress rings
* **Simple Mode** → Minimalistic interface
* One-click toggle button

### 💡 Smart UI / UX

* Light translucent “glass card” interface
* Drop shadow for depth
* Real-time updates every second
* Clean modern layout

---

## 📦 Installation (Source Version)

### 1. Install Dependencies

Make sure Python 3.12+ is installed.

Install PySide6:

```bash
pip install PySide6
```

### 2. Run the Application

```bash
python NEW_qt_hour_percent_clock_release.py
```

---

## 🛠 Build a Standalone Windows EXE

Requires Python 3.12 and PyInstaller.

### Install PyInstaller

```bash
py -3.12 -m pip install pyinstaller
```

### Build the EXE

```bash
py -3.12 -m PyInstaller --onefile --noconsole NEW_qt_hour_percent_clock_release.py
```

Your executable will be located at:

```
dist/HourPercentClock.exe
```

You can share this EXE with anyone —
**no Python installation needed**.

---

## 🗂 File Structure

```
HourPercentClock/
│
├── NEW_qt_hour_percent_clock_release.py   # Main application
├── hour_percent_clock_config.json         # Auto-generated config (ignored by git)
├── README.md                              # Documentation
├── LICENSE                                # MIT license
└── .gitignore                             # Git ignore rules
```

---

## 🔨 Tech Stack

* **Python 3.12**
* **PySide6 (Qt for Python)**
* **JSON Configuration Persistence**
* **PyInstaller for App Packaging**

---

## 📄 License

This project is licensed under the **MIT License**.

You are free to use, modify, and distribute the software.

---

## ⭐ Support

If you find this project useful, please consider giving it a ⭐ star!
Pull requests and suggestions are welcome.

---

## ✨ Author

Created by **hinahinako39**
