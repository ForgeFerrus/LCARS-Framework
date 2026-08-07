# LCARS system lexer.
# Призначення: перетворює текст LCARS Script у стабільний потік токенів.
# Лексер не знає про режими виконання: optical і quantum використовують один
# формат команд, тому відмінність залишається в контексті runtime, а не в мові.

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class TokenType(Enum):
    NUMBER = "NUMBER"
    STRING = "STRING"
    BOOLEAN = "BOOLEAN"
    IDENTIFIER = "IDENTIFIER"
    ASSIGN = "="
    PLUS = "+"
    MINUS = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    MODULO = "%"
    POWER = "^"
    EQUAL = "=="
    NOT_EQUAL = "!="
    LESS = "<"
    LESS_EQUAL = "<="
    GREATER = ">"
    GREATER_EQUAL = ">="
    AND = "and"
    OR = "or"
    NOT = "not"
    COMMA = ","
    DOT = "."
    COLON = ":"
    SEMICOLON = ";"
    LEFT_PAREN = "("
    RIGHT_PAREN = ")"
    LEFT_BRACKET = "["
    RIGHT_BRACKET = "]"
    LEFT_BRACE = "{"
    RIGHT_BRACE = "}"
    ARROW = "->"
    AT = "@"
    SIMULATION = "SIMULATION"
    DETECTOR = "DETECTOR"
    ANALYZER = "ANALYZER"
    VISUALIZE = "VISUALIZE"
    FUNCTION = "FUNCTION"
    PROCEDURE = "PROCEDURE"
    PLUGIN = "PLUGIN"
    ON = "ON"
    START = "START"
    COMPLETE = "COMPLETE"
    ERROR = "ERROR"
    PROGRESS = "PROGRESS"
    HIT = "HIT"
    READY = "READY"
    LOAD = "LOAD"
    IF = "IF"
    ELSE = "ELSE"
    FOR = "FOR"
    WHILE = "WHILE"
    FOREACH = "FOREACH"
    FROM = "FROM"
    TO = "TO"
    IN = "IN"
    RETURN = "RETURN"
    LOG = "log"
    EMIT = "emit"
    EXPORT = "export"
    IMPORT = "import"
    NEWLINE = "NEWLINE"
    INDENT = "INDENT"
    DEDENT = "DEDENT"
    EOF = "EOF"
    COMMENT = "COMMENT"


@dataclass
class Token:
    # Token зберігає вихідне значення і координати для діагностики агента.
    type: TokenType
    value: str
    line: int
    column: int

    def __str__(self) -> str:
        return "Token(" + self.type.value + ", " + repr(self.value) + ", " + str(self.line) + ":" + str(self.column) + ")"

    def __repr__(self) -> str:
        return self.__str__()


@dataclass
class LexerError:
    # Помилка є даними, а не винятком: консоль може показати її без падіння.
    message: str
    line: int
    column: int

    def __str__(self) -> str:
        return "LEXER " + str(self.line) + ":" + str(self.column) + " " + self.message


