# HourPercentClock ⏱✨

A clean, modern, and interactive percent-based time visualization tool that shows:

- **Hour progress** (inner ring)
- **Day progress** (outer ring)
- **Daily remaining percentage**
- **Your total days alive**
- **Countdown to your next 100-day milestone**

Built with **Python + PySide6**, packaged via **PyInstaller**.

---

## 🌟 Features

### ⏳ Time Progress Rings
- Outer ring shows **day progress** (0–100%)
- Inner ring shows **hour progress**
- Smooth, anti-aliased circular indicators
- Always drawn as a perfect circle regardless of window shape

### 🎂 Birthday-Based Life Tracking
- User can choose their **birthday** via an integrated date picker
- Automatically calculates:
  - Total days alive  
  - Next “full hundred days” milestone  
  - Days left until the next milestone  
- Birthday is saved into a JSON config file (`hour_percent_clock_config.json`)
- App automatically loads the saved birthday on next launch

### 🌓 Two Display Modes
- **Detailed Mode**: All statistics + rings  
- **Simple Mode**: Minimalistic view  
- One-click toggle

### 💡 Smart UI / UX
- Light translucent "glass card" UI
- Drop shadow for depth
- Automatically updates time every second
- Clean layout and readable typography

---

## 📦 Installation (Source Version)

### 1. Install Dependencies

```bash
pip install PySide6
