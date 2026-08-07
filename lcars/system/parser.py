# LCARS system parser.
# Призначення: будує спільне AST для runtime, компілятора та агентів.
# Парсер не запускає код і не залежить від способу обчислення; один AST може
# бути виконаний у normal або quantum контексті без дублювання граматики.

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from .lexer import Lexer, LexerError, Token, TokenType


class NodeType(Enum):
    # Типи вузлів AST для всіх конструкцій мови LCARS Script
    PROGRAM = "PROGRAM"
    VARIABLE_DECLARATION = "VARIABLE_DECLARATION"
    FUNCTION_DECLARATION = "FUNCTION_DECLARATION"
    PROCEDURE_DECLARATION = "PROCEDURE_DECLARATION"
    SIMULATION_DECLARATION = "SIMULATION_DECLARATION"
    DETECTOR_DECLARATION = "DETECTOR_DECLARATION"
    ANALYZER_DECLARATION = "ANALYZER_DECLARATION"
    VISUALIZE_DECLARATION = "VISUALIZE_DECLARATION"
    PLUGIN_DECLARATION = "PLUGIN_DECLARATION"
    BLOCK = "BLOCK"
    EVENT_HANDLER = "EVENT_HANDLER"
    BINARY_EXPRESSION = "BINARY_EXPRESSION"
    UNARY_EXPRESSION = "UNARY_EXPRESSION"
    CALL_EXPRESSION = "CALL_EXPRESSION"
    MEMBER_EXPRESSION = "MEMBER_EXPRESSION"
    LITERAL = "LITERAL"
    IDENTIFIER = "IDENTIFIER"
    ASSIGNMENT = "ASSIGNMENT"
    RETURN_STATEMENT = "RETURN_STATEMENT"
    IF_STATEMENT = "IF_STATEMENT"
    FOR_STATEMENT = "FOR_STATEMENT"
    WHILE_STATEMENT = "WHILE_STATEMENT"
    FOREACH_STATEMENT = "FOREACH_STATEMENT"
    EXPRESSION_STATEMENT = "EXPRESSION_STATEMENT"
    ARRAY_LITERAL = "ARRAY_LITERAL"
    OBJECT_LITERAL = "OBJECT_LITERAL"
    PROPERTY = "PROPERTY"
    IMPORT_STATEMENT = "IMPORT_STATEMENT"
    EXPORT_STATEMENT = "EXPORT_STATEMENT"
    LOG_STATEMENT = "LOG_STATEMENT"
    EMIT_STATEMENT = "EMIT_STATEMENT"


@dataclass
class ASTNode:
    # ASTNode — простий серіалізований контракт між parser/compiler/runtime.
    type: NodeType
    value: Any = None
    children: List["ASTNode"] = field(default_factory=list)
    line: int = 0
    column: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def AddChild(self, Child: "ASTNode") -> None:
        self.children.append(Child)

    AddChild = AddChild

    def Str(self) -> str:
        return "ASTNode(" + self.type.value + ", " + repr(self.value) + ")"

    def Repr(self) -> str:
        return self.Str()

    def __str__(self) -> str:
        return self.Str()


@dataclass
class ParserError:
    # Помилка накопичується в Parser.Errors і доступна консолі без exception.
    message: str
    line: int
    column: int

    def __str__(self) -> str:
        return "PARSER " + str(self.line) + ":" + str(self.column) + " " + self.message


