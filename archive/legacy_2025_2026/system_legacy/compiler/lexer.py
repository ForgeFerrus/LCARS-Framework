# LCARS FRAMEWORK v1.0.0-ALPHA
# Лексер LCARS Script (LCARS Script Lexer)
# ОПИС: Лексичний аналізатор мови LCARS Script. Розбиває вихідний код на токени
#        (лексеми) для подальшого синтаксичного аналізу парсером.
# ТОКЕНИ: NUMBER, STRING, BOOLEAN, IDENTIFIER, оператори, ключові слова
# ВЕРСІЯ: v1.0.0-ALPHA

# Titanium Bridge Migration: import re
# Titanium Bridge Migration: from enum import Enum
# Titanium Bridge Migration: from typing import List, NamedTuple, Optional
# Titanium Bridge Migration: from dataclasses import dataclass


class TokenType(Enum):
    """Типи токенів LCARS Script"""
    
    # Літерали
    NUMBER = "NUMBER"
    STRING = "STRING"
    BOOLEAN = "BOOLEAN"
    
    # Ідентифікатори та ключові слова
    IDENTIFIER = "IDENTIFIER"
    
    # Оператори
    ASSIGN = "="
    PLUS = "+"
    MINUS = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    MODULO = "%"
    POWER = "^"
    
    # Порівняння
    EQUAL = "=="
    NOT_EQUAL = "!="
    LESS = "<"
    LESS_EQUAL = "<="
    GREATER = ">"
    GREATER_EQUAL = ">="
    
    # Логічні оператори
    AND = "and"
    OR = "or"
    NOT = "not"
    
    # Розділювачі
    COMMA = ","
    DOT = "."
    COLON = ":"
    SEMICOLON = ";"
    
    # Дужки
    LEFT_PAREN = "("
    RIGHT_PAREN = ")"
    LEFT_BRACKET = "["
    RIGHT_BRACKET = "]"
    LEFT_BRACE = "{"
    RIGHT_BRACE = "}"
    
    # Спеціальні символи
    ARROW = "->"
    AT = "@"
    
    # Ключові слова
    SIMULATION = "SIMULATION"
    DETECTOR = "DETECTOR"
    ANALYZER = "ANALYZER"
    VISUALIZE = "VISUALIZE"
    FUNCTION = "FUNCTION"
    PROCEDURE = "PROCEDURE"
    PLUGIN = "PLUGIN"
    
    # Блоки коду
    ON = "ON"
    START = "START"
    COMPLETE = "COMPLETE"
    ERROR = "ERROR"
    PROGRESS = "PROGRESS"
    HIT = "HIT"
    READY = "READY"
    LOAD = "LOAD"
    
    # Умовні конструкції
    IF = "IF"
    ELSE = "ELSE"
    FOR = "FOR"
    WHILE = "WHILE"
    FOREACH = "FOREACH"
    FROM = "FROM"
    TO = "TO"
    IN = "IN"
    
    # Інші ключові слова
    RETURN = "RETURN"
    LOG = "log"
    EMIT = "emit"
    EXPORT = "export"
    IMPORT = "import"
    
    # Спеціальні токени
    NEWLINE = "NEWLINE"
    INDENT = "INDENT"
    DEDENT = "DEDENT"
    EOF = "EOF"
    
    # Коментарі
    COMMENT = "COMMENT"


@dataclass
class Token:
    """Токен LCARS Script"""
    type: TokenType
    value: str
    line: int
    column: int
    
    def __str__(self):
        return f"Token({self.type.value}, {repr(self.value)}, line={self.line}, col={self.column})"
    
    def __repr__(self):
        return self.__str__()


class LexerError(Exception):
    """Помилка лексичного аналізу"""
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Lexer Error at line {line}, column {column}: {message}")