class Lexer:
    # Один лексер обробляє і скрипти агента, і бортові команди.
    Keywords: Dict[str, TokenType] = {
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
    Operators: Dict[str, TokenType] = {
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

    def __init__(self, Text: str):
        self.Text = Text or ""
        self.Position = 0
        self.Line = 1
        self.Column = 1
        self.Tokens: List[Token] = []
        self.Error: Optional[LexerError] = None

    def Current(self) -> Optional[str]:
        if self.Position >= len(self.Text):
            return None
        return self.Text[self.Position]

    def Peek(self, Offset: int = 1) -> Optional[str]:
        Index = self.Position + Offset
        if Index >= len(self.Text):
            return None
        return self.Text[Index]

    def Advance(self) -> None:
        Character = self.Current()
        if Character is None:
            return
        self.Position += 1
        if Character == "\n":
            self.Line += 1
            self.Column = 1
        else:
            self.Column += 1

    # Перевіряє чи поточний символ є пропуском
    def SkipSpace(self) -> None:
        while True:
            Character = self.Current()
            if Character is None:
                break
            if Character not in (" ", "\t", "\r"):
                break
            self.Advance()

    # Пропускає коментар до кінця рядка
    def SkipComment(self) -> None:
        while True:
            Character = self.Current()
            if Character is None or Character == "\n":
                break
            self.Advance()

    # Читає число: ціле, з крапкою, з експонентою
    def ReadNumber(self) -> str:
        Start = self.Position
        HasDot = False
        HasExponent = False
        while True:
            Character = self.Current()
            # Цифра — продовжуємо читання
            if Character is not None and Character.isdigit():
                self.Advance()
                continue
            # Крапка — дозволяємо одну
            if Character == "." and not HasDot and not HasExponent:
                HasDot = True
                self.Advance()
                continue
            # Експонента (e/E)
            if Character in ("e", "E") and not HasExponent:
                HasExponent = True
                self.Advance()
                # Знак після експоненти
                NextChar = self.Current()
                if NextChar in ("+", "-"):
                    self.Advance()
                continue
            break
        return self.Text[Start:self.Position]

    def ReadIdentifier(self) -> str:
        Start = self.Position
        while True:
            Character = self.Current()
            if Character is None or not (Character.isalnum() or Character == "_"):
                break
            self.Advance()
        return self.Text[Start:self.Position]

    # Читає рядок з лапками, підтримує escape-послідовності
    def ReadString(self, Quote: str, Line: int, Column: int) -> str:
        self.Advance()
        Parts: List[str] = []
        # Таблиця escape-послідовностей
        Escapes = {"n": "\n", "t": "\t", "r": "\r", "\\": "\\", "\"": "\"", "'": "'"}
        while True:
            Character = self.Current()
            if Character is None or Character == Quote:
                break
            # Обробка escape-послідовності
            if Character == "\\":
                self.Advance()
                Escaped = self.Current()
                if Escaped is None:
                    self.Error = LexerError("unterminated escape", Line, Column)
                    return "".join(Parts)
                Parts.append(Escapes.get(Escaped, Escaped))
                self.Advance()
                continue
            Parts.append(Character)
            self.Advance()
        # Перевірка закриття лапки
        if self.Current() != Quote:
            self.Error = LexerError("unterminated string", Line, Column)
            return "".join(Parts)
        self.Advance()
        return "".join(Parts)

    def Add(self, Type: TokenType, Value: str, Line: int, Column: int) -> None:
        self.Tokens.append(Token(Type, Value, Line, Column))

    # Головний метод токенізації: перетворює текст на список токенів
    def tokenize(self) -> List[Token]:
        # У разі помилки повертаємо вже прочитану частину і EOF; це дозволяє
        # агенту отримати координату проблеми через Lexer.Error.
        while self.Error is None:
            # Пропускаємо пропуски
            self.SkipSpace()
            Character = self.Current()
            # Кінець вхідного тексту
            if Character is None:
                break
            Line = self.Line
            Column = self.Column
            # Новий рядок
            if Character == "\n":
                self.Add(TokenType.NEWLINE, Character, Line, Column)
                self.Advance()
                continue
            # Коментар // або #
            if Character == "/" and self.Peek() == "/":
                self.Advance()
                self.Advance()
                self.SkipComment()
                continue
            if Character == "#":
                self.Advance()
                self.SkipComment()
                continue
            # Рядок з лапками
            if Character in ("\"", "'"):
                Value = self.ReadString(Character, Line, Column)
                self.Add(TokenType.STRING, Value, Line, Column)
                continue
            # Число
            if Character.isdigit():
                self.Add(TokenType.NUMBER, self.ReadNumber(), Line, Column)
                continue
            # Ідентифікатор або ключове слово
            if Character.isalpha() or Character == "_":
                Value = self.ReadIdentifier()
                Upper = Value.upper()
                Type = self.Keywords.get(Upper, TokenType.IDENTIFIER)
                self.Add(Type, Value, Line, Column)
                continue
            # Оператор або роздільник
            Candidate = Character + (self.Peek() or "")
            Operator = Candidate if Candidate in self.Operators else Character
            if Operator in self.Operators:
                for _ in Operator:
                    self.Advance()
                self.Add(self.Operators[Operator], Operator, Line, Column)
                continue
            # Невідомий символ — помилка
            self.Error = LexerError("unexpected character " + repr(Character), Line, Column)
            self.Advance()
        # Додаємо EOF в кінець потоку токенів
        self.Add(TokenType.EOF, "", self.Line, self.Column)
        return self.Tokens

    def PrintTokens(self) -> None:
        for Item in self.Tokens:
            print(Item)

    # Старі CamelCase-виклики залишаються фасадом для модулів агентів.
    Tokenize = tokenize


__all__ = ["TokenType", "Token", "LexerError", "Lexer"]
