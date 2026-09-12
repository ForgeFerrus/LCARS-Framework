# ◤ TITANIUM SYSTEM LCARS SCRIPT LEXER // STARFLEET CANON 🖖
# =============================================================================
# ФАЙЛ: lcars/system/lexer.py
# ОПИС: Лексичний аналізатор (Lexer) для мови LCARS Script (.lcars).
#       Розбиває вихідний текст сценарію на лексеми (токени) для синтаксичного
#       аналізатора (Parser) з підтримкою команд, симуляцій Geant4 та функцій.
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Zero-Except, Zero-Underscores, Strict PascalCase, Pure Classes).
# =============================================================================

from __future__ import annotations
from lcars.base.type import LCARS
from lcars.base.info import Version

# ═════════════════════════════════════════════════════════════════════
# 1. ТИПИ ТОКЕНІВ (TOKEN TYPES)
# ═════════════════════════════════════════════════════════════════════
class TokenType(LCARS):
    # Літерали
    NUMBER     = "NUMBER"
    STRING     = "STRING"
    BOOLEAN    = "BOOLEAN"

    # Ідентифікатори та оператори
    IDENTIFIER = "IDENTIFIER"
    ASSIGN     = "="
    PLUS       = "+"
    MINUS      = "-"
    MULTIPLY   = "*"
    DIVIDE     = "/"
    MODULO     = "%"
    POWER      = "^"

    # Порівняння та логіка
    EQUAL         = "=="
    NOT_EQUAL     = "!="
    LESS          = "<"
    LESS_EQUAL    = "<="
    GREATER       = ">"
    GREATER_EQUAL = ">="
    AND           = "and"
    OR            = "or"
    NOT           = "not"

    # Розділювачі та дужки
    COMMA         = ","
    DOT           = "."
    COLON         = ":"
    SEMICOLON     = ";"
    LEFT_PAREN    = "("
    RIGHT_PAREN   = ")"
    LEFT_BRACKET  = "["
    RIGHT_BRACKET = "]"
    LEFT_BRACE    = "{"
    RIGHT_BRACE   = "}"
    ARROW         = "->"
    AT            = "@"

    # Ключові слова LCARS
    SIMULATION    = "SIMULATION"
    DETECTOR      = "DETECTOR"
    ANALYZER      = "ANALYZER"
    VISUALIZE     = "VISUALIZE"
    FUNCTION      = "FUNCTION"
    PROCEDURE     = "PROCEDURE"
    PLUGIN        = "PLUGIN"

    # Блоки подій
    ON            = "ON"
    START         = "START"
    COMPLETE      = "COMPLETE"
    ERROR         = "ERROR"
    PROGRESS      = "PROGRESS"
    HIT           = "HIT"
    READY         = "READY"
    LOAD          = "LOAD"

    # Керуючі конструкції
    IF            = "IF"
    ELSE          = "ELSE"
    FOR           = "FOR"
    WHILE         = "WHILE"
    FOREACH       = "FOREACH"
    FROM          = "FROM"
    TO            = "TO"
    IN            = "IN"
    RETURN        = "RETURN"

    # Інструкції середовища
    LOG           = "log"
    EMIT          = "emit"
    EXPORT        = "export"
    IMPORT        = "import"

    # Службові маркери
    NEWLINE       = "NEWLINE"
    INDENT        = "INDENT"
    DEDENT        = "DEDENT"
    EOF           = "EOF"
    COMMENT       = "COMMENT"

# ═════════════════════════════════════════════════════════════════════
# 2. СТРУКТУРА ТОКЕНА ТА ПОМИЛКИ
# ═════════════════════════════════════════════════════════════════════
class Token(LCARS):
    # Елементарний токен вихідного коду LCARS Script
    def __init__(self, Type: str, Value: str, Line: int, Column: int):
        super().__init__(Id=f"Token.{Type}")
        self.Type = Type
        self.Value = Value
        self.Line = Line
        self.Column = Column

        # Сумісність для парсера
        self.type = self.Type
        self.value = self.Value
        self.line = self.Line
        self.column = self.Column

    def __str__(self) -> str:
        return f"Token({self.Type}, {repr(self.Value)}, line={self.Line}, col={self.Column})"

    def __repr__(self) -> str:
        return self.__str__()

