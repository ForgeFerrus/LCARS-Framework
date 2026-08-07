# ◤ LCARS BASE DATABASE PANEL — LIBRARY COMPUTER DATABASE ACCESS
# Файл: lcars/ui/panels/database.py
# Призначення: Компонент доступу до бази даних бібліотечного комп'ютера LCARS.
# Опис логіки: Цей модуль забезпечує інтерфейс пошуку та перегляду даних,
#              завантажуючи інформацію про персонал, зоряні системи, історичні події,
#              технічні специфікації та архівні документи з локальної бази SQLite.
#              Розроблено за суворими стандартами Titanium без прямого використання PyQt/OS.

import sqlite3
from pathlib import Path

# Імпортуємо базові компоненти LCARS для побудови інтерфейсу без прямого виклику Qt
from lcars.base.default import Palette, FontStyle
from lcars.base.component import LCARSButton, LCARSElbow
from lcars.base.interface import LCARSContour
from lcars.base.type import Type
from lcars.modules.storage import ResolveChipPath

class LibraryPanel(Type.Panel):
    def __init__(self, Parent=None, Era=None, Faction=None):
        super().__init__(Parent)
        Self = self
        Self.Era = Era
        Self.Faction = Faction
        
        # Визначаємо шлях до бази даних 02.db в каталозі lcars/database
        # Використовуємо PathLib замість os, відповідно до вимог Titanium
        Self.DbPath = ResolveChipPath("LCARS Primary Database")
        Self.CurrentCategory = "PERSONNEL"
        Self.ActiveRecords = {} # Зберігає мапу відображуваного тексту на словник запису
        
        # Ініціалізуємо базу даних та графічний інтерфейс
        Self.EnsureDatabaseSchema()
        Self.BuildUi()
        Self.SelectCategory("PERSONNEL")

    def EnsureDatabaseSchema(self):
        # Відкриваємо з'єднання з базою даних SQLite
        # Створюємо таблиці та наповнюємо їх канонічним контентом, якщо вони порожні
        Self = self
        Conn = sqlite3.connect(str(Self.DbPath))
        Cursor = Conn.cursor()

        # Створення таблиці персоналу
        SqlPersonnel = (
            "CREATE TABLE IF NOT EXISTS personnel ("
            "id TEXT PRIMARY KEY, "
            "name TEXT, "
            "rank TEXT, "
            "faction TEXT, "
            "assignment TEXT, "
            "status TEXT, "
            "notes TEXT"
            ")"
        )
        Cursor.execute(SqlPersonnel)

        # Створення таблиці зоряних систем
        SqlStellar = (
            "CREATE TABLE IF NOT EXISTS stellar ("
            "id TEXT PRIMARY KEY, "
            "name TEXT, "
            "coordinates TEXT, "
            "sector TEXT, "
            "star_class TEXT, "
            "planets_count INTEGER, "
            "notes TEXT"
            ")"
        )
        Cursor.execute(SqlStellar)

        # Створення таблиці історичних подій
        SqlHistorical = (
            "CREATE TABLE IF NOT EXISTS historical ("
            "id TEXT PRIMARY KEY, "
            "stardate TEXT, "
            "event_name TEXT, "
            "description TEXT, "
            "key_figures TEXT"
            ")"
        )
        Cursor.execute(SqlHistorical)

        # Створення таблиці технічних систем
        SqlTechnical = (
            "CREATE TABLE IF NOT EXISTS technical ("
            "id TEXT PRIMARY KEY, "
            "system_name TEXT, "
            "category TEXT, "
            "specifications TEXT, "
            "status TEXT, "
            "details TEXT"
            ")"
        )
        Cursor.execute(SqlTechnical)

        # Створення таблиці архівних директив
        SqlArchive = (
            "CREATE TABLE IF NOT EXISTS archive ("
            "id TEXT PRIMARY KEY, "
            "title TEXT, "
            "category TEXT, "
            "author TEXT, "
            "stardate TEXT, "
            "content TEXT"
            ")"
        )
        Cursor.execute(SqlArchive)

        # Створення таблиці контактів
        SqlContacts = (
            "CREATE TABLE IF NOT EXISTS contacts ("
            "id TEXT PRIMARY KEY, "
            "name TEXT, "
            "faction TEXT, "
            "email TEXT, "
            "phone TEXT, "
            "notes TEXT"
            ")"
        )
        Cursor.execute(SqlContacts)

        # Наповнення даними, якщо таблиці порожні
        Cursor.execute("SELECT COUNT(*) FROM personnel")
        if Cursor.fetchone()[0] == 0:
            PersonnelData = [
                ("P1", "Jean-Luc Picard", "Admiral", "Starfleet", "Retired / Vineyards", "Inactive", "Legendary former Captain of the Enterprise NCC-1701-D/E."),
                ("P2", "William R. Riker", "Captain", "Starfleet", "U.S.S. Titan", "Active", "Bold commander with unparalleled tactical records."),
                ("P3", "Data", "Lt. Commander", "Starfleet", "U.S.S. Enterprise", "Deceased", "Advanced Soong-type android who sacrificed himself to save the crew."),
                ("P4", "Kathryn Janeway", "Admiral", "Starfleet", "Starfleet Command", "Active", "Brought U.S.S. Voyager back from the Delta Quadrant."),
                ("P5", "Seven of Nine", "Captain", "Starfleet", "U.S.S. Enterprise-G", "Active", "Former Borg drone, highly decorated command officer.")
            ]
            Cursor.executemany("INSERT INTO personnel VALUES (?,?,?,?,?,?,?)", PersonnelData)

        Cursor.execute("SELECT COUNT(*) FROM stellar")
        if Cursor.fetchone()[0] == 0:
            StellarData = [
                ("S1", "Sol System", "000-000-001", "Sector 001", "Class G", 8, "Capital sector of the United Federation of Planets."),
                ("S2", "Vulcan", "102-405-090", "Sector 40", "Class A", 1, "Home-world of logical Vulcans, major scientific hub."),
                ("S3", "Qo'noS (Kronos)", "402-901-203", "Sector 84", "Class M", 4, "Capital star system of the Klingon Empire."),
                ("S4", "Romulus", "789-012-005", "Romulan Sector", "Class M", 2, "Home-world of the Romulan Star Empire; destroyed in 2387 supernova."),
                ("S5", "Bajor", "506-112-909", "Denorios Belt", "Class M", 5, "Near the Bajoran Wormhole and Deep Space 9 station.")
            ]
            Cursor.executemany("INSERT INTO stellar VALUES (?,?,?,?,?,?,?)", StellarData)

        Cursor.execute("SELECT COUNT(*) FROM historical")
        if Cursor.fetchone()[0] == 0:
            HistoricalData = [
                ("H1", "43989.1", "Battle of Wolf 359", "Borg invasion resulting in the loss of 39 Starfleet vessels.", "Locutus of Borg, Admiral Hanson"),
                ("H2", "2063.04", "First Contact Day", "Zefram Cochrane's first successful warp flight attracting Vulcans.", "Zefram Cochrane, Phoenix Crew"),
                ("H3", "45230.5", "Khitomer Accords", "Peace treaty signed between the Federation and the Klingon Empire.", "Chancellor Gorkon, Captain Kirk"),
                ("H4", "50564.0", "Dominion War", "Federation-wide conflict against the Dominion and Cardassian alliance.", "Captain Sisko, Admiral Ross"),
                ("H5", "58349.2", "Romulan Supernova", "Supernova cataclysm destroying Romulus and altering alpha quadrant politics.", "Ambassador Spock, Admiral Picard")
            ]
            Cursor.executemany("INSERT INTO historical VALUES (?,?,?,?,?)", HistoricalData)

        Cursor.execute("SELECT COUNT(*) FROM technical")
        if Cursor.fetchone()[0] == 0:
            TechnicalData = [
                ("T1", "Warp Drive", "Propulsion", "Multi-spectral warp field coils", "Stable", "Generates a warp bubble to traverse space at FTL velocities."),
                ("T2", "Transporter", "Transportation", "Quantum-level matter stream resolver", "Online", "Dematerializes matter and beams it safely over long distances."),
                ("T3", "Phaser Array", "Tactical", "Pulse-compressed nadion emitters", "Charged", "Standard defensive particle energy weapon array."),
                ("T4", "Deflector Shields", "Defense", "Gravimetric distortion shield grids", "Optimal", "Protects the vessel from physical particles and energy fire."),
                ("T5", "Isolinear Core", "Computing", "Optical sub-processor matrix network", "Optimized", "Main processing and storage computer system on Starfleet ships.")
            ]
            Cursor.executemany("INSERT INTO technical VALUES (?,?,?,?,?,?)", TechnicalData)

        Cursor.execute("SELECT COUNT(*) FROM archive")
        if Cursor.fetchone()[0] == 0:
            ArchiveData = [
                ("A1", "Prime Directive", "Regulation", "Federation Council", "1024.1", "Starfleet General Order 1: Non-interference with pre-warp societies."),
                ("A2", "Omega Directive", "Classified", "Starfleet Command", "45230.1", "Emergency mandate instructing captains to eliminate any trace of Omega particles."),
                ("A3", "Treaty of Algeron", "Diplomatic", "Federation-Romulan", "2311.0", "Diplomatic agreement banning Federation cloaking technology research."),
                ("A4", "Borg Intelligence Files", "Security", "Starfleet Intelligence", "41254.9", "Comprehensive documentation on Borg adaptation, cubes, and transwarp cores.")
            ]
            Cursor.executemany("INSERT INTO archive VALUES (?,?,?,?,?,?)", ArchiveData)

        Cursor.execute("SELECT COUNT(*) FROM contacts")
        if Cursor.fetchone()[0] == 0:
            ContactsData = [
                ("C1", "Spock", "Vulcan Science Academy", "spock@academy.vul", "402-1200", "Scientific advisor, legendary Ambassador."),
                ("C2", "Worf", "Starfleet Security", "worf@enterprise.fed", "1701-E", "Lt. Commander, Klingon ambassadorial liaison."),
                ("C3", "Geordi La Forge", "Engineering Core", "laforge@enterprise.fed", "1701-D", "Chief Engineer of U.S.S. Enterprise-D.")
            ]
            Cursor.executemany("INSERT INTO contacts VALUES (?,?,?,?,?,?)", ContactsData)

        Conn.commit()
        Conn.close()

    def BuildUi(self):
        # Конструювання інтерфейсу бази даних
        Self = self
        Self.setStyleSheet("background-color: black;")
        
        # Головний горизонтальний макет
        MainLayout = Type.HMatrix(Self)
        MainLayout.setContentsMargins(10, 10, 10, 10)
        MainLayout.setSpacing(15)

        # --- ЛІВА ПАНЕЛЬ: КАТЕГОРІЇ ТА НАВІГАЦІЯ ---
        LeftCtrl = Type.VMatrix()
        LeftCtrl.setSpacing(5)

        # Кутовий елемент LCARSElbow
        ElbowL = LCARSElbow("top-left", Color=Palette.Buttons[5])
        ElbowL.setMinimumSize(180, 60)
        LeftCtrl.addWidget(ElbowL.Widget)

        # Заголовок бази даних
        LblDb = Type.Indicator("DATABASE ACCESS", Self)
        LblDb.setStyleSheet("color: " + Palette.Buttons[4] + "; " + FontStyle(18, "normal"))
        LeftCtrl.addWidget(LblDb)

        # Категорії даних
        Self.Categories = ["PERSONNEL", "STELLAR", "HISTORICAL", "TECHNICAL", "ARCHIVE", "CONTACTS"]
        Self.CategoryButtons = {}
        
        # Створення кнопок категорії з різними кольорами з палітри
        for Index, Cat in enumerate(Self.Categories):
            BtnColor = Palette.Buttons[Index % len(Palette.Buttons)]
            Btn = LCARSButton(Cat, BtnColor, shape="left")
            Btn.setMinimumHeight(40)
            
            # Підключаємо обробник події кліку
            # Використовуємо лямбду для безпечної передачі категорії
            Btn.clicked.connect(Self.CreateCategoryCallback(Cat))
            
            LeftCtrl.addWidget(Btn.Widget)
            Self.CategoryButtons[Cat] = Btn

        LeftCtrl.addStretch()

        # Кнопка терміналу безпеки
        BtnOff = LCARSButton("SECURE TERMINAL", Palette.Buttons[0], shape="left")
        BtnOff.setMinimumHeight(50)
        LeftCtrl.addWidget(BtnOff.Widget)

        MainLayout.addLayout(LeftCtrl)

        # --- ЦЕНТРАЛЬНА ПАНЕЛЬ: ПОШУК ТА СПИСОК РЕЗУЛЬТАТІВ ---
        CenterArea = Type.VMatrix()
        
        # Створюємо стильну контурну плашку для пошукової стрічки
        Head = LCARSContour(Color=Palette.Buttons[0], height=30)
        HLay = Type.HMatrix(Head.Widget)
        Self.LblHead = Type.Indicator("SEARCH ENGINE // LIBRARY COMPUTER", Head.Widget)
        Self.LblHead.setStyleSheet("color: black; " + FontStyle(14, "normal"))
        HLay.addWidget(Self.LblHead)
        CenterArea.addWidget(Head.Widget)

        # Рядок пошуку Input
        Self.SearchInput = Type.Input()
        Self.SearchInput.setPlaceholderText("ENTER SEARCH QUERY...")
        Self.SearchInput.setStyleSheet(
            "background: black; color: white; border: 1px solid " + Palette.Buttons[1] + "; "
            "padding: 10px; " + FontStyle(12, "normal")
        )
        Self.SearchInput.textChanged.connect(Self.PerformSearch)
        CenterArea.addWidget(Self.SearchInput)

        # Список результатів Manifest
        Self.ResultsList = Type.Manifest()
        ListStyle = (
            "QListWidget {"
            "background: black; color: " + Palette.Buttons[2] + "; border: 1px solid " + Palette.Buttons[3] + "; "
            "border-radius: 10px; padding: 10px; " + FontStyle(12, "normal") + " "
            "}"
            "QListWidget::item { border-bottom: 1px solid " + Palette.Buttons[8] + "; padding: 8px; }"
            "QListWidget::item:selected { background-color: " + Palette.Buttons[4] + "; color: black; }"
        )
        Self.ResultsList.setStyleSheet(ListStyle)
        Self.ResultsList.itemClicked.connect(Self.OnItemClicked)
        CenterArea.addWidget(Self.ResultsList, 1)

        MainLayout.addLayout(CenterArea, 1)

        # --- ПРАВА ПАНЕЛЬ: ДЕТАЛЬНА ІНФОРМАЦІЯ ---
        Self.RightLayout = Type.VMatrix()

        # Праве верхнє коліно LCARSElbow
        ElbowR = LCARSElbow("top-right", Color=Palette.Buttons[4])
        ElbowR.setMinimumSize(180, 60)
        Self.RightLayout.addWidget(ElbowR.Widget, alignment=Type.Directive.AlignmentFlag.AlignRight)

        # Панель для відображення деталей
        Self.DetailsBox = Type.Panel()
        Self.DetailsBox.setStyleSheet(
            "background: #020202; border: 1px solid " + Palette.Buttons[2] + "; "
            "border-radius: 10px; padding: 12px;"
        )
        Self.DetailsLayout = Type.VMatrix(Self.DetailsBox)
        
        # Заголовок деталей
        Self.DetailsTitle = Type.Indicator("◤ SYSTEM ACCESS", Self.DetailsBox)
        Self.DetailsTitle.setStyleSheet("color: " + Palette.Buttons[2] + "; " + FontStyle(16, "bold") + ";")
        Self.DetailsLayout.addWidget(Self.DetailsTitle)
        
        # Текст деталей
        Self.DetailsText = Type.Indicator("Select an item in the search matrix to retrieve isolinear records.", Self.DetailsBox)
        Self.DetailsText.setWordWrap(True)
        Self.DetailsText.setStyleSheet("color: white; " + FontStyle(12, "normal") + ";")
        Self.DetailsLayout.addWidget(Self.DetailsText, 1)

        Self.RightLayout.addWidget(Self.DetailsBox, 1)
        
        MainLayout.addLayout(Self.RightLayout)

    def CreateCategoryCallback(self, CategoryName):
        # Повертає функцію зворотного виклику для вибору категорії
        Self = self
        def Callback():
            Self.SelectCategory(CategoryName)
        return Callback

    def SelectCategory(self, CategoryName):
        # Встановлює поточну обрану категорію
        Self = self
        Self.CurrentCategory = CategoryName
        Self.LblHead.setText("SEARCH ENGINE // CATEGORY: " + str(CategoryName))
        
        # Візуально виділяємо активну кнопку
        for Cat, Btn in Self.CategoryButtons.items():
            if Cat == CategoryName:
                Btn.setStyleSheet("background-color: " + Palette.Buttons[4] + "; color: black;")
            else:
                Btn.setStyleSheet("background-color: " + Palette.Buttons[1] + "; color: black;")

        # Виконуємо пошук за новою категорією
        Self.PerformSearch()

    def PerformSearch(self):
        # Запит до бази даних за текстовим фільтром
        Self = self
        QueryText = Self.SearchInput.text().strip().lower()
        Self.ResultsList.clear()
        Self.ActiveRecords.clear()

        Conn = sqlite3.connect(str(Self.DbPath))
        Cursor = Conn.cursor()
        
        TableName = Self.CurrentCategory.lower()
        
        if TableName == "personnel":
            Cursor.execute("SELECT id, name, rank, faction, assignment, status, notes FROM personnel")
            Rows = Cursor.fetchall()
            for R in Rows:
                Record = {"id": R[0], "name": R[1], "rank": R[2], "faction": R[3], "assignment": R[4], "status": R[5], "notes": R[6]}
                if not QueryText or QueryText in Record["name"].lower() or QueryText in Record["rank"].lower() or QueryText in Record["assignment"].lower():
                    DisplayText = str(Record['rank']).upper() + " " + str(Record['name']).upper() + " [" + str(Record['faction']).upper() + "]"
                    Self.ActiveRecords[DisplayText] = Record
                    Self.ResultsList.addItem(DisplayText)

        elif TableName == "stellar":
            Cursor.execute("SELECT id, name, coordinates, sector, star_class, planets_count, notes FROM stellar")
            Rows = Cursor.fetchall()
            for R in Rows:
                Record = {"id": R[0], "name": R[1], "coordinates": R[2], "sector": R[3], "star_class": R[4], "planets_count": R[5], "notes": R[6]}
                if not QueryText or QueryText in Record["name"].lower() or QueryText in Record["sector"].lower():
                    DisplayText = "SYSTEM: " + str(Record['name']).upper() + " // " + str(Record['coordinates'])
                    Self.ActiveRecords[DisplayText] = Record
                    Self.ResultsList.addItem(DisplayText)

        elif TableName == "historical":
            Cursor.execute("SELECT id, stardate, event_name, description, key_figures FROM historical")
            Rows = Cursor.fetchall()
            for R in Rows:
                Record = {"id": R[0], "stardate": R[1], "event_name": R[2], "description": R[3], "key_figures": R[4]}
                if not QueryText or QueryText in Record["event_name"].lower() or QueryText in Record["key_figures"].lower():
                    DisplayText = "SD " + str(Record['stardate']) + " // " + str(Record['event_name']).upper()
                    Self.ActiveRecords[DisplayText] = Record
                    Self.ResultsList.addItem(DisplayText)

        elif TableName == "technical":
            Cursor.execute("SELECT id, system_name, category, specifications, status, details FROM technical")
            Rows = Cursor.fetchall()
            for R in Rows:
                Record = {"id": R[0], "system_name": R[1], "category": R[2], "specifications": R[3], "status": R[4], "details": R[5]}
                if not QueryText or QueryText in Record["system_name"].lower() or QueryText in Record["category"].lower():
                    DisplayText = str(Record['system_name']).upper() + " // STATUS: " + str(Record['status']).upper()
                    Self.ActiveRecords[DisplayText] = Record
                    Self.ResultsList.addItem(DisplayText)

        elif TableName == "archive":
            Cursor.execute("SELECT id, title, category, author, stardate, content FROM archive")
            Rows = Cursor.fetchall()
            for R in Rows:
                Record = {"id": R[0], "title": R[1], "category": R[2], "author": R[3], "stardate": R[4], "content": R[5]}
                if not QueryText or QueryText in Record["title"].lower() or QueryText in Record["category"].lower() or QueryText in Record["content"].lower():
                    DisplayText = "DOC: " + str(Record['title']).upper() + " (" + str(Record['category']).upper() + ")"
                    Self.ActiveRecords[DisplayText] = Record
                    Self.ResultsList.addItem(DisplayText)

        elif TableName == "contacts":
            Cursor.execute("SELECT id, name, faction, email, phone, notes FROM contacts")
            Rows = Cursor.fetchall()
            for R in Rows:
                Record = {"id": R[0], "name": R[1], "faction": R[2], "email": R[3], "phone": R[4], "notes": R[5]}
                if not QueryText or QueryText in Record["name"].lower() or QueryText in Record["faction"].lower():
                    DisplayText = "CONTACT: " + str(Record['name']).upper() + " // " + str(Record['faction'])
                    Self.ActiveRecords[DisplayText] = Record
                    Self.ResultsList.addItem(DisplayText)

        Conn.close()

    def OnItemClicked(self, Item):
        # Показ детальних записів про вибраний елемент
        Self = self
        DisplayText = Item.text()
        Record = Self.ActiveRecords.get(DisplayText)
        if not Record:
            return

        Self.DetailsTitle.setText("◤ " + str(Self.CurrentCategory).upper() + " RECORD")

        DetailText = ""
        TableName = Self.CurrentCategory.lower()
        
        if TableName == "personnel":
            DetailText = (
                "<b>Name:</b> " + str(Record['name']) + "<br>"
                "<b>Rank:</b> " + str(Record['rank']) + "<br>"
                "<b>Faction:</b> " + str(Record['faction']) + "<br>"
                "<b>Assignment:</b> " + str(Record['assignment']) + "<br>"
                "<b>Status:</b> <span style='color: #FF9900;'>" + str(Record['status']) + "</span><br><br>"
                "<b>System Bio:</b><br>" + str(Record['notes'])
            )

        elif TableName == "stellar":
            DetailText = (
                "<b>Sector:</b> " + str(Record['name']) + "<br>"
                "<b>Coordinates:</b> " + str(Record['coordinates']) + "<br>"
                "<b>Grid Sector:</b> " + str(Record['sector']) + "<br>"
                "<b>Star Class:</b> " + str(Record['star_class']) + "<br>"
                "<b>Surveyed Planets:</b> " + str(Record['planets_count']) + "<br><br>"
                "<b>Stellar Log:</b><br>" + str(Record['notes'])
            )

        elif TableName == "historical":
            DetailText = (
                "<b>Stardate:</b> " + str(Record['stardate']) + "<br>"
                "<b>Historical Event:</b> " + str(Record['event_name']) + "<br>"
                "<b>Key Figures:</b> " + str(Record['key_figures']) + "<br><br>"
                "<b>Chronicle Description:</b><br>" + str(Record['description'])
            )

        elif TableName == "technical":
            DetailText = (
                "<b>Sub-system:</b> " + str(Record['system_name']) + "<br>"
                "<b>Category:</b> " + str(Record['category']) + "<br>"
                "<b>Specs:</b> " + str(Record['specifications']) + "<br>"
                "<b>Chassis Status:</b> <span style='color: #00FF00;'>" + str(Record['status']) + "</span><br><br>"
                "<b>Operations:</b><br>" + str(Record['details'])
            )

        elif TableName == "archive":
            DetailText = (
                "<b>Document:</b> " + str(Record['title']) + "<br>"
                "<b>Classification:</b> " + str(Record['category']) + "<br>"
                "<b>Source/Author:</b> " + str(Record['author']) + "<br>"
                "<b>Temporal Stamp:</b> SD " + str(Record['stardate']) + "<br><br>"
                "<b>Archive Text:</b><br>" + str(Record['content'])
            )

        elif TableName == "contacts":
            DetailText = (
                "<b>Contact name:</b> " + str(Record['name']) + "<br>"
                "<b>Sub-faction:</b> " + str(Record['faction']) + "<br>"
                "<b>Subspace Email:</b> " + str(Record['email']) + "<br>"
                "<b>ODN Channel:</b> " + str(Record['phone']) + "<br><br>"
                "<b>Personal Notes:</b><br>" + str(Record['notes'])
            )

        Self.DetailsText.setText(DetailText)
