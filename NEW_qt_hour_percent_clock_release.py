# NEW_qt_hour_percent_clock.py
# -*- coding: utf-8 -*-
"""
Qt Hour Percent Clock - Public Version

功能：
- 外环：Day 进度
- 内环：Hour 进度
- 中间：当前小时百分比
- 文本区：Day 百分比、今日剩余百分比、已生存天数、下一个整百天倒计时
- 用户可以通过日期选择控件设置自己的生日
- 生日会保存在同目录的 JSON 配置文件中，下次启动自动读取
"""

import sys
import os
import json
from datetime import datetime, date
from math import ceil

from PySide6 import QtCore, QtGui, QtWidgets

# ====== 配置文件相关 ======
CONFIG_FILENAME = "hour_percent_clock_config.json"


def get_config_path() -> str:
    """返回配置文件路径（与 exe / 脚本同目录）"""
    base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.join(base_dir, CONFIG_FILENAME)


def load_birthdate_from_config() -> date | None:
    """从配置文件中读取生日，如果失败则返回 None"""
    config_path = get_config_path()
    if not os.path.exists(config_path):
        return None

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        y, m, d = data.get("year"), data.get("month"), data.get("day")
        if not all(isinstance(x, int) for x in (y, m, d)):
            return None
        bd = date(y, m, d)
        # 如果生日在未来，就忽略这个配置
        if bd > date.today():
            return None
        return bd
    except Exception:
        return None


def save_birthdate_to_config(birthdate: date) -> None:
    """将生日保存到配置文件"""
    config_path = get_config_path()
    data = {"year": birthdate.year, "month": birthdate.month, "day": birthdate.day}
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        # 写入失败也不要影响程序运行
        pass


# ====== 核心时间计算逻辑 ======
def compute_time_stats(birthdate: date):
    """
    返回:
    - now: 当前时间 (datetime)
    - hour_pct: 当前小时已过百分比 (0-100)
    - day_pct: 当前日已过百分比 (0-100)
    - days_alive: 已生存天数
    - next_hundred: 下一个整百天(如 2500)
    - days_to_next: 距离下一个整百天的天数
    """
    now = datetime.now()

    # 小时百分比
    sec_in_hour = now.minute * 60 + now.second + now.microsecond / 1_000_000
    hour_pct = sec_in_hour / 3600.0 * 100.0

    # 天百分比
    sec_in_day = (
        now.hour * 3600
        + now.minute * 60
        + now.second
        + now.microsecond / 1_000_000
    )
    day_pct = sec_in_day / 86400.0 * 100.0

    # 已生存天数
    days_alive = (now.date() - birthdate).days
    if days_alive < 0:
        days_alive = 0

    # 下一个整百天
    if days_alive == 0:
        next_hundred = 100
    else:
        next_hundred = ceil(days_alive / 100) * 100
        if next_hundred == days_alive:
            next_hundred += 100
    days_to_next = max(0, next_hundred - days_alive)

    return now, hour_pct, day_pct, days_alive, next_hundred, days_to_next