class LexerError(Exception, LCARS):
    # Помилка лексичного аналізу коду
    def __init__(self, Message: str, Line: int, Column: int):
        super().__init__(f"LexerError at line {Line}, col {Column}: {Message}")
        self.Message = Message
        self.Line = Line
        self.Column = Column

# ═════════════════════════════════════════════════════════════════════
# 3. ЛЕКСИЧНИЙ АНАЛІЗАТОР (LEXER)
# ═════════════════════════════════════════════════════════════════════
class Lexer(LCARS):
    # Головний лексер вихідного коду LCARS Script
    SystemVersion = Version.Release

    def __init__(self, Text: str = ""):
        super().__init__(Id="Lexer")
        self.Text = str(Text)
        self.Pos = 0
        self.Line = 1
        self.Column = 1
        self.Tokens: list[Token] = []

        # Таблиця канонічних ключових слів
        RawKeywords = {
            "SIMULATION": TokenType.SIMULATION,
            "DETECTOR": TokenType.DETECTOR,
            "ANALYZER": TokenType.ANALYZER,
            "VISUALIZE": TokenType.VISUALIZE,
            "FUNCTION": TokenType.FUNCTION,
            "PROCEDURE": TokenType.PROCEDURE,
            "PLUGIN": TokenType.PLUGIN,
            "ON": TokenType.ON,
            "START": TokenType.START,
            "COMPLETE": TokenType.COMPLETE,
            "ERROR": TokenType.ERROR,
            "PROGRESS": TokenType.PROGRESS,
            "HIT": TokenType.HIT,
            "READY": TokenType.READY,
            "LOAD": TokenType.LOAD,
            "IF": TokenType.IF,
            "ELSE": TokenType.ELSE,
            "FOR": TokenType.FOR,
            "WHILE": TokenType.WHILE,
            "FOREACH": TokenType.FOREACH,
            "FROM": TokenType.FROM,
            "TO": TokenType.TO,
            "IN": TokenType.IN,
            "RETURN": TokenType.RETURN,
            "LOG": TokenType.LOG,
            "EMIT": TokenType.EMIT,
            "EXPORT": TokenType.EXPORT,
            "IMPORT": TokenType.IMPORT,
            "AND": TokenType.AND,
            "OR": TokenType.OR,
            "NOT": TokenType.NOT,
            "TRUE": TokenType.BOOLEAN,
            "FALSE": TokenType.BOOLEAN,
        }
        self.Keywords = {}
        for K, V in RawKeywords.items():
            self.Keywords[K] = V
            self.Keywords[K.lower()] = V

    def CurrentChar(self) -> str | None:
        # Поточний аналізований символ
        if self.Pos >= len(self.Text):
            return None
        return self.Text[self.Pos]

    def PeekChar(self, Offset: int = 1) -> str | None:
        # Перегляд символу попереду без зсуву позиції
        PeekPos = self.Pos + Offset
        if PeekPos >= len(self.Text):
            return None
        return self.Text[PeekPos]

    def Advance(self) -> None:
        # Зсув позиції на наступний символ
        if self.Pos < len(self.Text):
            if self.Text[self.Pos] == "\n":
                self.Line += 1
                self.Column = 1
            else:
                self.Column += 1
            self.Pos += 1

    def SkipWhitespace(self) -> None:
        # Пропуск пробільних символів окрім переносу рядка
        while self.CurrentChar() and self.CurrentChar() in " \t\r":
            self.Advance()

    def SkipComment(self) -> None:
        # Пропуск однорядкових коментарів //
        if self.CurrentChar() == "/" and self.PeekChar() == "/":
            while self.CurrentChar() and self.CurrentChar() != "\n":
                self.Advance()

    def ReadNumber(self) -> str:
        # Читання цілих та дробових чисел
        Buffer = ""
        while self.CurrentChar() and (self.CurrentChar().isdigit() or self.CurrentChar() == "." or self.CurrentChar() in "eE-+"):
            Buffer += self.CurrentChar()
            self.Advance()
        return Buffer

    def ReadString(self, QuoteChar: str) -> str:
        # Читання строкового літералу з екрануванням
        Buffer = ""
        self.Advance()
        EscapeMap = {
            "n": "\n",
            "t": "\t",
            "r": "\r",
            "\\": "\\",
            "\"": "\"",
            "'": "'",
        }
        while self.CurrentChar() and self.CurrentChar() != QuoteChar:
            if self.CurrentChar() == "\\":
                self.Advance()
                NextC = self.CurrentChar()
                if NextC:
                    Buffer += EscapeMap.get(NextC, NextC)
                    self.Advance()
            else:
                Buffer += self.CurrentChar()
                self.Advance()
        if self.CurrentChar() == QuoteChar:
            self.Advance()
        return Buffer

    def ReadIdentifier(self) -> str:
        # Читання ідентифікатора або ключового слова
        Buffer = ""
        while self.CurrentChar() and (self.CurrentChar().isalnum() or self.CurrentChar() == "_"):
            Buffer += self.CurrentChar()
            self.Advance()
        return Buffer

    def ReadOperator(self) -> str | None:
        # Розпізнавання складених та одинарних операторів
        Char = self.CurrentChar()
        NextChar = self.PeekChar()

        # Двосимвольні оператори
        if Char == "=" and NextChar == "=":
            self.Advance()
            self.Advance()
            return "=="
        elif Char == "!" and NextChar == "=":
            self.Advance()
            self.Advance()
            return "!="
        elif Char == "<" and NextChar == "=":
            self.Advance()
            self.Advance()
            return "<="
        elif Char == ">" and NextChar == "=":
            self.Advance()
            self.Advance()
            return ">="
        elif Char == "-" and NextChar == ">":
            self.Advance()
            self.Advance()
            return "->"

        # Односимвольні оператори
        if Char in "=+-*/%^<>,.:;()[]{}@":
            self.Advance()
            return Char
        return None

    def Tokenize(self) -> list[Token]:
        # Повна токенізація вихідного тексту
        OperatorMap = {
            "=": TokenType.ASSIGN,
            "+": TokenType.PLUS,
            "-": TokenType.MINUS,
            "*": TokenType.MULTIPLY,
            "/": TokenType.DIVIDE,
            "%": TokenType.MODULO,
            "^": TokenType.POWER,
            "==": TokenType.EQUAL,
            "!=": TokenType.NOT_EQUAL,
            "<": TokenType.LESS,
            "<=": TokenType.LESS_EQUAL,
            ">": TokenType.GREATER,
            ">=": TokenType.GREATER_EQUAL,
            ",": TokenType.COMMA,
            ".": TokenType.DOT,
            ":": TokenType.COLON,
            ";": TokenType.SEMICOLON,
            "(": TokenType.LEFT_PAREN,
            ")": TokenType.RIGHT_PAREN,
            "[": TokenType.LEFT_BRACKET,
            "]": TokenType.RIGHT_BRACKET,
            "{": TokenType.LEFT_BRACE,
            "}": TokenType.RIGHT_BRACE,
            "@": TokenType.AT,
            "->": TokenType.ARROW,
        }

        while self.Pos < len(self.Text):
            self.SkipWhitespace()
            if self.Pos >= len(self.Text):
                break

            Char = self.CurrentChar()

            # 1. Новий рядок
            if Char == "\n":
                self.Tokens.append(Token(TokenType.NEWLINE, Char, self.Line, self.Column))
                self.Advance()
                continue

            # 2. Коментар
            if Char == "/" and self.PeekChar() == "/":
                self.SkipComment()
                continue

            # 3. Рядок у лапках
            if Char in "\"\'":
                Val = self.ReadString(Char)
                self.Tokens.append(Token(TokenType.STRING, Val, self.Line, self.Column))
                continue

            # 4. Число
            if Char.isdigit():
                Val = self.ReadNumber()
                self.Tokens.append(Token(TokenType.NUMBER, Val, self.Line, self.Column))
                continue

            # 5. Ідентифікатор або ключове слово
            if Char.isalpha() or Char == "_":
                Val = self.ReadIdentifier()
                TokType = self.Keywords.get(Val, TokenType.IDENTIFIER)
                self.Tokens.append(Token(TokType, Val, self.Line, self.Column))
                continue

            # 6. Оператор
            Op = self.ReadOperator()
            if Op:
                MatchedType = OperatorMap.get(Op)
                if MatchedType:
                    self.Tokens.append(Token(MatchedType, Op, self.Line, self.Column))
                continue

            # 7. Нерозпізнаний символ — зсуваємо вперед
            self.Advance()

        self.Tokens.append(Token(TokenType.EOF, "", self.Line, self.Column))
        return self.Tokens

    # Сумісність зі старим кодом
    tokenize = Tokenize

__all__ = [
    "TokenType",
    "Token",
    "LexerError",
    "Lexer",
]

