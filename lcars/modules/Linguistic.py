# ◤ TITANIUM LINGUISTIC MATRIX
# LCARS Framework :: LINGUISTIC_CORE // TRANSLATION_ENGINE // NO_Q PROTOCOL
# ОПИС: Ядро перекладу, словника та лінгвістичного аналізу (ISO-03).
# ФУНКЦІЇ: Фракційні шрифти, мультімовна підтримка та словник федерації.
# СТАНДАРТ: Titanium CamelCase (Повна заборона нижніх підкреслювань).
# ВЕРСІЯ: Делегована з lcars.base.version

from __future__ import annotations
# Titanium Bridge Migration: from typing import Optional, List, Dict, Any, Union

# Імпорт системних типів Titanium Master
from lcars.base.type import SystemComponent, Directive
from lcars.base.info import getVersion
from lcars.system.localization import LOCALIZATION as Language
from lcars.engineering.isolinear import IsolinearChip

__version__ = getVersion()
# 
class FontManagerAdapter:
    
    def __init__(self, ManagerNode):
        self.Manager = ManagerNode
        self.Fonts = {"lcars": "LCARS"}

    def LoadFont(self, Key: str):
        LangFont = self.Manager.LoadFontByLanguage(Key)
        if LangFont:
            return LangFont
        return self.Manager.LoadFontByFaction(Key)

Adapter = FontManager(Node)

# ── 1. ЛІНГВІСТИЧНИЙ ЧІП (TITANIUM ISO-03) ──

class LinguisticChip(IsolinearChip):
    # Спеціалізований вузол словника Titanium.
    def __init__(self):
        super().__init__('03', '03.db')
        self.InitializeMatrixSchema()

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

    @classmethod
    def GetSupportedLanguages(cls):
        return {CodeKey: DataNode["name"] for CodeKey, DataNode in cls.BaseLanguagesMap.items()}

    @classmethod
    def GetFontForLanguage(cls, LangCodeStr: str):
        LangCodeNormalized = LangCodeStr.lower()
        FontNode = cls.BaseLanguagesMap.get(LangCodeNormalized, {}).get("font")
        if FontNode: return FontNode
        
        # Завантаження фракційного шрифту Titanium
        ResultFont = FontManager.LoadFont(LangCodeNormalized)
        if ResultFont: return ResultFont
        
        return FontManager.Fonts.get("lcars", "LCARS")

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

    def __init__(self, FactionStr: Optional[str] = None):
        super().__init__()
        self.StorageChipNode = LinguisticChip()
        self.ActiveFactionStr = FactionStr.lower() if FactionStr else "federation"
        self.ActiveLanguageStr = Language.get_language()
        
        # Прив'язка шрифтів до мов Titanium
        self.InitializeFontMatrix()
        Language.register_callback(self.OnLanguageShift)
        
        print("◤ LINGUISTIC_MATRIX :: TASK: MATRIX ACTIVE. Linguistic grid locked.")

    def InitializeFontMatrix(self):
        for CodeKey in self.BaseLanguagesMap:
            if CodeKey in ["federation", "klingon", "romulan", "cardassian", "mandalorian", "galactic"]:
                FontRef = FontManager.LoadFont(CodeKey)
            else:
                FontRef = FontManager.LoadFont(CodeKey)
            if FontRef:
                self.BaseLanguagesMap[CodeKey]["font"] = FontRef

    def SetActiveFaction(self, FactionStr: Optional[str]):
        # Встановити активну фракцію Titanium та переключити шрифти.
        self.ActiveFactionStr = FactionStr.lower() if FactionStr else "federation"
        print(f"◤ LINGUISTIC_MATRIX :: TASK_REPORT: Faction vector set to {self.ActiveFactionStr}.")

    def TranslateText(self, RawText: str, SrcLangStr: str = "en", TgtLangStr: Optional[str] = None) -> str:
        if not RawText: return ""
        TargetLang = TgtLangStr or Language.get_language()
        
        # 1. Пошук в ізолінійному чіпі ISO-03
        if SrcLangStr == "en" and TargetLang in ["ua", "uk"]:
            QuerySql = "SELECT ukrainian FROM vocabulary WHERE english = ? AND (faction = ? OR faction = 'federation') ORDER BY (faction = ?) DESC LIMIT 1"
            ResultArray = self.StorageChipNode.ExecuteQuery(QuerySql, (RawText.lower(), self.ActiveFactionStr, self.ActiveFactionStr))
            if ResultArray: return ResultArray[0][0]
        
        # 2. Системна локалізація Titanium
        return Language.translate(RawText, faction=self.ActiveFactionStr) if RawText.isupper() else Language.auto_translate(RawText, src=SrcLangStr)

    def LookupTerm(self, TermStr: str, LangCodeStr: str = "en", LimitVal: int = 20) -> List[Dict[str, Any]]:
        ColumnStr = "english" if LangCodeStr == "en" else "ukrainian"
        QuerySql = f"SELECT * FROM vocabulary WHERE {ColumnStr} LIKE ? AND (faction = ? OR faction = 'federation') ORDER BY (faction = ?) DESC, frequency DESC LIMIT ?"
        RowsArray = self.StorageChipNode.ExecuteQuery(QuerySql, (f"%{TermStr}%", self.ActiveFactionStr, self.ActiveFactionStr, LimitVal))
        return [dict(Row) for Row in RowsArray]

    def AddVocabularyEntry(self, EngStr: str, UkrStr: str, **kwargs) -> bool:
        # Додати новий лінгвістичний паттерн до Titanium Matrix
        QuerySql = "INSERT OR IGNORE INTO vocabulary (english, ukrainian, level, faction) VALUES (?, ?, ?, ?)"
        FactionVal = kwargs.get("faction", self.ActiveFactionStr)
        SuccessFlag = self.StorageChipNode.ExecuteQuery(QuerySql, (EngStr.lower(), UkrStr.lower(), kwargs.get("level", "A1"), FactionVal))
        if SuccessFlag:
            print(f"◤ LINGUISTIC_MATRIX :: TASK_REPORT: Term '{EngStr}' indexed for {FactionVal}.")
        return bool(SuccessFlag)

    def GetLinguisticStats(self) -> Dict[str, Any]:
        ResultRows = self.StorageChipNode.ExecuteQuery("SELECT COUNT(*) FROM vocabulary")
        return {"vocabulary_count": ResultRows[0][0] if ResultRows else 0}

    def ResolveLabel(self, LabelKeyStr: str) -> str:
        # Канонічний розв'язувач міток Titanium з урахуванням фракції.
        ValueStr = Language.translate(LabelKeyStr, faction=self.ActiveFactionStr)
        if ValueStr and ValueStr != LabelKeyStr: return ValueStr
        return self.FallbackLabelsMap.get(LabelKeyStr, LabelKeyStr)

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