class Lexer:
    """Лексер для LCARS Script"""
    
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        
        # Визначення токенів
        self.keywords = {
            'SIMULATION': TokenType.SIMULATION,
            'DETECTOR': TokenType.DETECTOR,
            'ANALYZER': TokenType.ANALYZER,
            'VISUALIZE': TokenType.VISUALIZE,
            'FUNCTION': TokenType.FUNCTION,
            'PROCEDURE': TokenType.PROCEDURE,
            'PLUGIN': TokenType.PLUGIN,
            'ON': TokenType.ON,
            'START': TokenType.START,
            'COMPLETE': TokenType.COMPLETE,
            'ERROR': TokenType.ERROR,
            'PROGRESS': TokenType.PROGRESS,
            'HIT': TokenType.HIT,
            'READY': TokenType.READY,
            'LOAD': TokenType.LOAD,
            'IF': TokenType.IF,
            'ELSE': TokenType.ELSE,
            'FOR': TokenType.FOR,
            'WHILE': TokenType.WHILE,
            'FOREACH': TokenType.FOREACH,
            'FROM': TokenType.FROM,
            'TO': TokenType.TO,
            'IN': TokenType.IN,
            'RETURN': TokenType.RETURN,
            'log': TokenType.LOG,
            'emit': TokenType.EMIT,
            'export': TokenType.EXPORT,
            'import': TokenType.IMPORT,
            'and': TokenType.AND,
            'or': TokenType.OR,
            'not': TokenType.NOT,
            'true': TokenType.BOOLEAN,
            'false': TokenType.BOOLEAN,
        }
    
    def current_char(self) -> Optional[str]:
        """Поточний символ"""
        if self.pos >= len(self.text):
            return None
        return self.text[self.pos]
    
    def peek_char(self, offset: int = 1) -> Optional[str]:
        """Подивитися символ вперед"""
        peek_pos = self.pos + offset
        if peek_pos >= len(self.text):
            return None
        return self.text[peek_pos]
    
    def advance(self):
        """Перейти до наступного символу"""
        if self.pos < len(self.text):
            if self.text[self.pos] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.pos += 1
    
    def skip_whitespace(self):
        """Пропустити пробіли"""
        while self.current_char() and self.current_char() in ' \t\r':
            self.advance()
    
    def skip_comment(self):
        """Пропустити коментар"""
        if self.current_char() == '/' and self.peek_char() == '/':
            while self.current_char() and self.current_char() != '\n':
                self.advance()
    
    def read_number(self) -> str:
        """Читати число"""
        result = ''
        while (self.current_char() and 
               (self.current_char().isdigit() or 
                self.current_char() == '.' or
                self.current_char() in 'eE-+')):
            result += self.current_char()
            self.advance()
        return result
    
    def read_string(self, quote_char: str) -> str:
        """Читати рядок"""
        result = ''
        self.advance()  # Пропустити відкриваючу лапку
        
        while self.current_char() and self.current_char() != quote_char:
            if self.current_char() == '\\':
                self.advance()
                if self.current_char():
                    escape_chars = {
                        'n': '\n',
                        't': '\t',
                        'r': '\r',
                        '\\': '\\',
                        '"': '"',
                        "'": "'",
                    }
                    result += escape_chars.get(self.current_char(), self.current_char())
                    self.advance()
            else:
                result += self.current_char()
                self.advance()
        
        if self.current_char() == quote_char:
            self.advance()  # Пропустити закриваючу лапку
        else:
            raise LexerError(f"Unterminated string", self.line, self.column)
        
        return result
    
    def read_identifier(self) -> str:
        """Читати ідентифікатор"""
        result = ''
        while (self.current_char() and 
               (self.current_char().isalnum() or 
                self.current_char() == '_')):
            result += self.current_char()
            self.advance()
        return result
    
    def read_operator(self) -> Optional[str]:
        """Читати оператор"""
        char = self.current_char()
        next_char = self.peek_char()
        
        # Двосимвольні оператори
        if char == '=' and next_char == '=':
            self.advance()
            self.advance()
            return '=='
        elif char == '!' and next_char == '=':
            self.advance()
            self.advance()
            return '!='
        elif char == '<' and next_char == '=':
            self.advance()
            self.advance()
            return '<='
        elif char == '>' and next_char == '=':
            self.advance()
            self.advance()
            return '>='
        elif char == '-' and next_char == '>':
            self.advance()
            self.advance()
            return '->'
        
        # Односимвольні оператори
        if char in '=+-*/%^<>,.:;()[]{}@':
            self.advance()
            return char
        
        return None
    
    def tokenize(self) -> List[Token]:
        """Токенізувати весь текст"""
        while self.pos < len(self.text):
            self.skip_whitespace()
            
            if self.pos >= len(self.text):
                break
            
            char = self.current_char()
            
            # Новий рядок
            if char == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, char, self.line, self.column))
                self.advance()
                continue
            
            # Коментар
            if char == '/' and self.peek_char() == '/':
                self.skip_comment()
                continue
            
            # Рядок
            if char in '"\'':
                quote_char = char
                value = self.read_string(quote_char)
                self.tokens.append(Token(TokenType.STRING, value, self.line, self.column))
                continue
            
            # Число
            if char.isdigit():
                value = self.read_number()
                self.tokens.append(Token(TokenType.NUMBER, value, self.line, self.column))
                continue
            
            # Ідентифікатор або ключове слово
            if char.isalpha() or char == '_':
                value = self.read_identifier()
                token_type = self.keywords.get(value, TokenType.IDENTIFIER)
                self.tokens.append(Token(token_type, value, self.line, self.column))
                continue
            
            # Оператор
            operator = self.read_operator()
            if operator:
                # Перетворення рядка оператора в TokenType
                operator_map = {
                    '=': TokenType.ASSIGN,
                    '+': TokenType.PLUS,
                    '-': TokenType.MINUS,
                    '*': TokenType.MULTIPLY,
                    '/': TokenType.DIVIDE,
                    '%': TokenType.MODULO,
                    '^': TokenType.POWER,
                    '==': TokenType.EQUAL,
                    '!=': TokenType.NOT_EQUAL,
                    '<': TokenType.LESS,
                    '<=': TokenType.LESS_EQUAL,
                    '>': TokenType.GREATER,
                    '>=': TokenType.GREATER_EQUAL,
                    ',': TokenType.COMMA,
                    '.': TokenType.DOT,
                    ':': TokenType.COLON,
                    ';': TokenType.SEMICOLON,
                    '(': TokenType.LEFT_PAREN,
                    ')': TokenType.RIGHT_PAREN,
                    '[': TokenType.LEFT_BRACKET,
                    ']': TokenType.RIGHT_BRACKET,
                    '{': TokenType.LEFT_BRACE,
                    '}': TokenType.RIGHT_BRACE,
                    '@': TokenType.AT,
                    '->': TokenType.ARROW,
                }
                token_type = operator_map.get(operator)
                if token_type:
                    self.tokens.append(Token(token_type, operator, self.line, self.column))
                continue
            
            # Невідомий символ
            raise LexerError(f"Unexpected character: {char}", self.line, self.column)
        
        # Додати EOF токен
        self.tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        
        return self.tokens
    
    def print_tokens(self):
        """Друкувати токени для відладки"""
        for token in self.tokens:
            print(token)


# Тестування
if __name__ == "__main__":
    # Приклад коду LCARS Script
    test_code = """
    // Проста симуляція
    energy: 1.5 GeV
    particles: 10000
    
    SIMULATION main_beam {
        ENERGY energy
        PARTICLES particles
        
        ON START {
            log("Initializing simulation...")
            emit("simulation:started", {energy: energy})
        }
        
        ON COMPLETE {
            export("results.root")
        }
    }
    
    FUNCTION calculate_efficiency(detected, total) -> float {
        if total == 0 return 0.0
        return detected / total * 100
    }
    """
    
    print("=== LCARS Script Lexer Test ===")
    print("Input code:")
    print(test_code)
    print("\nTokens:")
    
    lexer = Lexer(test_code)
    tokens = lexer.tokenize()
    
    for token in tokens:
        print(token)
    
    print(f"\nTotal tokens: {len(tokens)}")
