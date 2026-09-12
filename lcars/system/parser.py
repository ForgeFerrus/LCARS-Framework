# ◤ TITANIUM SYSTEM LCARS SCRIPT PARSER // STARFLEET CANON 🖖
# =============================================================================
# ФАЙЛ: lcars/system/parser.py
# ОПИС: Синтаксичний аналізатор (Parser) для мови LCARS Script (.lcars).
#       Будує абстрактне синтаксичне дерево (AST) за методом рекурсивного спуску
#       з підтримкою блоків симуляцій, детекторів, аналізаторів, функцій та подій.
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Zero-Except, Zero-Underscores, Strict PascalCase, Pure Classes).
# =============================================================================

from __future__ import annotations
from lcars.base.type import LCARS
from lcars.base.info import Version
from lcars.system.lexer import Lexer, Token, TokenType, LexerError

# ═════════════════════════════════════════════════════════════════════
# 1. ТИПИ ВУЗЛІВ AST (AST NODE TYPES)
# ═════════════════════════════════════════════════════════════════════
class NodeType(LCARS):
    # Корінь програми
    PROGRAM = "PROGRAM"

    # Декларації
    VARIABLE_DECLARATION   = "VARIABLE_DECLARATION"
    FUNCTION_DECLARATION   = "FUNCTION_DECLARATION"
    PROCEDURE_DECLARATION  = "PROCEDURE_DECLARATION"

    # Спеціальні конструкції LCARS
    SIMULATION_DECLARATION = "SIMULATION_DECLARATION"
    DETECTOR_DECLARATION   = "DETECTOR_DECLARATION"
    ANALYZER_DECLARATION   = "ANALYZER_DECLARATION"
    VISUALIZE_DECLARATION  = "VISUALIZE_DECLARATION"
    PLUGIN_DECLARATION     = "PLUGIN_DECLARATION"

    # Блоки та обробники
    BLOCK                  = "BLOCK"
    EVENT_HANDLER          = "EVENT_HANDLER"

    # Вирази
    BINARY_EXPRESSION      = "BINARY_EXPRESSION"
    UNARY_EXPRESSION       = "UNARY_EXPRESSION"
    CALL_EXPRESSION        = "CALL_EXPRESSION"
    MEMBER_EXPRESSION      = "MEMBER_EXPRESSION"
    LITERAL                = "LITERAL"
    IDENTIFIER             = "IDENTIFIER"

    # Інструкції та цикли
    ASSIGNMENT             = "ASSIGNMENT"
    RETURN_STATEMENT       = "RETURN_STATEMENT"
    IF_STATEMENT           = "IF_STATEMENT"
    FOR_STATEMENT          = "FOR_STATEMENT"
    WHILE_STATEMENT        = "WHILE_STATEMENT"
    FOREACH_STATEMENT      = "FOREACH_STATEMENT"
    EXPRESSION_STATEMENT   = "EXPRESSION_STATEMENT"

    # Структури даних
    ARRAY_LITERAL          = "ARRAY_LITERAL"
    OBJECT_LITERAL         = "OBJECT_LITERAL"
    PROPERTY               = "PROPERTY"

# ═════════════════════════════════════════════════════════════════════
# 2. ВУЗОЛ ДЕРЕВА ТА ПОМИЛКА ПАРСИНГУ
# ═════════════════════════════════════════════════════════════════════
class ASTNode(LCARS):
    # Базовий вузол синтаксичного дерева AST
    def __init__(self, Type: str, Value: any = None, Children: list[ASTNode] | None = None, Line: int = 0, Column: int = 0):
        super().__init__(Id=f"ASTNode.{Type}")
        self.Type = Type
        self.Value = Value
        self.Children = list(Children) if Children is not None else []
        self.Line = int(Line)
        self.Column = int(Column)

        # Сумісність для компілятора
        self.type = self.Type
        self.value = self.Value
        self.children = self.Children
        self.line = self.Line
        self.column = self.Column

    def AddChild(self, ChildNode: ASTNode) -> None:
        # Додавання дочірнього вузла
        if ChildNode:
            self.Children.append(ChildNode)

    # Аліас сумісності
    add_child = AddChild

    def __str__(self) -> str:
        return f"ASTNode({self.Type}, {repr(self.Value)})"

    def __repr__(self) -> str:
        return self.__str__()

