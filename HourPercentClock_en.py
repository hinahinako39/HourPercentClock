# HourPercentClock_en.py
# -*- coding: utf-8 -*-
"""
Hour Percent Clock — International English Edition
Minimalist UI, ISO datetime, ISO birthday input,
Compact/Detailed modes, no card layout.
"""

import sys
import os
import json
from datetime import datetime, date
from math import ceil

from PySide6 import QtCore, QtGui, QtWidgets


# ====== Config Filename ======
CONFIG_FILENAME = "hour_percent_clock_config.json"


def get_config_path():
    base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.join(base_dir, CONFIG_FILENAME)


def load_birthdate_from_config():
    """Load birthday from JSON config. Return date or None."""
    cfg_path = get_config_path()
    if not os.path.exists(cfg_path):
        return None

    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        y, m, d = data.get("year"), data.get("month"), data.get("day")
        if all(isinstance(x, int) for x in (y, m, d)):
            bd = date(y, m, d)
            if bd <= date.today():
                return bd
        return None
    except Exception:
        return None


def save_birthdate_to_config(birthdate: date):
    """Write birthday into JSON"""
    cfg_path = get_config_path()
    data = {
        "year": birthdate.year,
        "month": birthdate.month,
        "day": birthdate.day
    }
    try:
        with open(cfg_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# ====== Time stats ======
def compute_time_stats(birthdate: date):
    """
    Return:
    now, hour_pct, day_pct, days_alive, next_hundred, days_to_next
    """
    now = datetime.now()

    # Hour percent
    sec_in_hour = now.minute * 60 + now.second + now.microsecond / 1_000_000
    hour_pct = sec_in_hour / 3600 * 100.0

    # Day percent
    sec_in_day = (
        now.hour * 3600 +
        now.minute * 60 +
        now.second +
        now.microsecond / 1_000_000
    )
    day_pct = sec_in_day / 86400 * 100.0

    # Days alive
    days_alive = (now.date() - birthdate).days
    if days_alive < 0:
        days_alive = 0

    # Next hundred milestone
    if days_alive == 0:
        next_hundred = 100
    else:
        next_hundred = ceil(days_alive / 100) * 100
        if next_hundred == days_alive:
            next_hundred += 100

    days_to_next = max(0, next_hundred - days_alive)

    return now, hour_pct, day_pct, days_alive, next_hundred, days_to_next


# ====== Ring Widget ======
class HourCircleWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._hour_percent = 0
        self._day_percent = 0

    def setPercents(self, hour_pct, day_pct):
        self._hour_percent = max(0, min(100, hour_pct))
        self._day_percent = max(0, min(100, day_pct))
        self.update()

    def sizeHint(self):
        return QtCore.QSize(240, 240)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        w, h = self.width(), self.height()
        margin = 8
        side = min(w, h) - margin * 2
        if side <= 0:
            return

        left = (w - side) / 2
        top = (h - side) / 2
        outer_rect = QtCore.QRectF(left, top, side, side)

        start_angle = int(90 * 16)  # 12 o'clock

        # ---- Day ring (outer)
        bg_pen = QtGui.QPen(QtGui.QColor("#d0d0d0"), 8)
        painter.setPen(bg_pen)
        painter.drawEllipse(outer_rect)

        day_span = int(-360 * 16 * (self._day_percent / 100))
        fg_pen = QtGui.QPen(QtGui.QColor("#3498db"), 8)
        painter.setPen(fg_pen)
        painter.drawArc(outer_rect, start_angle, day_span)

        # ---- Hour ring (inner)
        inner_margin = 16
        inner_rect = outer_rect.adjusted(
            inner_margin, inner_margin,
            -inner_margin, -inner_margin
        )

        bg2 = QtGui.QPen(QtGui.QColor("#e0e0e0"), 10)
        painter.setPen(bg2)
        painter.drawEllipse(inner_rect)

        hour_span = int(-360 * 16 * (self._hour_percent / 100))
        fg2 = QtGui.QPen(QtGui.QColor("#2ecc71"), 10)
        painter.setPen(fg2)
        painter.drawArc(inner_rect, start_angle, hour_span)

        # ---- Center text
        painter.setPen(QtGui.QColor("#333"))
        font = painter.font()
        font.setPointSize(14)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(self.rect(), QtCore.Qt.AlignCenter,
                         f"{self._hour_percent:0.2f}%")


# ====== Main Window ======
class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Hour Percent Clock — International Edition")
        self.mode = "detailed"

        # Background
        self.setStyleSheet("QWidget { background-color: #f4f4f6; }")

        # Birthday load
        bd = load_birthdate_from_config()
        self.birthdate = bd if bd else date(2001, 11, 14)

        # === Time label ===
        self.timeLabel = QtWidgets.QLabel("--:--:--")
        self.timeLabel.setAlignment(QtCore.Qt.AlignCenter)
        ft = self.timeLabel.font()
        ft.setPointSize(20)
        ft.setBold(True)
        self.timeLabel.setFont(ft)

        # === Circle ===
        self.circle = HourCircleWidget()

        # === Hour text ===
        self.hourText = QtWidgets.QLabel("Hour Progress: 0.00%")
        self.hourText.setAlignment(QtCore.Qt.AlignCenter)

        # === Day percent ===
        self.dayText = QtWidgets.QLabel("Day Progress: 0.00%")

        # === Day bar ===
        self.dayBar = QtWidgets.QProgressBar()
        self.dayBar.setRange(0, 10000)
        self.dayBar.setTextVisible(False)
        self.dayBar.setFixedHeight(20)

        self.dayBar.setStyleSheet("""
        QProgressBar {
            background-color: #e6e6e6;
            border: 1px solid #cccccc;
            border-radius: 8px;
        }
        QProgressBar::chunk {
            background-color: #2ecc71;
            border-radius: 8px;
        }
        """)

        # === Remaining today ===
        self.remainingLabel = QtWidgets.QLabel("Remaining Today: 100.00%")

        # === Days lived ===
        self.livedLabel = QtWidgets.QLabel("Days Alive: 0")

        # === Next milestone ===
        self.milestoneLabel = QtWidgets.QLabel("Next 100-Day Milestone: 0 days left")

        # === Birthday input (ISO) ===
        self.birthLabel = QtWidgets.QLabel("Your Birthday (YYYY-MM-DD):")

        self.birthEdit = QtWidgets.QDateEdit()
        self.birthEdit.setCalendarPopup(True)
        self.birthEdit.setDisplayFormat("yyyy-MM-dd")
        self.birthEdit.setDate(QtCore.QDate(
            self.birthdate.year,
            self.birthdate.month,
            self.birthdate.day
        ))
        self.birthEdit.setMaximumDate(QtCore.QDate.currentDate())
        self.birthEdit.dateChanged.connect(self.onBirthChanged)

        # === Toggle Detailed/Compact ===
        self.toggleBtn = QtWidgets.QPushButton("Switch to Compact Mode")
        self.toggleBtn.clicked.connect(self.toggleMode)

        # === Layout (International minimalist style) ===
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        layout.addWidget(self.timeLabel)
        layout.addWidget(self.circle, alignment=QtCore.Qt.AlignCenter)
        layout.addWidget(self.hourText)
        layout.addWidget(self.dayText)
        layout.addWidget(self.dayBar)
        layout.addWidget(self.remainingLabel)
        layout.addWidget(self.livedLabel)
        layout.addWidget(self.milestoneLabel)

        # Birthday Row
        birthRow = QtWidgets.QHBoxLayout()
        birthRow.addWidget(self.birthLabel)
        birthRow.addWidget(self.birthEdit)
        layout.addLayout(birthRow)

        layout.addWidget(self.toggleBtn, alignment=QtCore.Qt.AlignCenter)

        # Timer
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.updateClock)
        self.timer.start(1000)
        self.updateClock()

        self.resize(440, 620)

    # ==== Update Clock ====
    def updateClock(self):
        (now, hour_pct, day_pct, alive, next_h,
         left) = compute_time_stats(self.birthdate)

        weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][now.weekday()]
        iso_text = now.strftime(f"%Y-%m-%d {weekday} %H:%M:%S")
        self.timeLabel.setText(iso_text)

        # Rings
        self.circle.setPercents(hour_pct, day_pct)

        # Texts
        self.hourText.setText(f"Hour Progress: {hour_pct:0.2f}%")
        self.dayText.setText(f"Day Progress:  {day_pct:0.2f}%")
        self.dayBar.setValue(int(day_pct * 100))

        remaining = 100.0 - day_pct
        self.remainingLabel.setText(f"Remaining Today: {remaining:0.2f}%")

        self.livedLabel.setText(f"Days Alive: {alive}")
        self.milestoneLabel.setText(
            f"Next 100-Day Milestone: {left} days left"
        )

    # ==== On birthday change ====
    def onBirthChanged(self, qdate):
        self.birthdate = date(qdate.year(), qdate.month(), qdate.day())
        save_birthdate_to_config(self.birthdate)
        self.updateClock()

    # ==== Toggle Mode ====
    def toggleMode(self):
        if self.mode == "detailed":
            self.mode = "compact"
            self.remainingLabel.hide()
            self.livedLabel.hide()
            self.milestoneLabel.hide()
            self.birthLabel.hide()
            self.birthEdit.hide()
            self.toggleBtn.setText("Switch to Detailed Mode")
        else:
            self.mode = "detailed"
            self.remainingLabel.show()
            self.livedLabel.show()
            self.milestoneLabel.show()
            self.birthLabel.show()
            self.birthEdit.show()
            self.toggleBtn.setText("Switch to Compact Mode")


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
