# ◤ TITANIUM LINGUISTIC MATRIX
# LCARS Framework :: LINGUISTIC_CORE // TRANSLATION_ENGINE // NO_Q PROTOCOL
# ОПИС: Ядро перекладу, словника та лінгвістичного аналізу (ISO-03).
# ФУНКЦІЇ: Фракційні шрифти, мультімовна підтримка та словник федерації.
# СТАНДАРТ: Titanium CamelCase (Повна заборона нижніх підкреслювань).
# ВЕРСІЯ: Делегована з lcars.base.version

from __future__ import annotations
from typing import Optional, List, Dict, Any, Union

# Імпорт системних типів Titanium Master
from lcars.base.type import SystemComponent, Directive
from lcars.base.version import getVersion
from lcars.system.localization import LOCALIZATION as Language
from lcars.engineering.isolinear import IsolinearChip

__version__ = getVersion()

# Адаптер менеджеру шрифтів для завантаження шрифтів за мовою та фракцією
class FontManagerAdapter:
    
    # Ініціалізація адаптера менеджеру шрифтів
    def __init__(self, ManagerNode):
        self.Manager = ManagerNode
        self.Fonts = {"lcars": "LCARS"}

    # Завантаження шрифту за ключем мови
    def LoadFont(self, Key: str):
        LangFont = self.Manager.LoadFontByLanguage(Key)
        if LangFont:
            return LangFont
        return self.Manager.LoadFontByFaction(Key)

Adapter = FontManager(Node)

# ── 1. ЛІНГВІСТИЧНИЙ ЧІП (TITANIUM ISO-03) ──

# Спеціалізований вузол словника Titanium
class LinguisticChip(IsolinearChip):
    # Спеціалізований вузол словника Titanium.
    def __init__(self):
        super().__init__('03', '03.db')
        self.InitializeMatrixSchema()

    # Ініціалізація схеми матриці лінгвістичних даних
    def InitializeMatrixSchema(self):
        # Реставрація повної схеми Titanium-рівня (Zero-Underscore)
        if not self.Connect():
            return

        MatrixConn = self.Connection
        if MatrixConn:
            CursorNode = MatrixConn.cursor()
            CursorNode.execute('CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, level TEXT)')
            CursorNode.execute('''CREATE TABLE IF NOT EXISTS vocabulary (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                english TEXT, 
                ukrainian TEXT, 
                frequency INTEGER DEFAULT 0,
                level TEXT DEFAULT 'A1',
                faction TEXT DEFAULT 'federation'
            )''')
            
            CursorNode.execute('''CREATE TABLE IF NOT EXISTS phrases (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                english TEXT, 
                ukrainian TEXT,
                context TEXT,
                faction TEXT DEFAULT 'federation'
            )''')
            CursorNode.execute('CREATE TABLE IF NOT EXISTS grammar_rules (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, rule_text TEXT, level TEXT)')
            CursorNode.execute('CREATE TABLE IF NOT EXISTS user_progress (id INTEGER PRIMARY KEY AUTOINCREMENT, item_id INTEGER, mastery INTEGER DEFAULT 0)')
            
            MatrixConn.commit()

# ── 2. ЛІНГВІСТИЧНА МАТРИЦЯ (TITANIUM SERVICE) ──