class ParserError(Exception, LCARS):
    # Помилка синтаксичного розбору
    def __init__(self, Message: str, TokenObj: Token | None = None):
        Line = TokenObj.Line if TokenObj else 0
        Col = TokenObj.Column if TokenObj else 0
        super().__init__(f"ParserError at line {Line}, col {Col}: {Message}")
        self.Message = Message
        self.Token = TokenObj
        self.Line = Line
        self.Column = Col

# ═════════════════════════════════════════════════════════════════════
# 3. СИНТАКСИЧНИЙ АНАЛІЗАТОР (PARSER)
# ═════════════════════════════════════════════════════════════════════
class Parser(LCARS):
    # Рекурсивний синтаксичний аналізатор LCARS Script
    SystemVersion = Version.Release

    def __init__(self, Tokens: list[Token]):
        super().__init__(Id="Parser")
        self.Tokens = list(Tokens)
        self.Current = 0
        self.CurrentToken = self.Tokens[0] if self.Tokens else None

        # Сумісність
        self.tokens = self.Tokens
        self.current = self.Current
        self.current_token = self.CurrentToken

    def Advance(self) -> None:
        # Перехід до наступного токена
        if self.Current < len(self.Tokens) - 1:
            self.Current += 1
            self.CurrentToken = self.Tokens[self.Current]
        else:
            self.CurrentToken = None
        self.current = self.Current
        self.current_token = self.CurrentToken

    def Peek(self, Offset: int = 1) -> Token | None:
        # Перегляд токена попереду без зсуву курсору
        PeekPos = self.Current + Offset
        if PeekPos < len(self.Tokens):
            return self.Tokens[PeekPos]
        return None

    def Expect(self, ExpectedType: str) -> Token:
        # Очікування токена строго визначеного типу
        if self.CurrentToken and self.CurrentToken.Type == ExpectedType:
            Tok = self.CurrentToken
            self.Advance()
            return Tok
        Actual = self.CurrentToken.Type if self.CurrentToken else "EOF"
        raise ParserError(f"Expected {ExpectedType}, got {Actual}", self.CurrentToken)

    def Match(self, *ExpectedTypes: str) -> bool:
        # Перевірка чи відповідає поточний токен будь-якому з типів
        if self.CurrentToken and self.CurrentToken.Type in ExpectedTypes:
            return True
        return False

    def Consume(self, *ExpectedTypes: str) -> Token | None:
        # Споживання токена у разі збігу типу
        if self.Match(*ExpectedTypes):
            Tok = self.CurrentToken
            self.Advance()
            return Tok
        return None

    def SkipNewlines(self) -> None:
        # Пропуск токенів перенесення рядків
        while self.Consume(TokenType.NEWLINE):
            pass

    def Parse(self) -> ASTNode:
        # Головна точка парсингу програми
        self.SkipNewlines()
        ProgramNode = ASTNode(NodeType.PROGRAM)

        while self.CurrentToken and self.CurrentToken.Type != TokenType.EOF:
            self.SkipNewlines()
            if not self.CurrentToken or self.CurrentToken.Type == TokenType.EOF:
                break

            # Розпізнавання декларацій верхнього рівня
            if self.Match(TokenType.IDENTIFIER):
                Node = self.ParseVariableDeclaration()
                if Node:
                    ProgramNode.AddChild(Node)
            elif self.Match(TokenType.SIMULATION):
                ProgramNode.AddChild(self.ParseSimulationDeclaration())
            elif self.Match(TokenType.DETECTOR):
                ProgramNode.AddChild(self.ParseDetectorDeclaration())
            elif self.Match(TokenType.ANALYZER):
                ProgramNode.AddChild(self.ParseAnalyzerDeclaration())
            elif self.Match(TokenType.VISUALIZE):
                ProgramNode.AddChild(self.ParseVisualizeDeclaration())
            elif self.Match(TokenType.FUNCTION):
                ProgramNode.AddChild(self.ParseFunctionDeclaration())
            elif self.Match(TokenType.PROCEDURE):
                ProgramNode.AddChild(self.ParseProcedureDeclaration())
            elif self.Match(TokenType.PLUGIN):
                ProgramNode.AddChild(self.ParsePluginDeclaration())
            else:
                Stmt = self.ParseExpressionStatement()
                if Stmt:
                    ProgramNode.AddChild(Stmt)

            self.SkipNewlines()

        return ProgramNode

    def ParseVariableDeclaration(self) -> ASTNode | None:
        # Парсинг декларації змінної
        if not self.Match(TokenType.IDENTIFIER):
            return None

        NameTok = self.CurrentToken
        self.Advance()
        self.SkipNewlines()

        if not self.Consume(TokenType.COLON, TokenType.ASSIGN):
            self.CurrentToken = self.Tokens[self.Current]
            self.current = self.Current
            self.current_token = self.CurrentToken
            return None

        self.SkipNewlines()
        ValNode = self.ParseExpression()
        return ASTNode(NodeType.VARIABLE_DECLARATION, NameTok.Value, [ValNode], NameTok.Line, NameTok.Column)

    def ParseSimulationDeclaration(self) -> ASTNode:
        # Парсинг блоку симуляції Geant4
        SimTok = self.Expect(TokenType.SIMULATION)
        NameTok = self.Expect(TokenType.IDENTIFIER)
        Node = ASTNode(NodeType.SIMULATION_DECLARATION, NameTok.Value, Line=SimTok.Line, Column=SimTok.Column)

        self.SkipNewlines()
        self.Expect(TokenType.LEFT_BRACE)
        self.SkipNewlines()

        while not self.Consume(TokenType.RIGHT_BRACE):
            if self.CurrentToken and self.CurrentToken.Type == TokenType.EOF:
                raise ParserError("Unclosed simulation block", SimTok)
            self.SkipNewlines()

            if self.Match(TokenType.ON):
                Node.AddChild(self.ParseEventHandler())
            elif self.Match(TokenType.IDENTIFIER):
                ParamName = self.Expect(TokenType.IDENTIFIER)
                self.SkipNewlines()
                if not self.Match(TokenType.NEWLINE):
                    Val = self.ParseExpression()
                else:
                    Val = ASTNode(NodeType.LITERAL, None, Line=ParamName.Line, Column=ParamName.Column)
                Node.AddChild(ASTNode(NodeType.ASSIGNMENT, ParamName.Value, [Val], ParamName.Line, ParamName.Column))
            else:
                if self.CurrentToken and self.CurrentToken.Type != TokenType.NEWLINE:
                    self.Advance()
            self.SkipNewlines()

        return Node

    def ParseDetectorDeclaration(self) -> ASTNode:
        # Парсинг опису детектора
        DetTok = self.Expect(TokenType.DETECTOR)
        NameTok = self.Expect(TokenType.IDENTIFIER)
        Node = ASTNode(NodeType.DETECTOR_DECLARATION, NameTok.Value, Line=DetTok.Line, Column=DetTok.Column)

        self.SkipNewlines()
        self.Expect(TokenType.LEFT_BRACE)
        self.SkipNewlines()

        while not self.Consume(TokenType.RIGHT_BRACE):
            if self.CurrentToken and self.CurrentToken.Type == TokenType.EOF:
                raise ParserError("Unclosed detector block", DetTok)
            self.SkipNewlines()
            Stmt = self.ParseStatement()
            if Stmt:
                Node.AddChild(Stmt)
            self.SkipNewlines()

        return Node

    def ParseAnalyzerDeclaration(self) -> ASTNode:
        # Парсинг опису аналізатора
        AnTok = self.Expect(TokenType.ANALYZER)
        NameTok = self.Expect(TokenType.IDENTIFIER)
        Node = ASTNode(NodeType.ANALYZER_DECLARATION, NameTok.Value, Line=AnTok.Line, Column=AnTok.Column)

        self.SkipNewlines()
        self.Expect(TokenType.LEFT_BRACE)
        self.SkipNewlines()

        while not self.Consume(TokenType.RIGHT_BRACE):
            if self.CurrentToken and self.CurrentToken.Type == TokenType.EOF:
                raise ParserError("Unclosed analyzer block", AnTok)
            self.SkipNewlines()
            Stmt = self.ParseStatement()
            if Stmt:
                Node.AddChild(Stmt)
            self.SkipNewlines()

        return Node

    def ParseVisualizeDeclaration(self) -> ASTNode:
        # Парсинг блоку візуалізації
        VizTok = self.Expect(TokenType.VISUALIZE)
        NameTok = self.Expect(TokenType.IDENTIFIER)
        Node = ASTNode(NodeType.VISUALIZE_DECLARATION, NameTok.Value, Line=VizTok.Line, Column=VizTok.Column)

        self.SkipNewlines()
        self.Expect(TokenType.LEFT_BRACE)
        self.SkipNewlines()

        while not self.Consume(TokenType.RIGHT_BRACE):
            if self.CurrentToken and self.CurrentToken.Type == TokenType.EOF:
                raise ParserError("Unclosed visualize block", VizTok)
            self.SkipNewlines()
            Stmt = self.ParseStatement()
            if Stmt:
                Node.AddChild(Stmt)
            self.SkipNewlines()

        return Node

    def ParsePluginDeclaration(self) -> ASTNode:
        # Парсинг декларації плагіна
        PlugTok = self.Expect(TokenType.PLUGIN)
        NameTok = self.Expect(TokenType.IDENTIFIER)
        Node = ASTNode(NodeType.PLUGIN_DECLARATION, NameTok.Value, Line=PlugTok.Line, Column=PlugTok.Column)

        self.SkipNewlines()
        self.Expect(TokenType.LEFT_BRACE)
        self.SkipNewlines()

        while not self.Consume(TokenType.RIGHT_BRACE):
            if self.CurrentToken and self.CurrentToken.Type == TokenType.EOF:
                raise ParserError("Unclosed plugin block", PlugTok)
            self.SkipNewlines()
            Stmt = self.ParseStatement()
            if Stmt:
                Node.AddChild(Stmt)
            self.SkipNewlines()

        return Node

    def ParseFunctionDeclaration(self) -> ASTNode:
        # Парсинг декларації функції
        FuncTok = self.Expect(TokenType.FUNCTION)
        NameTok = self.Expect(TokenType.IDENTIFIER)
        Node = ASTNode(NodeType.FUNCTION_DECLARATION, NameTok.Value, Line=FuncTok.Line, Column=FuncTok.Column)

        self.SkipNewlines()
        self.Expect(TokenType.LEFT_PAREN)
        Params = []
        while not self.Consume(TokenType.RIGHT_PAREN):
            if self.CurrentToken and self.CurrentToken.Type == TokenType.EOF:
                raise ParserError("Unclosed function parameters", FuncTok)
            ParamTok = self.Expect(TokenType.IDENTIFIER)
            Params.append(ASTNode(NodeType.IDENTIFIER, ParamTok.Value, Line=ParamTok.Line, Column=ParamTok.Column))
            self.Consume(TokenType.COMMA)
            self.SkipNewlines()
        Node.Children.extend(Params)

        if self.Consume(TokenType.ARROW):
            RetType = self.Expect(TokenType.IDENTIFIER)
            Node.AddChild(ASTNode(NodeType.IDENTIFIER, RetType.Value, Line=RetType.Line, Column=RetType.Column))

        self.SkipNewlines()
        Node.AddChild(self.ParseBlock())
        return Node

    def ParseProcedureDeclaration(self) -> ASTNode:
        # Парсинг декларації процедури
        ProcTok = self.Expect(TokenType.PROCEDURE)
        NameTok = self.Expect(TokenType.IDENTIFIER)
        Node = ASTNode(NodeType.PROCEDURE_DECLARATION, NameTok.Value, Line=ProcTok.Line, Column=ProcTok.Column)

        self.SkipNewlines()
        self.Expect(TokenType.LEFT_PAREN)
        Params = []
        while not self.Consume(TokenType.RIGHT_PAREN):
            if self.CurrentToken and self.CurrentToken.Type == TokenType.EOF:
                raise ParserError("Unclosed procedure parameters", ProcTok)
            ParamTok = self.Expect(TokenType.IDENTIFIER)
            Params.append(ASTNode(NodeType.IDENTIFIER, ParamTok.Value, Line=ParamTok.Line, Column=ParamTok.Column))
            self.Consume(TokenType.COMMA)
            self.SkipNewlines()
        Node.Children.extend(Params)

        self.SkipNewlines()
        Node.AddChild(self.ParseBlock())
        return Node

    def ParseEventHandler(self) -> ASTNode:
        # Парсинг блоку обробника події (ON START / ON COMPLETE)
        OnTok = self.Expect(TokenType.ON)
        EvtTok = self.CurrentToken
        self.Advance()
        Node = ASTNode(NodeType.EVENT_HANDLER, EvtTok.Value if EvtTok else "CUSTOM", Line=OnTok.Line, Column=OnTok.Column)

        if self.Consume(TokenType.LEFT_PAREN):
            while not self.Consume(TokenType.RIGHT_PAREN):
                if self.CurrentToken and self.CurrentToken.Type == TokenType.EOF:
                    raise ParserError("Unclosed event parameters", OnTok)
                Node.AddChild(self.ParseExpression())
                self.Consume(TokenType.COMMA)
                self.SkipNewlines()

        self.SkipNewlines()
        Node.AddChild(self.ParseBlock())
        return Node

    def ParseBlock(self) -> ASTNode:
        # Парсинг складеного блоку інструкцій у фігурних дужках { ... }
        self.Expect(TokenType.LEFT_BRACE)
        self.SkipNewlines()
        BlockNode = ASTNode(NodeType.BLOCK)

        while not self.Consume(TokenType.RIGHT_BRACE):
            if self.CurrentToken and self.CurrentToken.Type == TokenType.EOF:
                raise ParserError("Unclosed block", self.CurrentToken)
            self.SkipNewlines()
            Stmt = self.ParseStatement()
            if Stmt:
                BlockNode.AddChild(Stmt)
            self.SkipNewlines()

        return BlockNode

    def ParseStatement(self) -> ASTNode | None:
        # Парсинг окремої інструкції
        if self.Match(TokenType.RETURN):
            return self.ParseReturnStatement()
        elif self.Match(TokenType.IF):
            return self.ParseIfStatement()
        elif self.Match(TokenType.FOR):
            return self.ParseForStatement()
        elif self.Match(TokenType.WHILE):
            return self.ParseWhileStatement()
        elif self.Match(TokenType.FOREACH):
            return self.ParseForeachStatement()
        elif self.Match(TokenType.IDENTIFIER):
            # Можлива інструкція присвоєння або виклик функції
            Expr = self.ParseExpression()
            if Expr:
                if self.Consume(TokenType.ASSIGN):
                    Val = self.ParseExpression()
                    return ASTNode(NodeType.ASSIGNMENT, None, [Expr, Val], Expr.Line, Expr.Column)
                return ASTNode(NodeType.EXPRESSION_STATEMENT, None, [Expr], Expr.Line, Expr.Column)
        return None

    def ParseReturnStatement(self) -> ASTNode:
        # Парсинг інструкції повернення значення
        RetTok = self.Expect(TokenType.RETURN)
        Val = None
        if not self.Match(TokenType.NEWLINE, TokenType.RIGHT_BRACE):
            Val = self.ParseExpression()
        return ASTNode(NodeType.RETURN_STATEMENT, None, [Val] if Val else [], RetTok.Line, RetTok.Column)

    def ParseIfStatement(self) -> ASTNode:
        # Парсинг умовного розгалуження IF / ELSE
        IfTok = self.Expect(TokenType.IF)
        Cond = self.ParseExpression()
        self.SkipNewlines()
        ThenBlock = self.ParseBlock()
        Children = [Cond, ThenBlock]

        self.SkipNewlines()
        if self.Consume(TokenType.ELSE):
            self.SkipNewlines()
            ElseBlock = self.ParseBlock() if self.Match(TokenType.LEFT_BRACE) else self.ParseIfStatement()
            Children.append(ElseBlock)

        return ASTNode(NodeType.IF_STATEMENT, None, Children, IfTok.Line, IfTok.Column)

    def ParseForStatement(self) -> ASTNode:
        # Парсинг числового циклу FOR x FROM a TO b
        ForTok = self.Expect(TokenType.FOR)
        VarTok = self.Expect(TokenType.IDENTIFIER)
        self.Expect(TokenType.FROM)
        StartVal = self.ParseExpression()
        self.Expect(TokenType.TO)
        EndVal = self.ParseExpression()
        self.SkipNewlines()
        Body = self.ParseBlock()
        return ASTNode(NodeType.FOR_STATEMENT, VarTok.Value, [StartVal, EndVal, Body], ForTok.Line, ForTok.Column)

    def ParseWhileStatement(self) -> ASTNode:
        # Парсинг умовного циклу WHILE
        WhileTok = self.Expect(TokenType.WHILE)
        Cond = self.ParseExpression()
        self.SkipNewlines()
        Body = self.ParseBlock()
        return ASTNode(NodeType.WHILE_STATEMENT, None, [Cond, Body], WhileTok.Line, WhileTok.Column)

    def ParseForeachStatement(self) -> ASTNode:
        # Парсинг ітераційного циклу FOREACH x IN collection
        ForeachTok = self.Expect(TokenType.FOREACH)
        VarTok = self.Expect(TokenType.IDENTIFIER)
        self.Expect(TokenType.IN)
        Collection = self.ParseExpression()
        self.SkipNewlines()
        Body = self.ParseBlock()
        return ASTNode(NodeType.FOREACH_STATEMENT, VarTok.Value, [Collection, Body], ForeachTok.Line, ForeachTok.Column)

    def ParseExpressionStatement(self) -> ASTNode | None:
        # Парсинг інструкції виразу або присвоєння
        Expr = self.ParseExpression()
        if Expr:
            if self.Consume(TokenType.ASSIGN):
                Val = self.ParseExpression()
                return ASTNode(NodeType.ASSIGNMENT, None, [Expr, Val], Expr.Line, Expr.Column)
            return ASTNode(NodeType.EXPRESSION_STATEMENT, None, [Expr], Expr.Line, Expr.Column)
        return None

    def ParseExpression(self) -> ASTNode:
        # Головний парсер виразів (Logical OR)
        return self.ParseLogicalOr()

    def ParseLogicalOr(self) -> ASTNode:
        Left = self.ParseLogicalAnd()
        while self.Match(TokenType.OR):
            OpTok = self.Consume(TokenType.OR)
            Right = self.ParseLogicalAnd()
            Left = ASTNode(NodeType.BINARY_EXPRESSION, OpTok.Value if OpTok else "or", [Left, Right], Left.Line, Left.Column)
        return Left

    def ParseLogicalAnd(self) -> ASTNode:
        Left = self.ParseEquality()
        while self.Match(TokenType.AND):
            OpTok = self.Consume(TokenType.AND)
            Right = self.ParseEquality()
            Left = ASTNode(NodeType.BINARY_EXPRESSION, OpTok.Value if OpTok else "and", [Left, Right], Left.Line, Left.Column)
        return Left

    def ParseEquality(self) -> ASTNode:
        Left = self.ParseComparison()
        while self.Match(TokenType.EQUAL, TokenType.NOT_EQUAL):
            OpTok = self.CurrentToken
            self.Advance()
            Right = self.ParseComparison()
            Left = ASTNode(NodeType.BINARY_EXPRESSION, OpTok.Value if OpTok else "==", [Left, Right], Left.Line, Left.Column)
        return Left

    def ParseComparison(self) -> ASTNode:
        Left = self.ParseTerm()
        while self.Match(TokenType.LESS, TokenType.LESS_EQUAL, TokenType.GREATER, TokenType.GREATER_EQUAL):
            OpTok = self.CurrentToken
            self.Advance()
            Right = self.ParseTerm()
            Left = ASTNode(NodeType.BINARY_EXPRESSION, OpTok.Value if OpTok else "<", [Left, Right], Left.Line, Left.Column)
        return Left

    def ParseTerm(self) -> ASTNode:
        Left = self.ParseFactor()
        while self.Match(TokenType.PLUS, TokenType.MINUS):
            OpTok = self.CurrentToken
            self.Advance()
            Right = self.ParseFactor()
            Left = ASTNode(NodeType.BINARY_EXPRESSION, OpTok.Value if OpTok else "+", [Left, Right], Left.Line, Left.Column)
        return Left

    def ParseFactor(self) -> ASTNode:
        Left = self.ParseUnary()
        while self.Match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO, TokenType.POWER):
            OpTok = self.CurrentToken
            self.Advance()
            Right = self.ParseUnary()
            Left = ASTNode(NodeType.BINARY_EXPRESSION, OpTok.Value if OpTok else "*", [Left, Right], Left.Line, Left.Column)
        return Left

    def ParseUnary(self) -> ASTNode:
        if self.Match(TokenType.NOT, TokenType.MINUS, TokenType.PLUS):
            OpTok = self.CurrentToken
            self.Advance()
            Operand = self.ParseUnary()
            return ASTNode(NodeType.UNARY_EXPRESSION, OpTok.Value if OpTok else "-", [Operand], OpTok.Line if OpTok else 0, OpTok.Column if OpTok else 0)
        return self.ParseCall()

    def ParseCall(self) -> ASTNode:
        Primary = self.ParsePrimary()
        while True:
            if self.Consume(TokenType.LEFT_PAREN):
                Args = []
                while not self.Consume(TokenType.RIGHT_PAREN):
                    if self.CurrentToken and self.CurrentToken.Type == TokenType.EOF:
                        raise ParserError("Unclosed function call arguments", self.CurrentToken)
                    Args.append(self.ParseExpression())
                    self.Consume(TokenType.COMMA)
                    self.SkipNewlines()
                Primary = ASTNode(NodeType.CALL_EXPRESSION, None, [Primary] + Args, Primary.Line, Primary.Column)
            elif self.Consume(TokenType.DOT):
                Member = self.Expect(TokenType.IDENTIFIER)
                MemberNode = ASTNode(NodeType.IDENTIFIER, Member.Value, Line=Member.Line, Column=Member.Column)
                Primary = ASTNode(NodeType.MEMBER_EXPRESSION, ".", [Primary, MemberNode], Primary.Line, Primary.Column)
            elif self.Consume(TokenType.LEFT_BRACKET):
                IdxNode = self.ParseExpression()
                self.Expect(TokenType.RIGHT_BRACKET)
                Primary = ASTNode(NodeType.MEMBER_EXPRESSION, "[]", [Primary, IdxNode], Primary.Line, Primary.Column)
            else:
                break
        return Primary

    def ParsePrimary(self) -> ASTNode:
        if self.Match(TokenType.NUMBER):
            Tok = self.Consume(TokenType.NUMBER)
            NumStr = Tok.Value if Tok else "0"
            NumVal = float(NumStr) if "." in NumStr else int(NumStr)
            return ASTNode(NodeType.LITERAL, Tok.Value if Tok else "", Line=Tok.Line if Tok else 0, Column=Tok.Column if Tok else 0)
        elif self.Match(TokenType.BOOLEAN):
            Tok = self.Consume(TokenType.BOOLEAN)
            return ASTNode(NodeType.LITERAL, (Tok.Value.lower() == "true") if Tok else False, Line=Tok.Line if Tok else 0, Column=Tok.Column if Tok else 0)
        elif self.Consume(TokenType.LEFT_BRACKET):
            Elements = []
            while not self.Consume(TokenType.RIGHT_BRACKET):
                if self.CurrentToken and self.CurrentToken.Type == TokenType.EOF:
                    raise ParserError("Unclosed array literal", self.CurrentToken)
                Elements.append(self.ParseExpression())
                self.Consume(TokenType.COMMA)
                self.SkipNewlines()
            return ASTNode(NodeType.ARRAY_LITERAL, None, Elements)
        elif self.Consume(TokenType.LEFT_BRACE):
            Props = []
            self.SkipNewlines()
            while not self.Consume(TokenType.RIGHT_BRACE):
                if self.CurrentToken and self.CurrentToken.Type == TokenType.EOF:
                    raise ParserError("Unclosed object literal", self.CurrentToken)
                self.SkipNewlines()
                KeyTok = self.Consume(TokenType.IDENTIFIER, TokenType.STRING)
                if not KeyTok:
                    raise ParserError(f"Expected object key, got {self.CurrentToken}", self.CurrentToken)
                self.Expect(TokenType.COLON)
                self.SkipNewlines()
                ValNode = self.ParseExpression()
                Props.append(ASTNode(NodeType.PROPERTY, KeyTok.Value, [ValNode], KeyTok.Line, KeyTok.Column))
                self.Consume(TokenType.COMMA)
                self.SkipNewlines()
            return ASTNode(NodeType.OBJECT_LITERAL, None, Props)
        elif self.Consume(TokenType.LEFT_PAREN):
            Expr = self.ParseExpression()
            self.Expect(TokenType.RIGHT_PAREN)
            return Expr
        elif self.Match(TokenType.IDENTIFIER, TokenType.LOG, TokenType.EMIT, TokenType.EXPORT, TokenType.IMPORT):
            Tok = self.CurrentToken
            self.Advance()
            return ASTNode(NodeType.IDENTIFIER, Tok.Value if Tok else "", Line=Tok.Line if Tok else 0, Column=Tok.Column if Tok else 0)
        raise ParserError(f"Unexpected token: {self.CurrentToken}", self.CurrentToken)

