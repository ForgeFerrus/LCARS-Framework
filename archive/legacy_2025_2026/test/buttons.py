# LCARS PADD :: ALL BUTTON FORMS AND COMPONENTS TEST
from __future__ import annotations

import sys
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from PyQt6.QtGui import QImage, QPainter, QColor
from PyQt6.QtCore import Qt

from lcars.base.type import LCARS
from lcars.base.interface import PADD
from lcars.base.component import LCARSButton, LCARSElbow, LCARSIndicator, LCARSBar, LCARSLabel
from lcars.base.default import Palette

Passed = 0
Failed = 0
Total = 0

def Check(Name, Condition, Detail=None):
    global Passed, Failed, Total
    Total += 1
    if Condition:
        Passed += 1
        print(f"[PASS] {Name}")
        if Detail is not None:
            print(f"       {Detail}")
        return True
    Failed += 1
    print(f"[FAIL] {Name}")
    if Detail is not None:
        print(f"       {Detail}")
    return False

def Main():
    print("=" * 68)
    print("LCARS PADD :: ALL BUTTON FORMS & PHYSICAL COMPONENTS TEST")
    print("=" * 68)

    app = LCARS.Application([])
    padd = PADD(Title="TACTICAL INTERFACE NCC-1701-D", Width=1280, Height=800)

    Check("PADD Created", padd is not None)
    Check("PADD Frameless Check", bool(padd.widget.windowFlags() & Qt.WindowType.FramelessWindowHint) is True)

    # Головний горизонтальний контейнер для розподілу на колонки
    columns_container = QWidget()
    columns_layout = QHBoxLayout(columns_container)
    columns_layout.setContentsMargins(12, 12, 12, 12)
    columns_layout.setSpacing(16)

    # -------------------------------------------------------------
    # КОЛОНКА 1: Основні форми (Rect, Pill, Soft, Elbow)
    # -------------------------------------------------------------
    col1 = QVBoxLayout()
    col1.setSpacing(10)
    col1.addWidget(LCARSLabel(Text="PRIMARY FORMS", Color=Palette.Buttons[0]).widget)

    btn_rect = LCARSButton(Text="SYS RECT", Form=LCARSButton.Rect, Number="01-4402", Color="#D07030", Width=180, Height=42)
    btn_pill = LCARSButton(Text="WARP PILL", Form=LCARSButton.Pill, Number="02-1088", Color="#CC8833", Width=180, Height=42)
    btn_soft = LCARSButton(Text="IMPULSE SOFT", Form=LCARSButton.Soft, Number="03-7740", Color="#AA6699", Width=180, Height=42)
    btn_elbow = LCARSButton(Text="FRAME ELBOW", Form=LCARSButton.Elbow, Number="04-9912", Color="#9977AA", Width=180, Height=54)

    col1.addWidget(btn_rect.widget)
    col1.addWidget(btn_pill.widget)
    col1.addWidget(btn_soft.widget)
    col1.addWidget(btn_elbow.widget)
    col1.addStretch()
    columns_layout.addLayout(col1)

    # -------------------------------------------------------------
    # КОЛОНКА 2: Зрізані пігулки (PillHalf) - 4 напрямки
    # -------------------------------------------------------------
    col2 = QVBoxLayout()
    col2.setSpacing(10)
    col2.addWidget(LCARSLabel(Text="PILL-HALF CUTS", Color=Palette.Buttons[1]).widget)

    btn_ph_0 = LCARSButton(Text="PH EAST 0", Form=LCARSButton.PillHalf, Direction=0, Number="05-10714", Color="#EE8833", Width=180, Height=42)
    btn_ph_90 = LCARSButton(Text="PH SOUTH 90", Form=LCARSButton.PillHalf, Direction=90, Number="06-3320", Color="#DD6622", Width=180, Height=42)
    btn_ph_180 = LCARSButton(Text="PH WEST 180", Form=LCARSButton.PillHalf, Direction=180, Number="07-4021", Color="#CC5511", Width=180, Height=42)
    btn_ph_270 = LCARSButton(Text="PH NORTH 270", Form=LCARSButton.PillHalf, Direction=270, Number="08-5519", Color="#BB4400", Width=180, Height=42)

    col2.addWidget(btn_ph_0.widget)
    col2.addWidget(btn_ph_90.widget)
    col2.addWidget(btn_ph_180.widget)
    col2.addWidget(btn_ph_270.widget)
    col2.addStretch()
    columns_layout.addLayout(col2)

    # -------------------------------------------------------------
    # КОЛОНКА 3: Зрізані soft-прямокутники (SoftHalf) - 4 напрямки
    # -------------------------------------------------------------
    col3 = QVBoxLayout()
    col3.setSpacing(10)
    col3.addWidget(LCARSLabel(Text="SOFT-HALF CUTS", Color=Palette.Buttons[2]).widget)

    btn_sh_0 = LCARSButton(Text="SH EAST 0", Form=LCARSButton.SoftHalf, Direction=0, Number="09-8801", Color="#995577", Width=180, Height=42)
    btn_sh_90 = LCARSButton(Text="SH SOUTH 90", Form=LCARSButton.SoftHalf, Direction=90, Number="10-1240", Color="#884466", Width=180, Height=42)
    btn_sh_180 = LCARSButton(Text="SH WEST 180", Form=LCARSButton.SoftHalf, Direction=180, Number="11-7650", Color="#773355", Width=180, Height=42)
    btn_sh_270 = LCARSButton(Text="SH NORTH 270", Form=LCARSButton.SoftHalf, Direction=270, Number="12-9011", Color="#662244", Width=180, Height=42)

    col3.addWidget(btn_sh_0.widget)
    col3.addWidget(btn_sh_90.widget)
    col3.addWidget(btn_sh_180.widget)
    col3.addWidget(btn_sh_270.widget)
    col3.addStretch()
    columns_layout.addLayout(col3)

    # -------------------------------------------------------------
    # КОЛОНКА 4: Індикатори та елементи стану
    # -------------------------------------------------------------
    col4 = QVBoxLayout()
    col4.setSpacing(10)
    col4.addWidget(LCARSLabel(Text="STATUS & SENSORS", Color=Palette.Buttons[3]).widget)

    ind_bar = LCARSIndicator(IndicatorType=LCARSIndicator.Bar, Color="#FF9900", Width=80, Height=24)
    ind_dot = LCARSIndicator(IndicatorType=LCARSIndicator.Dot, Color="#33CC99", Width=24, Height=24)
    ind_ring = LCARSIndicator(IndicatorType=LCARSIndicator.Ring, Color="#FF3333", Width=24, Height=24)
    ind_ph = LCARSIndicator(IndicatorType=LCARSIndicator.PillHalf, Color="#99CCFF", Width=60, Height=24)

    col4.addWidget(ind_bar.widget)
    col4.addWidget(ind_dot.widget)
    col4.addWidget(ind_ring.widget)
    col4.addWidget(ind_ph.widget)
    col4.addStretch()
    columns_layout.addLayout(col4)

    # Додаємо всю структуру колонок у PADD
    padd.addWidget(columns_container)

    Check("Columns Container Mounted to PADD", padd.Content.Layout.count() >= 1)

    # Перевірка сенсорних властивостей кнопок
    Check("Button Sensory Active", btn_rect.Sensory is True)
    btn_rect.OnClick()
    Check("Button Click State Update", btn_rect.State == "pressed")
    btn_rect.OnRelease()
    Check("Button Release State Update", btn_rect.State == "normal")

    # Перевірка індексів
    Check("Canonical Index 01-4402 Valid", btn_rect.GetNumber() == "01-4402")
    Check("Canonical Index 05-10714 Valid", btn_ph_0.GetNumber() == "05-10714")

    print("=" * 68)
    print("LCARS PADD :: ALL BUTTONS & COMPONENTS FINAL REPORT")
    print("=" * 68)
    print(f"TOTAL TESTS : {Total}")
    print(f"PASSED      : {Passed}")
    print(f"FAILED      : {Failed}")
    print("=" * 68)
    if Failed == 0:
        print("COMPONENTS STATUS : OPERATIONAL")
        print("OVERALL STATUS    : NOMINAL")
        return 0
    print("COMPONENTS STATUS : FAILED")
    return 1

if __name__ == "__main__":
    sys.exit(Main())
