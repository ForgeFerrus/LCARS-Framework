#!/usr/bin/env python3
"""
KLINGON BATTLE STATION - REAL LCARS SYSTEM
Використовує справжній LCARS фреймворк для створення бойової станції
"""
import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from lcars.base.interface import LCARSApplication, LCARSScreen
from lcars.base.component import (
    Button1, Button2, Button3, Button4, Button5,
    Label1, Indicator1, Elbow1, Elbow2, Elbow3, Elbow4,
    Bracket1, Bracket2, Bar1, Bar2, Divider1, Component
)
from lcars.base.signal import Observer
from lcars.base.desktop import LCARSDesktop

class KlingonBattleStation(LCARSScreen):
    """Справжня клінгонська бойова станція на LCARS фреймворку"""
    
    def __init__(self):
        super().__init__(
            Title="IKV BORTAS - KLINGON BATTLE STATION",
            Color="#660000",
            Width=1400,
            Height=900
        )
        
        # Клінгонські системи
        self.weapons_online = False
        self.shields_raised = False
        self.cloak_engaged = False
        self.red_alert = False
        
        # Створюємо LCARS компоненти
        self.build_klingon_interface()
        
    def build_klingon_interface(self):
        """Будуємо справжній LCARS інтерфейс"""
        
        # Верхній хедер - Клінгонська імперія
        self.header = Label1(
            Text="tlhIngan wo' - IKV BORTAS",
            X=50, Y=20,
            Width=1300, Height=60,
            Color="#B8860B",
            FontSize=32
        )
        
        # Ліва панель - Системи зброї
        self.weapon_panel = self.create_weapon_panel()
        
        # Центральна панель - Тактичний дисплей
        self.tactical_panel = self.create_tactical_panel()
        
        # Права панель - Статус систем
        self.status_panel = self.create_status_panel()
        
        # Нижня панель - Управління
        self.control_panel = self.create_control_panel()
        
    def create_weapon_panel(self):
        """Панель систем зброї"""
        panel = Component()
        
        # Заголовок зброї
        panel.AddElement(Label1(
            Text="⚔️ WEAPONS SYSTEMS",
            X=50, Y=120,
            Width=300, Height=40,
            Color="#FF9900",
            FontSize=24
        ))
        
        # Фазери
        phasers = Button1(
            Text="PHASERS",
            X=50, Y=180,
            Width=280, Height=50,
            Color="#8B0000"
        )
        phasers.Clicked.Attach(self.fire_phasers)
        panel.AddElement(phasers)
        
        # Торпеди
        torpedoes = Button2(
            Text="PHOTON TORPEDOES",
            X=50, Y=250,
            Width=280, Height=50,
            Color="#8B0000"
        )
        torpedoes.Clicked.Attach(self.launch_torpedoes)
        panel.AddElement(torpedoes)
        
        # Дисраптор
        disruptor = Button3(
            Text="DISRUPTOR CANNON",
            X=50, Y=320,
            Width=280, Height=50,
            Color="#8B0000"
        )
        disruptor.Clicked.Attach(self.fire_disruptor)
        panel.AddElement(disruptor)
        
        # Індикатор статусу зброї
        self.weapon_status = Indicator1(
            Text="WEAPONS: STANDBY",
            X=50, Y=400,
            Width=280, Height=30,
            Color="#FFD700"
        )
        panel.AddElement(self.weapon_status)
        
        return panel
        
    def create_tactical_panel(self):
        """Тактична панель"""
        panel = Component()
        
        # Радарний дисплей
        panel.AddElement(Label1(
            Text="🎯 TACTICAL DISPLAY",
            X=400, Y=120,
            Width=600, Height=40,
            Color="#FF9900",
            FontSize=24
        ))
        
        # Індикатори цілей
        self.enemy_count = Indicator1(
            Text="ENEMY SHIPS: 0",
            X=400, Y=180,
            Width=280, Height=30,
            Color="#FFD700"
        )
        panel.AddElement(self.enemy_count)
        
        # Дистанція
        self.distance = Indicator1(
            Text="DISTANCE: --",
            X=700, Y=180,
            Width=300, Height=30,
            Color="#FFD700"
        )
        panel.AddElement(self.distance)
        
        # Статус бойових систем
        self.combat_status = Indicator1(
            Text="COMBAT SYSTEMS: ONLINE",
            X=400, Y=230,
            Width=600, Height=30,
            Color="#FFD700"
        )
        panel.AddElement(self.combat_status)
        
        # Сканер систем
        scanner = Button4(
            Text="SCAN FOR ENEMIES",
            X=400, Y=280,
            Width=280, Height=50,
            Color="#434343"
        )
        scanner.Clicked.Attach(self.scan_for_enemies)
        panel.AddElement(scanner)
        
        # Бойовий режим
        combat_mode = Button5(
            Text="COMBAT MODE",
            X=700, Y=280,
            Width=300, Height=50,
            Color="#8B0000"
        )
        combat_mode.Clicked.Attach(self.engage_combat_mode)
        panel.AddElement(combat_mode)
        
        return panel
        
    def create_status_panel(self):
        """Панель статусу систем"""
        panel = Component()
        
        # Заголовок статусу
        panel.AddElement(Label1(
            Text="🛡️ SHIP STATUS",
            X=1050, Y=120,
            Width=300, Height=40,
            Color="#FF9900",
            FontSize=24
        ))
        
        # Щити
        self.shields = Indicator1(
            Text="SHIELDS: 100%",
            X=1050, Y=180,
            Width=300, Height=30,
            Color="#FFD700"
        )
        panel.AddElement(self.shields)
        
        # Енергія
        self.power = Indicator1(
            Text="POWER: 100%",
            X=1050, Y=220,
            Width=300, Height=30,
            Color="#FFD700"
        )
        panel.AddElement(self.power)
        
        # Корпус
        self.hull = Indicator1(
            Text="HULL: 100%",
            X=1050, Y=260,
            Width=300, Height=30,
            Color="#FFD700"
        )
        panel.AddElement(self.hull)
        
        # Управління щитами
        raise_shields = Button1(
            Text="RAISE SHIELDS",
            X=1050, Y=320,
            Width=140, Height=40,
            Color="#434343"
        )
        raise_shields.Clicked.Attach(self.raise_shields)
        panel.AddElement(raise_shields)
        
        lower_shields = Button2(
            Text="LOWER SHIELDS",
            X=1200, Y=320,
            Width=140, Height=40,
            Color="#434343"
        )
        lower_shields.Clicked.Attach(self.lower_shields)
        panel.AddElement(lower_shields)
        
        # Маскуючий пристрій
        cloak = Button3(
            Text="ENGAGE CLOAK",
            X=1050, Y=380,
            Width=300, Height=40,
            Color="#434343"
        )
        cloak.Clicked.Attach(self.engage_cloak)
        panel.AddElement(cloak)
        
        return panel
        
    def create_control_panel(self):
        """Панель управління"""
        panel = Component()
        
        # Червона тривога
        red_alert = Button1(
            Text="🚨 RED ALERT",
            X=400, Y=750,
            Width=200, Height=50,
            Color="#8B0000"
        )
        red_alert.Clicked.Attach(self.toggle_red_alert)
        panel.AddElement(red_alert)
        
        # Комунікації
        comms = Button2(
            Text="📡 HAIL EMPIRE",
            X=620, Y=750,
            Width=200, Height=50,
            Color="#434343"
        )
        comms.Clicked.Attach(self.hail_empire)
        panel.AddElement(comms)
        
        # Самознищення
        self_destruct = Button3(
            Text="💀 SELF DESTRUCT",
            X=840, Y=750,
            Width=200, Height=50,
            Color="#8B0000"
        )
        self_destruct.Clicked.Attach(self.self_destruct)
        panel.AddElement(self_destruct)
        
        # Вихід
        exit_btn = Button4(
            Text="majQa' (EXIT)",
            X=50, Y=750,
            Width=150, Height=50,
            Color="#CD7F32"
        )
        exit_btn.Clicked.Attach(lambda: sys.exit(0))
        panel.AddElement(exit_btn)
        
        return panel
        
    # ==============================================================================
    # КЛІНГОНСЬКІ СИСТЕМНИЙ ФУНКЦІЇ
    # ==============================================================================
    
    def fire_phasers(self):
        """Вогонь з фазерів"""
        if not self.weapons_online:
            print("🔫 PHASERS CHARGING...")
            self.weapons_online = True
            self.weapon_status.Text = "WEAPONS: PHASERS CHARGED"
        else:
            print("🔫 PHASERS FIRING!")
            print("⚡ ENERGY BEAMS STRIKING ENEMY TARGETS!")
            self.weapon_status.Text = "WEAPONS: PHASERS FIRING"
            
    def launch_torpedoes(self):
        """Запуск торпед"""
        print("🚀 PHOTON TORPEDOES LAUNCHING!")
        print("💥 TORPEDOES TRACKING ENEMY TARGETS!")
        self.weapon_status.Text = "WEAPONS: TORPEDOES AWAY"
        
    def fire_disruptor(self):
        """Вогонь з дисраптора"""
        print("⚡ DISRUPTOR CANNON CHARGING...")
        print("💥 DISRUPTOR BLAST FIRING!")
        self.weapon_status.Text = "WEAPONS: DISRUPTOR ACTIVE"
        
    def scan_for_enemies(self):
        """Сканування ворогів"""
        import random
        enemy_count = random.randint(1, 5)
        distance = random.randint(20000, 80000)
        
        print(f"🔍 SCANNING FOR ENEMIES...")
        print(f"👁️ DETECTED {enemy_count} HOSTILE SHIPS")
        print(f"📏 DISTANCE: {distance:,} KM")
        
        self.enemy_count.Text = f"ENEMY SHIPS: {enemy_count}"
        self.distance.Text = f"DISTANCE: {distance:,} KM"
        
    def engage_combat_mode(self):
        """Бойовий режим"""
        print("⚔️ COMBAT MODE ENGAGED!")
        print("🛡️ ALL WEAPONS SYSTEMS ONLINE!")
        print("⚡ POWER DIVERTED TO COMBAT SYSTEMS!")
        
        self.weapons_online = True
        self.combat_status.Text = "COMBAT SYSTEMS: ENGAGED"
        self.weapon_status.Text = "WEAPONS: COMBAT READY"
        
    def raise_shields(self):
        """Підняти щити"""
        if not self.shields_raised:
            print("🛡️ SHIELDS RAISING!")
            print("⚡ SHIELDS AT 150% POWER!")
            self.shields_raised = True
            self.shields.Text = "SHIELDS: 150%"
            self.power.Text = "POWER: 85%"
        else:
            print("🛡️ SHIELDS ALREADY RAISED!")
            
    def lower_shields(self):
        """Опустити щити"""
        if self.shields_raised:
            print("🛡️ SHIELDS LOWERING!")
            print("⚡ POWER RESTORED TO NORMAL!")
            self.shields_raised = False
            self.shields.Text = "SHIELDS: 0%"
            self.power.Text = "POWER: 100%"
        else:
            print("🛡️ SHIELDS ALREADY LOWERED!")
            
    def engage_cloak(self):
        """Активувати маскуючий пристрій"""
        if self.shields_raised:
            print("❌ CANNOT ENGAGE CLOAK WITH SHIELDS UP!")
            return
            
        if not self.cloak_engaged:
            print("👻 CLOAKING DEVICE ENGAGING!")
            print("🌑 SHIP BECOMING INVISIBLE!")
            self.cloak_engaged = True
            self.power.Text = "POWER: 70%"
        else:
            print("👻 CLOAKING DEVICE DISENGAGING!")
            print("👁️ SHIP BECOMING VISIBLE!")
            self.cloak_engaged = False
            self.power.Text = "POWER: 100%"
            
    def toggle_red_alert(self):
        """Перемкнути червону тривогу"""
        if not self.red_alert:
            print("🚨 RED ALERT! RED ALERT!")
            print("⚠️ ALL HANDS TO BATTLE STATIONS!")
            print("🔥 CONDITION RED - ENEMY APPROACHING!")
            self.red_alert = True
            self.combat_status.Text = "COMBAT SYSTEMS: RED ALERT"
        else:
            print("✅ RED ALERT CANCELLED")
            print("🟢 CONDITION GREEN - ALL CLEAR")
            self.red_alert = False
            self.combat_status.Text = "COMBAT SYSTEMS: STANDBY"
            
    def hail_empire(self):
        """Зв'язок з Імперією"""
        print("📡 HAILING THE KLINGON HIGH COMMAND!")
        print("🏛️ TRANSMITTING BATTLE REPORT...")
        print("📜 REQUESTING REINFORCEMENTS...")
        print("🗡️ FOR THE HONOR AND GLORY OF THE EMPIRE!")
        
    def self_destruct(self):
        """Самознищення"""
        print("💀 SELF-DESTRUCT SEQUENCE INITIATED!")
        print("⏰ 60 SECOND COUNTDOWN STARTED!")
        print("🚨 ABANDON SHIP! ABANDON SHIP!")
        
        import time
        for i in range(60, 0, -10):
            print(f"⏰ {i} SECONDS REMAINING...")
            time.sleep(0.1)  # Швидко для демонстрації
            
        print("💥💥💥 BOOM! 💥💥💥")
        print("🗡️ Qapla'! (Victory in Death!)")
        sys.exit(0)

def main():
    """Запуск клінгонської бойової станції"""
    print("🔥🔥🔥 KLINGON BATTLE STATION INITIALIZING 🔥🔥🔥")
    print("⚔️⚔️⚔️ IKV BORTAS - LCARS SYSTEMS ONLINE ⚔️⚔️⚔️")
    print("🛡️🛡️🛡️ REAL LCARS FRAMEWORK ACTIVATED 🛡️🛡️🛡️")
    
    # Створюємо Qt додаток
    app = LCARSApplication(sys.argv)
    
    # Створюємо бойову станцію
    station = KlingonBattleStation()
    station.show()
    
    print("🚀🚀🚀 BATTLE STATION READY FOR COMBAT 🚀🚀🚀")
    print("🗡️🗡️🗡️ FOR THE HONOR OF THE EMPIRE! 🗡️🗡️🗡️")
    print("")
    print("Qapla'! (Success and Victory!)")
    
    # Запуск головного циклу
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