class Parser:
    # Таблиця пріоритетів визначає єдиний порядок обчислення для двох режимів.
    Precedence = {
        TokenType.OR: 1,
        TokenType.AND: 2,
        TokenType.EQUAL: 3,
        TokenType.NOT_EQUAL: 3,
        TokenType.LESS: 4,
        TokenType.LESS_EQUAL: 4,
        TokenType.GREATER: 4,
        TokenType.GREATER_EQUAL: 4,
        TokenType.PLUS: 5,
        TokenType.MINUS: 5,
        TokenType.MULTIPLY: 6,
        TokenType.DIVIDE: 6,
        TokenType.MODULO: 6,
        TokenType.POWER: 7,
    }
    DomainTypes = {
        TokenType.SIMULATION: NodeType.SIMULATION_DECLARATION,
        TokenType.DETECTOR: NodeType.DETECTOR_DECLARATION,
        TokenType.ANALYZER: NodeType.ANALYZER_DECLARATION,
        TokenType.VISUALIZE: NodeType.VISUALIZE_DECLARATION,
        TokenType.PLUGIN: NodeType.PLUGIN_DECLARATION,
    }

    def __init__(self, Tokens: Optional[List[Token]] = None):
        self.Tokens = Tokens or [Token(TokenType.EOF, "", 1, 1)]
        self.Position = 0
        self.Errors: List[ParserError] = []

    @property
    def CurrentToken(self) -> Token:
        if self.Position >= len(self.Tokens):
            return self.Tokens[-1]
        return self.Tokens[self.Position]

    def Peek(self, Offset: int = 1) -> Token:
        Index = self.Position + Offset
        if Index >= len(self.Tokens):
            return self.Tokens[-1]
        return self.Tokens[Index]

    def Advance(self) -> Token:
        Item = self.CurrentToken
        if self.Position < len(self.Tokens) - 1:
            self.Position += 1
        return Item

    def Match(self, *Types: TokenType) -> bool:
        return self.CurrentToken.type in Types

    def Consume(self, *Types: TokenType) -> Optional[Token]:
        if self.Match(*Types):
            return self.Advance()
        return None

    def Error(self, Message: str, Token: Optional[Token] = None) -> None:
        Item = Token or self.CurrentToken
        self.Errors.append(ParserError(Message, Item.line, Item.column))

    def Expect(self, Type: TokenType, Message: str = "") -> Token:
        if self.Match(Type):
            return self.Advance()
        Text = Message or ("expected " + Type.value + ", got " + self.CurrentToken.type.value)
        self.Error(Text)
        return Token(Type, "", self.CurrentToken.line, self.CurrentToken.column)

    def SkipLines(self) -> None:
        while self.Consume(TokenType.NEWLINE, TokenType.SEMICOLON):
            pass

    def parse(self) -> ASTNode:
        Root = ASTNode(NodeType.PROGRAM)
        self.SkipLines()
        while not self.Match(TokenType.EOF):
            Before = self.Position
            Node = self.ParseTop()
            if Node is not None:
                Root.AddChild(Node)
            self.SkipLines()
            if self.Position == Before:
                self.Advance()
        return Root

    def ParseTop(self) -> Optional[ASTNode]:
        if self.Match(TokenType.FUNCTION):
            return self.ParseFunction(False)
        if self.Match(TokenType.PROCEDURE):
            return self.ParseFunction(True)
        if self.CurrentToken.type in self.DomainTypes:
            return self.ParseDomain()
        return self.ParseStatement()

    def ParseDomain(self) -> ASTNode:
        Start = self.Advance()
        Name = self.Expect(TokenType.IDENTIFIER, "domain name expected")
        Node = ASTNode(self.DomainTypes[Start.type], Name.value, line=Start.line, column=Start.column)
        Node.metadata["domain"] = Start.value.upper()
        self.SkipLines()
        if not self.Consume(TokenType.LEFT_BRACE):
            self.Error("domain block expected", self.CurrentToken)
            return Node
        Node.children.extend(self.ParseBlockItems(True).children)
        return Node

    def ParseFunction(self, Procedure: bool) -> ASTNode:
        Start = self.Advance()
        Name = self.Expect(TokenType.IDENTIFIER, "function name expected")
        Type = NodeType.PROCEDURE_DECLARATION if Procedure else NodeType.FUNCTION_DECLARATION
        Node = ASTNode(Type, Name.value, line=Start.line, column=Start.column)
        self.SkipLines()
        self.Expect(TokenType.LEFT_PAREN, "parameter list expected")
        while not self.Match(TokenType.RIGHT_PAREN, TokenType.EOF):
            Parameter = self.Expect(TokenType.IDENTIFIER, "parameter name expected")
            Node.children.append(ASTNode(NodeType.IDENTIFIER, Parameter.value, line=Parameter.line, column=Parameter.column))
            if not self.Consume(TokenType.COMMA):
                break
        self.Expect(TokenType.RIGHT_PAREN, "closing parameter list expected")
        if self.Consume(TokenType.ARROW):
            ReturnType = self.Expect(TokenType.IDENTIFIER, "return type expected")
            Node.metadata["return_type"] = ReturnType.value
        self.SkipLines()
        if not self.Consume(TokenType.LEFT_BRACE):
            self.Error("function block expected", self.CurrentToken)
            return Node
        Node.children.append(self.ParseBlockItems(False))
        return Node

    def ParseBlockItems(self, Domain: bool) -> ASTNode:
        Block = ASTNode(NodeType.BLOCK)
        self.SkipLines()
        while not self.Match(TokenType.RIGHT_BRACE, TokenType.EOF):
            Before = self.Position
            if Domain and self.Match(TokenType.ON):
                Block.AddChild(self.ParseEvent())
            else:
                Item = self.ParseStatement()
                if Item is not None:
                    Block.AddChild(Item)
            self.SkipLines()
            if self.Position == Before:
                self.Advance()
        self.Expect(TokenType.RIGHT_BRACE, "closing block expected")
        return Block

    def ParseEvent(self) -> ASTNode:
        Start = self.Expect(TokenType.ON)
        Event = self.Advance()
        Node = ASTNode(NodeType.EVENT_HANDLER, Event.value, line=Start.line, column=Start.column)
        if self.Consume(TokenType.LEFT_PAREN):
            while not self.Match(TokenType.RIGHT_PAREN, TokenType.EOF):
                Node.children.append(self.ParseExpression())
                if not self.Consume(TokenType.COMMA):
                    break
            self.Expect(TokenType.RIGHT_PAREN, "closing event parameters expected")
        self.SkipLines()
        if self.Consume(TokenType.LEFT_BRACE):
            Node.children.append(self.ParseBlockItems(False))
        else:
            self.Error("event block expected", self.CurrentToken)
        return Node

    def ParseStatement(self) -> Optional[ASTNode]:
        if self.Match(TokenType.NEWLINE, TokenType.SEMICOLON):
            self.Advance()
            return None
        if self.Match(TokenType.RETURN):
            Start = self.Advance()
            Value = None if self.Match(TokenType.NEWLINE, TokenType.RIGHT_BRACE, TokenType.EOF) else self.ParseExpression()
            return ASTNode(NodeType.RETURN_STATEMENT, children=[] if Value is None else [Value], line=Start.line, column=Start.column)
        if self.Match(TokenType.IF):
            return self.ParseIf()
        if self.Match(TokenType.WHILE):
            return self.ParseWhile()
        if self.Match(TokenType.FOR):
            return self.ParseFor()
        if self.Match(TokenType.FOREACH):
            return self.ParseForeach()
        if self.Match(TokenType.IMPORT):
            return self.ParseImport()
        if self.Match(TokenType.EXPORT):
            return self.ParseExport()
        if self.Match(TokenType.LOG):
            return self.ParseLog()
        if self.Match(TokenType.EMIT):
            return self.ParseEmit()
        if self.Match(TokenType.IDENTIFIER) and self.Peek().type in (TokenType.COLON, TokenType.ASSIGN):
            Name = self.Advance()
            Operator = self.Advance()
            Value = self.ParseExpression()
            Kind = NodeType.VARIABLE_DECLARATION if Operator.type == TokenType.COLON else NodeType.ASSIGNMENT
            return ASTNode(Kind, Name.value, [Value], Name.line, Name.column)
        Start = self.CurrentToken
        Value = self.ParseExpression()
        return ASTNode(NodeType.EXPRESSION_STATEMENT, children=[Value], line=Start.line, column=Start.column)

    def ParseIf(self) -> ASTNode:
        Start = self.Advance()
        Condition = self.ParseExpression()
        Then = self.ParseRequiredBlock()
        Children = [Condition, Then]
        if self.Consume(TokenType.ELSE):
            Children.append(self.ParseRequiredBlock())
        return ASTNode(NodeType.IF_STATEMENT, children=Children, line=Start.line, column=Start.column)

    def ParseWhile(self) -> ASTNode:
        Start = self.Advance()
        Condition = self.ParseExpression()
        Body = self.ParseRequiredBlock()
        return ASTNode(NodeType.WHILE_STATEMENT, children=[Condition, Body], line=Start.line, column=Start.column)

    # Парсинг циклу FOR: FOR i IN collection { body }
    def ParseFor(self) -> ASTNode:
        Start = self.Advance()
        Iterator = self.Expect(TokenType.IDENTIFIER, "iterator name expected").value
        self.Expect(TokenType.IN, "IN expected after iterator")
        Collection = self.ParseExpression()
        Body = self.ParseRequiredBlock()
        return ASTNode(NodeType.FOR_STATEMENT, value={"iterator": Iterator, "in": "IN"}, children=[Collection, Body], line=Start.line, column=Start.column)

    # Парсинг циклу FOREACH: FOREACH item IN collection { body }
    def ParseForeach(self) -> ASTNode:
        Start = self.Advance()
        Iterator = self.Expect(TokenType.IDENTIFIER, "iterator name expected").value
        self.Expect(TokenType.IN, "IN expected after iterator")
        Collection = self.ParseExpression()
        Body = self.ParseRequiredBlock()
        return ASTNode(NodeType.FOREACH_STATEMENT, value={"iterator": Iterator, "in": "IN"}, children=[Collection, Body], line=Start.line, column=Start.column)

    # Парсинг IMPORT: IMPORT "module" або IMPORT module
    def ParseImport(self) -> ASTNode:
        Start = self.Advance()
        if self.Match(TokenType.STRING):
            Module = self.Advance().value
        else:
            Module = self.Expect(TokenType.IDENTIFIER, "module name expected").value
        return ASTNode(NodeType.IMPORT_STATEMENT, value=Module, line=Start.line, column=Start.column)

    # Парсинг EXPORT: EXPORT expression
    def ParseExport(self) -> ASTNode:
        Start = self.Advance()
        Value = self.ParseExpression()
        return ASTNode(NodeType.EXPORT_STATEMENT, children=[Value], line=Start.line, column=Start.column)

    # Парсинг LOG: log(expression) як оператор
    def ParseLog(self) -> ASTNode:
        Start = self.Advance()
        self.Expect(TokenType.LEFT_PAREN, "( expected after log")
        Args = []
        if not self.Match(TokenType.RIGHT_PAREN):
            Args.append(self.ParseExpression())
            while self.Consume(TokenType.COMMA):
                Args.append(self.ParseExpression())
        self.Expect(TokenType.RIGHT_PAREN, ") expected to close log arguments")
        return ASTNode(NodeType.LOG_STATEMENT, children=Args, line=Start.line, column=Start.column)

    # Парсинг EMIT: emit("event", data) як оператор
    def ParseEmit(self) -> ASTNode:
        Start = self.Advance()
        self.Expect(TokenType.LEFT_PAREN, "( expected after emit")
        Event = self.ParseExpression()
        Args = [Event]
        if self.Consume(TokenType.COMMA):
            Args.append(self.ParseExpression())
        self.Expect(TokenType.RIGHT_PAREN, ") expected to close emit arguments")
        return ASTNode(NodeType.EMIT_STATEMENT, children=Args, line=Start.line, column=Start.column)

    def ParseRequiredBlock(self) -> ASTNode:
        self.SkipLines()
        if self.Consume(TokenType.LEFT_BRACE):
            return self.ParseBlockItems(False)
        self.Error("statement block expected", self.CurrentToken)
        return ASTNode(NodeType.BLOCK)

    def ParseExpression(self, Minimum: int = 0) -> ASTNode:
        Left = self.ParsePrefix()
        while self.CurrentToken.type in self.Precedence and self.Precedence[self.CurrentToken.type] >= Minimum:
            Operator = self.Advance()
            Priority = self.Precedence[Operator.type]
            Right = self.ParseExpression(Priority + (0 if Operator.type == TokenType.POWER else 1))
            Left = ASTNode(NodeType.BINARY_EXPRESSION, Operator.value, [Left, Right], Left.line, Left.column)
        return Left

    def ParsePrefix(self) -> ASTNode:
        if self.Match(TokenType.MINUS, TokenType.NOT, TokenType.PLUS):
            Operator = self.Advance()
            return ASTNode(NodeType.UNARY_EXPRESSION, Operator.value, [self.ParsePrefix()], Operator.line, Operator.column)
        Node = self.ParsePrimary()
        while True:
            if self.Consume(TokenType.LEFT_PAREN):
                Args: List[ASTNode] = []
                while not self.Match(TokenType.RIGHT_PAREN, TokenType.EOF):
                    Args.append(self.ParseExpression())
                    if not self.Consume(TokenType.COMMA):
                        break
                self.Expect(TokenType.RIGHT_PAREN, "closing call expected")
                Node = ASTNode(NodeType.CALL_EXPRESSION, children=[Node] + Args, line=Node.line, column=Node.column)
                continue
            if self.Consume(TokenType.LEFT_BRACKET):
                Index = self.ParseExpression()
                self.Expect(TokenType.RIGHT_BRACKET, "closing index expected")
                Node = ASTNode(NodeType.MEMBER_EXPRESSION, "[]", [Node, Index], Node.line, Node.column)
                continue
            if self.Consume(TokenType.DOT):
                Member = self.Expect(TokenType.IDENTIFIER, "member name expected")
                Right = ASTNode(NodeType.IDENTIFIER, Member.value, line=Member.line, column=Member.column)
                Node = ASTNode(NodeType.MEMBER_EXPRESSION, ".", [Node, Right], Node.line, Node.column)
                continue
            break
        return Node

    def ParsePrimary(self) -> ASTNode:
        Item = self.CurrentToken
        if self.Consume(TokenType.NUMBER):
            return ASTNode(NodeType.LITERAL, Item.value, line=Item.line, column=Item.column)
        if self.Consume(TokenType.STRING):
            return ASTNode(NodeType.LITERAL, Item.value, line=Item.line, column=Item.column)
        if self.Consume(TokenType.BOOLEAN):
            return ASTNode(NodeType.LITERAL, Item.value.lower() == "true", line=Item.line, column=Item.column)
        if self.Consume(TokenType.IDENTIFIER, TokenType.LOG, TokenType.EMIT, TokenType.EXPORT, TokenType.IMPORT):
            return ASTNode(NodeType.IDENTIFIER, Item.value, line=Item.line, column=Item.column)
        if self.Consume(TokenType.LEFT_PAREN):
            Value = self.ParseExpression()
            self.Expect(TokenType.RIGHT_PAREN, "closing expression expected")
            return Value
        if self.Consume(TokenType.LEFT_BRACKET):
            Items: List[ASTNode] = []
            while not self.Match(TokenType.RIGHT_BRACKET, TokenType.EOF):
                Items.append(self.ParseExpression())
                if not self.Consume(TokenType.COMMA):
                    break
            self.Expect(TokenType.RIGHT_BRACKET, "closing array expected")
            return ASTNode(NodeType.ARRAY_LITERAL, children=Items, line=Item.line, column=Item.column)
        if self.Consume(TokenType.LEFT_BRACE):
            Items = []
            while not self.Match(TokenType.RIGHT_BRACE, TokenType.EOF):
                Key = self.Advance()
                self.Expect(TokenType.COLON, "object property separator expected")
                Items.append(ASTNode(NodeType.PROPERTY, Key.value, [self.ParseExpression()], Key.line, Key.column))
                if not self.Consume(TokenType.COMMA):
                    break
            self.Expect(TokenType.RIGHT_BRACE, "closing object expected")
            return ASTNode(NodeType.OBJECT_LITERAL, children=Items, line=Item.line, column=Item.column)
        self.Error("expression expected", Item)
        self.Advance()
        return ASTNode(NodeType.LITERAL, None, line=Item.line, column=Item.column)

    # Сумісність зі старим snake/camel API.
    Current = property(lambda self: self.CurrentToken)
    advance = Advance
    peek = Peek
    match = Match
    consume = Consume
    expect = Expect
    parse_expression = ParseExpression
    parse_statement = ParseStatement
    parse_block = ParseRequiredBlock

    def PrintAst(self, Node: ASTNode, Indent: int = 0) -> None:
        print("  " * Indent + Node.Str())
        for Child in Node.children:
            self.PrintAst(Child, Indent + 1)


__all__ = ["NodeType", "ASTNode", "ParserError", "Parser"]