# Базові мови та їх властивості в Titanium Matrix
class LinguisticMatrix(SystemComponent):
    # Базові мови та їх властивості в Titanium Matrix
    BaseLanguagesMap = {
        "en": {"name": "English", "font": None, "keyboard": "qwerty"},
        "ua": {"name": "Українська", "font": None, "keyboard": "ukr"},
        "de": {"name": "Deutsch", "font": None, "keyboard": "de"},
        "fr": {"name": "Français", "font": None, "keyboard": "fr"},
        "es": {"name": "Español", "font": None, "keyboard": "es"},
        "it": {"name": "Italiano", "font": None, "keyboard": "it"},
        "pl": {"name": "Polski", "font": None, "keyboard": "pl"},
        "tr": {"name": "Türkçe", "font": None, "keyboard": "tr"},
        "zh": {"name": "中文", "font": None, "keyboard": "zh"},
        "ja": {"name": "日本語", "font": None, "keyboard": "jp"},
        # Фракційні мови Titanium
        "federation": {"name": "Federation Standard", "font": None, "keyboard": "qwerty"},
        "klingon":    {"name": "Klingon", "font": None, "keyboard": "kli"},
        "romulan":    {"name": "Rihannsu (Romulan)", "font": None, "keyboard": "rom"},
        "cardassian": {"name": "Cardăsda", "font": None, "keyboard": "card"},
        "mandalorian": {"name": "Mando'a", "font": None, "keyboard": "mandal"},
        "galactic":   {"name": "Galactic Basic", "font": None, "keyboard": "aurebesh"},
    }

    # Отримання списку підтримуваних мов
    @classmethod
    def GetSupportedLanguages(cls):
        return {CodeKey: DataNode["name"] for CodeKey, DataNode in cls.BaseLanguagesMap.items()}

    # Отримання шрифту для зазначеної мови
    @classmethod
    def GetFontForLanguage(cls, LangCodeStr: str):
        LangCodeNormalized = LangCodeStr.lower()
        FontNode = cls.BaseLanguagesMap.get(LangCodeNormalized, {}).get("font")
        if FontNode: return FontNode
        
        # Завантаження фракційного шрифту Titanium
        ResultFont = FontManager.LoadFont(LangCodeNormalized)
        if ResultFont: return ResultFont
        
        return FontManager.Fonts.get("lcars", "LCARS")

    # Отримання розкладки клавіатури для мови
    @classmethod
    def GetKeyboardLayout(cls, LangCodeStr: str):
        LangCodeNormalized = LangCodeStr.lower()
        return cls.BaseLanguagesMap.get(LangCodeNormalized, {}).get("keyboard", "qwerty")

    # Мітки-заглушки Titanium
    FallbackLabelsMap = {
        "TITLE": "LINGUISTIC MATRIX",
        "VOCABULARY_BANK": "VOCABULARY BANK",
        "TRAINING_MODULES": "TRAINING MODULES",
        "GRAMMAR_CORE": "GRAMMAR CORE",
    }

    # Ініціалізація лінгвістичної матриці Titanium
    def __init__(self, FactionStr: Optional[str] = None):
        super().__init__()
        self.StorageChipNode = LinguisticChip()
        self.ActiveFactionStr = FactionStr.lower() if FactionStr else "federation"
        self.ActiveLanguageStr = Language.GetLanguage()
        
        # Прив'язка шрифтів до мов Titanium
        self.InitializeFontMatrix()
        Language.RegisterCallback(self.OnLanguageShift)
        
        print("◤ LINGUISTIC_MATRIX :: TASK: MATRIX ACTIVE. Linguistic grid locked.")

    # Ініціалізація матриці шрифтів для всіх мов
    def InitializeFontMatrix(self):
        for CodeKey in self.BaseLanguagesMap:
            if CodeKey in ["federation", "klingon", "romulan", "cardassian", "mandalorian", "galactic"]:
                FontRef = FontManager.LoadFont(CodeKey)
            else:
                FontRef = FontManager.LoadFont(CodeKey)
            if FontRef:
                self.BaseLanguagesMap[CodeKey]["font"] = FontRef

    # Встановлення активної фракції та переключення шрифтів
    def SetActiveFaction(self, FactionStr: Optional[str]):
        # Встановити активну фракцію Titanium та переключити шрифти.
        self.ActiveFactionStr = FactionStr.lower() if FactionStr else "federation"
        print(f"◤ LINGUISTIC_MATRIX :: TASK_REPORT: Faction vector set to {self.ActiveFactionStr}.")

    # Переклад тексту з врахуванням фракції та мови
    def TranslateText(self, RawText: str, SrcLangStr: str = "en", TgtLangStr: Optional[str] = None) -> str:
        if not RawText: return ""
        TargetLang = TgtLangStr or Language.GetLanguage()
        
        # 1. Пошук в ізолінійному чіпі ISO-03
        if SrcLangStr == "en" and TargetLang in ["ua", "uk"]:
            QuerySql = "SELECT ukrainian FROM vocabulary WHERE english = ? AND (faction = ? OR faction = 'federation') ORDER BY (faction = ?) DESC LIMIT 1"
            ResultArray = self.StorageChipNode.ExecuteQuery(QuerySql, (RawText.lower(), self.ActiveFactionStr, self.ActiveFactionStr))
            if ResultArray: return ResultArray[0][0]
        
        # 2. Системна локалізація Titanium
        return Language.translate(RawText, faction=self.ActiveFactionStr) if RawText.isupper() else Language.auto_translate(RawText, src=SrcLangStr)

    # Пошук терміну в словнику за мовою та фракцією
    def LookupTerm(self, TermStr: str, LangCodeStr: str = "en", LimitVal: int = 20) -> List[Dict[str, Any]]:
        ColumnStr = "english" if LangCodeStr == "en" else "ukrainian"
        QuerySql = f"SELECT * FROM vocabulary WHERE {ColumnStr} LIKE ? AND (faction = ? OR faction = 'federation') ORDER BY (faction = ?) DESC, frequency DESC LIMIT ?"
        RowsArray = self.StorageChipNode.ExecuteQuery(QuerySql, (f"%{TermStr}%", self.ActiveFactionStr, self.ActiveFactionStr, LimitVal))
        return [dict(Row) for Row in RowsArray]

    # Додавання нового лінгвістичного патерну до матриці
    def AddVocabularyEntry(self, EngStr: str, UkrStr: str, **kwargs) -> bool:
        # Додати новий лінгвістичний паттерн до Titanium Matrix
        QuerySql = "INSERT OR IGNORE INTO vocabulary (english, ukrainian, level, faction) VALUES (?, ?, ?, ?)"
        FactionVal = kwargs.get("faction", self.ActiveFactionStr)
        SuccessFlag = self.StorageChipNode.ExecuteQuery(QuerySql, (EngStr.lower(), UkrStr.lower(), kwargs.get("level", "A1"), FactionVal))
        if SuccessFlag:
            print(f"◤ LINGUISTIC_MATRIX :: TASK_REPORT: Term '{EngStr}' indexed for {FactionVal}.")
        return bool(SuccessFlag)

    # Отримання статистики лінгвістичної матриці
    def GetLinguisticStats(self) -> Dict[str, Any]:
        ResultRows = self.StorageChipNode.ExecuteQuery("SELECT COUNT(*) FROM vocabulary")
        return {"vocabulary_count": ResultRows[0][0] if ResultRows else 0}

    # Канонічний розв'язувач міток з урахуванням фракції
    def ResolveLabel(self, LabelKeyStr: str) -> str:
        # Канонічний розв'язувач міток Titanium з урахуванням фракції.
        ValueStr = Language.translate(LabelKeyStr, faction=self.ActiveFactionStr)
        if ValueStr and ValueStr != LabelKeyStr: return ValueStr
        return self.FallbackLabelsMap.get(LabelKeyStr, LabelKeyStr)

    # Обробка зміни мови системи
    def OnLanguageShift(self, NewLangCodeStr: str):
        self.ActiveLanguageStr = NewLangCodeStr
        print(f"◤ LINGUISTIC_MATRIX :: EVENT: Language vector shift: {NewLangCodeStr}.")

# ГЛОБАЛЬНИЙ ЕКЗЕМПЛЯР TITANIUM LINGUISTICS
TitaniumLinguisticMatrix = LinguisticMatrix()
LinguisticMatrixRef = TitaniumLinguisticMatrix

# Аліаси за стандартом
LINGUISTIC_MATRIX = TitaniumLinguisticMatrix
LinguisticDatabase = LinguisticChip

# Експорт вузлів Titanium
__all__ = ["LinguisticMatrix", "TitaniumLinguisticMatrix", "LinguisticChip"]