class HourCircleWidget(QtWidgets.QWidget):
    """
    自定义控件：
    - 外环：Day 进度
    - 内环：Hour 进度
    - 中间文字：Hour 百分比
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._hour_percent = 0.0
        self._day_percent = 0.0

    def setPercents(self, hour_pct: float, day_pct: float):
        self._hour_percent = max(0.0, min(100.0, hour_pct))
        self._day_percent = max(0.0, min(100.0, day_pct))
        self.update()

    def sizeHint(self):
        return QtCore.QSize(240, 240)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        w = self.width()
        h = self.height()

        # 取宽高中较小的那一边，保证画的是正方形 → 正圆
        margin_outer = 8
        side = min(w, h) - 2 * margin_outer
        if side <= 0:
            return

        # 让正方形区域在控件中心
        left = (w - side) / 2
        top = (h - side) / 2
        outer_rect = QtCore.QRectF(left, top, side, side)
        outer_width = 8

        # Qt 角度系（从 12 点方向开始，顺时针为负角度）
        start_deg = 90
        start_angle = int(start_deg * 16)

        # --- 外环：Day 进度 ---
        bg_day_pen = QtGui.QPen(QtGui.QColor("#e0e0e0"), outer_width)
        painter.setPen(bg_day_pen)
        painter.drawEllipse(outer_rect)

        day_span_deg = -360 * (self._day_percent / 100.0)
        day_span_angle = int(day_span_deg * 16)
        day_pen = QtGui.QPen(QtGui.QColor("#3498db"), outer_width)
        painter.setPen(day_pen)
        painter.drawArc(outer_rect, start_angle, day_span_angle)

        # --- 内环：Hour 进度 ---
        inner_margin = 16
        inner_rect = outer_rect.adjusted(
            inner_margin, inner_margin, -inner_margin, -inner_margin
        )
        inner_width = 10

        bg_hour_pen = QtGui.QPen(QtGui.QColor("#dddddd"), inner_width)
        painter.setPen(bg_hour_pen)
        painter.drawEllipse(inner_rect)

        hour_span_deg = -360 * (self._hour_percent / 100.0)
        hour_span_angle = int(hour_span_deg * 16)
        hour_pen = QtGui.QPen(QtGui.QColor("#2ecc71"), inner_width)
        painter.setPen(hour_pen)
        painter.drawArc(inner_rect, start_angle, hour_span_angle)

        # --- 中间文字：Hour 百分比 ---
        painter.setPen(QtGui.QColor("#333333"))
        font = painter.font()
        font.setPointSize(14)
        font.setBold(True)
        painter.setFont(font)

        text = f"{self._hour_percent:0.2f}%"
        painter.drawText(self.rect(), QtCore.Qt.AlignCenter, text)


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Hour Percent Clock")
        self.mode = "detailed"

        # 默认背景色
        self.setStyleSheet("QWidget { background-color: #d6dde5; }")

        # ====== 读取生日配置，若无则用一个默认值 ======
        loaded_birthdate = load_birthdate_from_config()
        if loaded_birthdate is not None:
            self.birthdate = loaded_birthdate
        else:
            # 没有配置时的默认生日（可以改成你喜欢的默认值）
            self.birthdate = date(2001, 1, 1)

        # ====== 顶部时间标签 ======
        self.timeLabel = QtWidgets.QLabel("--:--:--")
        self.timeLabel.setAlignment(QtCore.Qt.AlignCenter)
        tfont = self.timeLabel.font()
        tfont.setPointSize(20)
        tfont.setBold(True)
        self.timeLabel.setFont(tfont)

        # ====== 圆环控件 ======
        self.circle = HourCircleWidget()

        # 小时文本
        self.hourTextLabel = QtWidgets.QLabel("Hour: 0.00%")
        self.hourTextLabel.setAlignment(QtCore.Qt.AlignCenter)

        # ====== 详细信息区域（可以整体隐藏） ======
        self.detailWidget = QtWidgets.QWidget()
        dlayout = QtWidgets.QVBoxLayout(self.detailWidget)
        dlayout.setSpacing(6)
        dlayout.setContentsMargins(0, 0, 0, 0)

        # --- 生日输入区域 ---
        birthLayout = QtWidgets.QHBoxLayout()
        birthLabel = QtWidgets.QLabel("你的生日：")
        self.birthDateEdit = QtWidgets.QDateEdit()
        self.birthDateEdit.setCalendarPopup(True)
        self.birthDateEdit.setDisplayFormat("yyyy-MM-dd")

        self.birthDateEdit.setDate(
            QtCore.QDate(self.birthdate.year, self.birthdate.month, self.birthdate.day)
        )
        self.birthDateEdit.setMaximumDate(QtCore.QDate.currentDate())
        self.birthDateEdit.dateChanged.connect(self.onBirthdateChanged)

        birthLayout.addWidget(birthLabel)
        birthLayout.addWidget(self.birthDateEdit)

        # Day 文本
        self.dayTextLabel = QtWidgets.QLabel("Day: 0.00%")

        # 今日剩余百分比
        self.remainingLabel = QtWidgets.QLabel("今日剩余：100.00%")

        # Day 进度条（加粗 + 圆角）
        self.dayBar = QtWidgets.QProgressBar()
        self.dayBar.setRange(0, 10000)
        self.dayBar.setTextVisible(False)
        self.dayBar.setFixedHeight(20)
        self.dayBar.setStyleSheet("""
        QProgressBar {
            border: 2px solid #cccccc;
            border-radius: 10px;
            background-color: #eeeeee;
        }
        QProgressBar::chunk {
            background-color: #2ecc71;
            border-radius: 10px;
        }
        """)

        # Life 天数
        self.lifeLabel = QtWidgets.QLabel("你已经在这个世界上待了：0 天")

        # 下一个整百天
        self.nextHundredLabel = QtWidgets.QLabel("距离你人生的第 0 天还有：0 天")

        # 布局顺序
        dlayout.addLayout(birthLayout)
        dlayout.addWidget(self.dayTextLabel)
        dlayout.addWidget(self.dayBar)
        dlayout.addWidget(self.remainingLabel)
        dlayout.addWidget(self.lifeLabel)
        dlayout.addWidget(self.nextHundredLabel)

        # ====== 模式切换按钮 ======
        self.toggleButton = QtWidgets.QPushButton("切换为简洁模式")
        self.toggleButton.clicked.connect(self.toggleMode)

        # ====== 毛玻璃卡片（外层） ======
        self.card = QtWidgets.QFrame()
        self.card.setObjectName("glassCard")
        card_layout = QtWidgets.QVBoxLayout(self.card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(12)

        # ====== 内部圆角小卡片：时间、Hour、详细信息 ======
        def make_section():
            f = QtWidgets.QFrame()
            f.setObjectName("sectionFrame")
            lay = QtWidgets.QVBoxLayout(f)
            lay.setContentsMargins(10, 8, 10, 8)
            lay.setSpacing(4)
            return f, lay

        # 时间卡片
        self.timeFrame, timeLay = make_section()
        timeLay.addWidget(self.timeLabel)

        # Hour 信息卡片
        self.hourFrame, hourLay = make_section()
        hourLay.addWidget(self.hourTextLabel)

        # 详细信息卡片
        self.detailFrame, detailLay = make_section()
        detailLay.addWidget(self.detailWidget)

        # 把内容放进大卡片
        card_layout.addWidget(self.timeFrame)
        card_layout.addWidget(self.circle, alignment=QtCore.Qt.AlignCenter)
        card_layout.addWidget(self.hourFrame)
        card_layout.addWidget(self.detailFrame)
        card_layout.addWidget(self.toggleButton, alignment=QtCore.Qt.AlignCenter)

        # 卡片样式
        self.card.setStyleSheet("""
        #glassCard {
            background-color: rgba(255, 255, 255, 210);
            border-radius: 18px;
        }
        #sectionFrame {
            background-color: rgba(255, 255, 255, 220);
            border-radius: 12px;
        }
        """)

        # 阴影效果
        shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 0)
        shadow.setColor(QtGui.QColor(0, 0, 0, 80))
        self.card.setGraphicsEffect(shadow)

        # ====== 主布局 ======
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.addWidget(self.card)

        # ====== 定时器 ======
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.updateClock)
        # 每秒刷新一次就够
        self.timer.start(1000)
        self.updateClock()

        # 初始窗口尺寸
        self.resize(420, 560)

    @QtCore.Slot()
    def updateClock(self):
        now, hour_pct, day_pct, days_alive, next_hundred, days_to_next = compute_time_stats(
            self.birthdate
        )

        # 显示日期 + 星期 + 时间
        weekday_map = ["一", "二", "三", "四", "五", "六", "日"]
        weekday_cn = weekday_map[now.weekday()]
        self.timeLabel.setText(
            now.strftime(f"%Y-%m-%d 周{weekday_cn}  %H:%M:%S")
        )

        # 内外环
        self.circle.setPercents(hour_pct, day_pct)
        self.hourTextLabel.setText(f"Hour: {hour_pct:0.2f}%")

        # Day 百分比 & 剩余
        self.dayTextLabel.setText(f"Day:  {day_pct:0.2f}%")
        self.dayBar.setValue(int(day_pct * 100))
        remaining_pct = max(0.0, 100.0 - day_pct)
        self.remainingLabel.setText(f"今日剩余：{remaining_pct:0.2f}%")

        # Life & 整百天
        self.lifeLabel.setText(f"你已经在这个世界上待了： {days_alive} 天")
        self.nextHundredLabel.setText(
            f"距离你人生的第 {next_hundred} 天还有： {days_to_next} 天"
        )

    @QtCore.Slot()
    def toggleMode(self):
        if self.mode == "detailed":
            self.mode = "simple"
            self.detailFrame.hide()
            self.toggleButton.setText("切换为详细模式")
        else:
            self.mode = "detailed"
            self.detailFrame.show()
            self.toggleButton.setText("切换为简洁模式")

    @QtCore.Slot(QtCore.QDate)
    def onBirthdateChanged(self, qdate: QtCore.QDate):
        """用户修改生日时回调"""
        self.birthdate = date(qdate.year(), qdate.month(), qdate.day())
        save_birthdate_to_config(self.birthdate)
        # 立即刷新一次
        self.updateClock()


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
