# LCARS FRAMEWORK v1.0.0-ALPHA
# Парсер LCARS Script (LCARS Script Parser)
# ОПИС: Синтаксичний аналізатор для мови LCARS Script. Будує AST (Abstract Syntax Tree)
#        з токенів отриманих від лексера. Підтримує декларації змінних, функцій,
#        процедур, симуляцій, детекторів, аналізаторів та візуалізацій.
# АРХІТЕКТУРА: Рекурсивний спуск з підтримкою вкладених структур
# ВЕРСІЯ: v1.0.0-ALPHA

# Titanium Bridge Migration: from typing import List, Optional, Union, Any, Dict
# Titanium Bridge Migration: from dataclasses import dataclass
# Titanium Bridge Migration: from enum import Enum

from .lexer import Lexer, Token, TokenType, LexerError


class NodeType(Enum):
    """Типи вузлів AST"""
    
    # Програма
    PROGRAM = "PROGRAM"
    
    # Декларації
    VARIABLE_DECLARATION = "VARIABLE_DECLARATION"
    FUNCTION_DECLARATION = "FUNCTION_DECLARATION"
    PROCEDURE_DECLARATION = "PROCEDURE_DECLARATION"
    
    # Спеціальні конструкції LCARS
    SIMULATION_DECLARATION = "SIMULATION_DECLARATION"
    DETECTOR_DECLARATION = "DETECTOR_DECLARATION"
    ANALYZER_DECLARATION = "ANALYZER_DECLARATION"
    VISUALIZE_DECLARATION = "VISUALIZE_DECLARATION"
    PLUGIN_DECLARATION = "PLUGIN_DECLARATION"
    
    # Блоки коду
    BLOCK = "BLOCK"
    EVENT_HANDLER = "EVENT_HANDLER"
    
    # Вирази
    BINARY_EXPRESSION = "BINARY_EXPRESSION"
    UNARY_EXPRESSION = "UNARY_EXPRESSION"
    CALL_EXPRESSION = "CALL_EXPRESSION"
    MEMBER_EXPRESSION = "MEMBER_EXPRESSION"
    LITERAL = "LITERAL"
    IDENTIFIER = "IDENTIFIER"
    
    # Інструкції
    ASSIGNMENT = "ASSIGNMENT"
    RETURN_STATEMENT = "RETURN_STATEMENT"
    IF_STATEMENT = "IF_STATEMENT"
    FOR_STATEMENT = "FOR_STATEMENT"
    WHILE_STATEMENT = "WHILE_STATEMENT"
    FOREACH_STATEMENT = "FOREACH_STATEMENT"
    EXPRESSION_STATEMENT = "EXPRESSION_STATEMENT"
    
    # Структури даних
    ARRAY_LITERAL = "ARRAY_LITERAL"
    OBJECT_LITERAL = "OBJECT_LITERAL"
    PROPERTY = "PROPERTY"


@dataclass
class ASTNode:
    """Базовий вузол AST"""
    type: NodeType
    value: Any = None
    children: List['ASTNode'] = None
    line: int = 0
    column: int = 0
    
    def __post_init__(self):
        if self.children is None:
            self.children = []
    
    def add_child(self, child: 'ASTNode'):
        """Додати дочірній вузол"""
        self.children.append(child)
    
    def __str__(self):
        return f"ASTNode({self.type.value}, {self.value})"
    
    def __repr__(self):
        return self.__str__()


class ParserError(Exception):
    """Помилка парсингу"""
    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(f"Parser Error at line {token.line}, column {token.column}: {message}")


class Parser:
    """Парсер для LCARS Script"""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
        self.current_token = self.tokens[0] if tokens else None
    
    def advance(self):
        """Перейти до наступного токена"""
        if self.current < len(self.tokens) - 1:
            self.current += 1
            self.current_token = self.tokens[self.current]
        else:
            self.current_token = None
    
    def peek(self, offset: int = 1) -> Optional[Token]:
        """Подивитися наступний токен"""
        peek_pos = self.current + offset
        if peek_pos < len(self.tokens):
            return self.tokens[peek_pos]
        return None
    
    def expect(self, token_type: TokenType) -> Token:
        """Очікувати токен певного типу"""
        if self.current_token and self.current_token.type == token_type:
            token = self.current_token
            self.advance()
            return token
        else:
            expected_type = token_type.value if token_type else "None"
            actual_type = self.current_token.type.value if self.current_token else "EOF"
            raise ParserError(f"Expected {expected_type}, got {actual_type}", self.current_token)
    
    def match(self, *token_types: TokenType) -> bool:
        """Перевірити, чи поточний токен відповідає одному з типів"""
        if self.current_token and self.current_token.type in token_types:
            return True
        return False
    
    def consume(self, *token_types: TokenType) -> Optional[Token]:
        """Спожити токен, якщо він відповідає типу"""
        if self.match(*token_types):
            token = self.current_token
            self.advance()
            return token
        return None
    
    def skip_newlines(self):
        """Пропустити токени NEWLINE"""
        while self.consume(TokenType.NEWLINE):
            pass
    
    def parse(self) -> ASTNode:
        """Парсити всю програму"""
        self.skip_newlines()
        
        program = ASTNode(NodeType.PROGRAM)
        
        while self.current_token and self.current_token.type != TokenType.EOF:
            self.skip_newlines()
            
            if not self.current_token or self.current_token.type == TokenType.EOF:
                break
            
            # Парсимо різні типи декларацій
            if self.match(TokenType.IDENTIFIER):
                # Може бути декларація змінної
                node = self.parse_variable_declaration()
                if node:
                    program.add_child(node)
            elif self.match(TokenType.SIMULATION):
                node = self.parse_simulation_declaration()
                program.add_child(node)
            elif self.match(TokenType.DETECTOR):
                node = self.parse_detector_declaration()
                program.add_child(node)
            elif self.match(TokenType.ANALYZER):
                node = self.parse_analyzer_declaration()
                program.add_child(node)
            elif self.match(TokenType.VISUALIZE):
                node = self.parse_visualize_declaration()
                program.add_child(node)
            elif self.match(TokenType.FUNCTION):
                node = self.parse_function_declaration()
                program.add_child(node)
            elif self.match(TokenType.PROCEDURE):
                node = self.parse_procedure_declaration()
                program.add_child(node)
            elif self.match(TokenType.PLUGIN):
                node = self.parse_plugin_declaration()
                program.add_child(node)
            else:
                # Спробувати парсити як вираз
                node = self.parse_expression_statement()
                if node:
                    program.add_child(node)
            
            self.skip_newlines()
        
        return program
    
    def parse_variable_declaration(self) -> Optional[ASTNode]:
        """Парсити декларацію змінної"""
        if not self.match(TokenType.IDENTIFIER):
            return None
        
        name_token = self.current_token
        self.advance()
        self.skip_newlines()
        
        if not self.consume(TokenType.COLON):
            # Це не декларація змінної, повернемо як вираз
            # Повертаємо токен назад
            self.current = max(0, self.current - 1)
            self.current_token = self.tokens[self.current]
            return None
        
        self.skip_newlines()
        value = self.parse_expression()
        
        node = ASTNode(
            NodeType.VARIABLE_DECLARATION,
            name_token.value,
            [value],
            name_token.line,
            name_token.column
        )
        
        return node
    
    def parse_simulation_declaration(self) -> ASTNode:
        """Парсити декларацію симуляції"""
        sim_token = self.expect(TokenType.SIMULATION)
        name_token = self.expect(TokenType.IDENTIFIER)
        
        node = ASTNode(
            NodeType.SIMULATION_DECLARATION,
            name_token.value,
            line=sim_token.line,
            column=sim_token.column
        )
        
        self.skip_newlines()
        self.expect(TokenType.LEFT_BRACE)
        self.skip_newlines()
        
        # Парсимо тіло симуляції
        while not self.consume(TokenType.RIGHT_BRACE):
            if self.current_token.type == TokenType.EOF:
                raise ParserError("Unclosed simulation block", sim_token)
            
            self.skip_newlines()
            
            if self.match(TokenType.ON):
                event_handler = self.parse_event_handler()
                node.add_child(event_handler)
            elif self.match(TokenType.IDENTIFIER):
                # Може бути параметр симуляції
                if True:
                    param_node = self.parse_simulation_parameter()
                    node.add_child(param_node)
                if False: # Removed except block
                    # Якщо це не параметр, пропустити токен
                    if "event handler keyword" in str(e):
                        # Пропустити і дати можливість обробити як обробник подій
                        continue
                    else:
                        raise e
            elif self.current_token and self.current_token.type in [TokenType.NUMBER, TokenType.STRING, TokenType.BOOLEAN]:
                # Це може бути значення без імені параметра
                stmt = self.parse_expression_statement()
                if stmt:
                    node.add_child(stmt)
            else:
                # Пропустити невідомий токен
                if self.current_token and self.current_token.type != TokenType.NEWLINE:
                    self.advance()
            
            self.skip_newlines()
        
        return node
    
    def parse_simulation_parameter(self) -> ASTNode:
        """Парсити параметр симуляції"""
        param_name = self.expect(TokenType.IDENTIFIER)
        self.skip_newlines()
        
        # Перевірити, чи це не ключове слово для обробника подій
        if param_name.value in ['START', 'COMPLETE', 'ERROR', 'PROGRESS', 'HIT', 'READY', 'LOAD']:
            # Це не параметр, а частина обробника подій
            # Повертаємо токен назад для обробки в основному циклі
            self.current = max(0, self.current - 1)
            self.current_token = self.tokens[self.current]
            raise ParserError(f"Expected parameter, got event handler keyword", param_name)
        
        # Якщо наступний токен - це не NEWLINE, то це значення
        if not self.match(TokenType.NEWLINE):
            value = self.parse_expression()
        else:
            # Параметр без значення
            value = ASTNode(NodeType.LITERAL, None, line=param_name.line, column=param_name.column)
        
        node = ASTNode(
            NodeType.ASSIGNMENT,
            param_name.value,
            [value],
            param_name.line,
            param_name.column
        )
        
        return node
    
    def parse_detector_declaration(self) -> ASTNode:
        """Парсити декларацію детектора"""
        detector_token = self.expect(TokenType.DETECTOR)
        name_token = self.expect(TokenType.IDENTIFIER)
        
        node = ASTNode(
            NodeType.DETECTOR_DECLARATION,
            name_token.value,
            line=detector_token.line,
            column=detector_token.column
        )
        
        self.skip_newlines()
        self.expect(TokenType.LEFT_BRACE)
        self.skip_newlines()
        
        # Парсимо тіло детектора
        while not self.consume(TokenType.RIGHT_BRACE):
            if self.current_token.type == TokenType.EOF:
                raise ParserError("Unclosed detector block", detector_token)
            
            self.skip_newlines()
            stmt = self.parse_statement()
            if stmt:
                node.add_child(stmt)
            self.skip_newlines()
        
        return node
    
    def parse_analyzer_declaration(self) -> ASTNode:
        """Парсити декларацію аналізатора"""
        analyzer_token = self.expect(TokenType.ANALYZER)
        name_token = self.expect(TokenType.IDENTIFIER)
        
        node = ASTNode(
            NodeType.ANALYZER_DECLARATION,
            name_token.value,
            line=analyzer_token.line,
            column=analyzer_token.column
        )
        
        self.skip_newlines()
        self.expect(TokenType.LEFT_BRACE)
        self.skip_newlines()
        
        # Парсимо тіло аналізатора
        while not self.consume(TokenType.RIGHT_BRACE):
            if self.current_token.type == TokenType.EOF:
                raise ParserError("Unclosed analyzer block", analyzer_token)
            
            self.skip_newlines()
            stmt = self.parse_statement()
            if stmt:
                node.add_child(stmt)
            self.skip_newlines()
        
        return node
    
    def parse_visualize_declaration(self) -> ASTNode:
        """Парсити декларацію візуалізації"""
        viz_token = self.expect(TokenType.VISUALIZE)
        name_token = self.expect(TokenType.IDENTIFIER)
        
        node = ASTNode(
            NodeType.VISUALIZE_DECLARATION,
            name_token.value,
            line=viz_token.line,
            column=viz_token.column
        )
        
        self.skip_newlines()
        self.expect(TokenType.LEFT_BRACE)
        self.skip_newlines()
        
        # Парсимо тіло візуалізації
        while not self.consume(TokenType.RIGHT_BRACE):
            if self.current_token.type == TokenType.EOF:
                raise ParserError("Unclosed visualize block", viz_token)
            
            self.skip_newlines()
            stmt = self.parse_statement()
            if stmt:
                node.add_child(stmt)
            self.skip_newlines()
        
        return node
    
    def parse_function_declaration(self) -> ASTNode:
        """Парсити декларацію функції"""
        func_token = self.expect(TokenType.FUNCTION)
        name_token = self.expect(TokenType.IDENTIFIER)
        
        node = ASTNode(
            NodeType.FUNCTION_DECLARATION,
            name_token.value,
            line=func_token.line,
            column=func_token.column
        )
        
        # Парсимо параметри
        self.skip_newlines()
        self.expect(TokenType.LEFT_PAREN)
        
        params = []
        while not self.consume(TokenType.RIGHT_PAREN):
            if self.current_token.type == TokenType.EOF:
                raise ParserError("Unclosed function parameters", func_token)
            
            param_token = self.expect(TokenType.IDENTIFIER)
            params.append(ASTNode(NodeType.IDENTIFIER, param_token.value, line=param_token.line, column=param_token.column))
            
            self.consume(TokenType.COMMA)
            self.skip_newlines()
        
        # Додаємо параметри як дочірні вузли
        node.children.extend(params)
        
        # Парсимо тип повернення (опціонально)
        if self.consume(TokenType.ARROW):
            return_type = self.expect(TokenType.IDENTIFIER)
            node.add_child(ASTNode(NodeType.IDENTIFIER, return_type.value, line=return_type.line, column=return_type.column))
        
        # Парсимо тіло функції
        self.skip_newlines()
        body = self.parse_block()
        node.add_child(body)
        
        return node
    
    def parse_procedure_declaration(self) -> ASTNode:
        """Парсити декларацію процедури"""
        proc_token = self.expect(TokenType.PROCEDURE)
        name_token = self.expect(TokenType.IDENTIFIER)
        
        node = ASTNode(
            NodeType.PROCEDURE_DECLARATION,
            name_token.value,
            line=proc_token.line,
            column=proc_token.column
        )
        
        # Парсимо параметри
        self.skip_newlines()
        self.expect(TokenType.LEFT_PAREN)
        
        params = []
        while not self.consume(TokenType.RIGHT_PAREN):
            if self.current_token.type == TokenType.EOF:
                raise ParserError("Unclosed procedure parameters", proc_token)
            
            param_token = self.expect(TokenType.IDENTIFIER)
            params.append(ASTNode(NodeType.IDENTIFIER, param_token.value, line=param_token.line, column=param_token.column))
            
            self.consume(TokenType.COMMA)
            self.skip_newlines()
        
        # Додаємо параметри як дочірні вузли
        node.children.extend(params)
        
        # Парсимо тіло процедури
        self.skip_newlines()
        body = self.parse_block()
        node.add_child(body)
        
        return node
    
    def parse_plugin_declaration(self) -> ASTNode:
        """Парсити декларацію плагіна"""
        plugin_token = self.expect(TokenType.PLUGIN)
        name_token = self.expect(TokenType.IDENTIFIER)
        
        node = ASTNode(
            NodeType.PLUGIN_DECLARATION,
            name_token.value,
            line=plugin_token.line,
            column=plugin_token.column
        )
        
        self.skip_newlines()
        self.expect(TokenType.LEFT_BRACE)
        self.skip_newlines()
        
        # Парсимо тіло плагіна
        while not self.consume(TokenType.RIGHT_BRACE):
            if self.current_token.type == TokenType.EOF:
                raise ParserError("Unclosed plugin block", plugin_token)
            
            self.skip_newlines()
            stmt = self.parse_statement()
            if stmt:
                node.add_child(stmt)
            self.skip_newlines()
        
        return node
    
    def parse_event_handler(self) -> ASTNode:
        """Парсити обробник подій"""
        on_token = self.expect(TokenType.ON)
        
        # Обробка різних типів подій
        if self.match(TokenType.START):
            event_token = self.tokens[self.current - 1]
        elif self.match(TokenType.COMPLETE):
            event_token = self.tokens[self.current - 1]
        elif self.match(TokenType.ERROR):
            event_token = self.tokens[self.current - 1]
        elif self.match(TokenType.PROGRESS):
            event_token = self.tokens[self.current - 1]
        elif self.match(TokenType.HIT):
            event_token = self.tokens[self.current - 1]
        elif self.match(TokenType.READY):
            event_token = self.tokens[self.current - 1]
        elif self.match(TokenType.LOAD):
            event_token = self.tokens[self.current - 1]
        else:
            # Кастомна подія
            event_token = self.expect(TokenType.IDENTIFIER)
        
        node = ASTNode(
            NodeType.EVENT_HANDLER,
            event_token.value,
            line=on_token.line,
            column=on_token.column
        )
        
        # Парсимо параметри події (опціонально)
        if self.consume(TokenType.LEFT_PAREN):
            while not self.consume(TokenType.RIGHT_PAREN):
                if self.current_token.type == TokenType.EOF:
                    raise ParserError("Unclosed event parameters", on_token)
                
                param = self.parse_expression()
                node.add_child(param)
                
                self.consume(TokenType.COMMA)
                self.skip_newlines()
        
        # Парсимо тіло обробника
        self.skip_newlines()
        body = self.parse_block()
        node.add_child(body)
        
        return node
    
    def parse_block(self) -> ASTNode:
        """Парсити блок коду"""
        self.expect(TokenType.LEFT_BRACE)
        self.skip_newlines()
        
        block = ASTNode(NodeType.BLOCK)
        
        while not self.consume(TokenType.RIGHT_BRACE):
            if self.current_token.type == TokenType.EOF:
                raise ParserError("Unclosed block", self.current_token)
            
            self.skip_newlines()
            stmt = self.parse_statement()
            if stmt:
                block.add_child(stmt)
            self.skip_newlines()
        
        return block
    
    def parse_statement(self) -> Optional[ASTNode]:
        """Парсити інструкцію"""
        if self.match(TokenType.RETURN):
            return self.parse_return_statement()
        elif self.match(TokenType.IF):
            return self.parse_if_statement()
        elif self.match(TokenType.FOR):
            return self.parse_for_statement()
        elif self.match(TokenType.WHILE):
            return self.parse_while_statement()
        elif self.match(TokenType.FOREACH):
            return self.parse_foreach_statement()
        else:
            return self.parse_expression_statement()
    
    def parse_return_statement(self) -> ASTNode:
        """Парсити return інструкцію"""
        return_token = self.expect(TokenType.RETURN)
        
        value = None
        if not self.match(TokenType.NEWLINE, TokenType.RIGHT_BRACE):
            value = self.parse_expression()
        
        node = ASTNode(
            NodeType.RETURN_STATEMENT,
            None,
            [value] if value else [],
            return_token.line,
            return_token.column
        )
        
        return node
    
    def parse_if_statement(self) -> ASTNode:
        """Парсити if інструкцію"""
        if_token = self.expect(TokenType.IF)
        
        condition = self.parse_expression()
        self.skip_newlines()
        
        then_block = self.parse_block()
        
        node = ASTNode(
            NodeType.IF_STATEMENT,
            None,
            [condition, then_block],
            if_token.line,
            if_token.column
        )
        
        # ELSE блок (опціонально)
        self.skip_newlines()
        if self.consume(TokenType.ELSE):
            self.skip_newlines()
            else_block = self.parse_block()
            node.add_child(else_block)
        
        return node
    
    def parse_for_statement(self) -> ASTNode:
        """Парсити for інструкцію"""
        for_token = self.expect(TokenType.FOR)
        var_token = self.expect(TokenType.IDENTIFIER)
        
        node = ASTNode(
            NodeType.FOR_STATEMENT,
            var_token.value,
            line=for_token.line,
            column=for_token.column
        )
        
        self.expect(TokenType.FROM)
        start = self.parse_expression()
        node.add_child(start)
        
        self.expect(TokenType.TO)
        end = self.parse_expression()
        node.add_child(end)
        
        self.skip_newlines()
        body = self.parse_block()
        node.add_child(body)
        
        return node
    
    def parse_while_statement(self) -> ASTNode:
        """Парсити while інструкцію"""
        while_token = self.expect(TokenType.WHILE)
        
        condition = self.parse_expression()
        self.skip_newlines()
        
        body = self.parse_block()
        
        node = ASTNode(
            NodeType.WHILE_STATEMENT,
            None,
            [condition, body],
            while_token.line,
            while_token.column
        )
        
        return node
    
    def parse_foreach_statement(self) -> ASTNode:
        """Парсити foreach інструкцію"""
        foreach_token = self.expect(TokenType.FOREACH)
        var_token = self.expect(TokenType.IDENTIFIER)
        
        node = ASTNode(
            NodeType.FOREACH_STATEMENT,
            var_token.value,
            line=foreach_token.line,
            column=foreach_token.column
        )
        
        self.expect(TokenType.IN)
        collection = self.parse_expression()
        node.add_child(collection)
        
        self.skip_newlines()
        body = self.parse_block()
        node.add_child(body)
        
        return node
    
    def parse_expression_statement(self) -> ASTNode:
        """Парсити інструкцію-вираз"""
        expr = self.parse_expression()
        
        return ASTNode(
            NodeType.EXPRESSION_STATEMENT,
            None,
            [expr],
            expr.line,
            expr.column
        )
    
    def parse_expression(self) -> ASTNode:
        """Парсити вираз"""
        return self.parse_assignment()
    
    def parse_assignment(self) -> ASTNode:
        """Парсити присвоєння"""
        expr = self.parse_logical_or()
        
        if self.consume(TokenType.ASSIGN):
            value = self.parse_assignment()
            return ASTNode(
                NodeType.ASSIGNMENT,
                None,
                [expr, value],
                expr.line,
                expr.column
            )
        
        return expr
    
    def parse_logical_or(self) -> ASTNode:
        """Парсити логічне АБО"""
        left = self.parse_logical_and()
        
        while self.consume(TokenType.OR):
            op_token = self.tokens[self.current - 1]
            right = self.parse_logical_and()
            left = ASTNode(
                NodeType.BINARY_EXPRESSION,
                op_token.value,
                [left, right],
                op_token.line,
                op_token.column
            )
        
        return left
    
    def parse_logical_and(self) -> ASTNode:
        """Парсити логічне І"""
        left = self.parse_equality()
        
        while self.consume(TokenType.AND):
            op_token = self.tokens[self.current - 1]
            right = self.parse_equality()
            left = ASTNode(
                NodeType.BINARY_EXPRESSION,
                op_token.value,
                [left, right],
                op_token.line,
                op_token.column
            )
        
        return left
    
    def parse_equality(self) -> ASTNode:
        """Парсити порівняння"""
        left = self.parse_comparison()
        
        while self.consume(TokenType.EQUAL, TokenType.NOT_EQUAL):
            op_token = self.tokens[self.current - 1]
            right = self.parse_comparison()
            left = ASTNode(
                NodeType.BINARY_EXPRESSION,
                op_token.value,
                [left, right],
                op_token.line,
                op_token.column
            )
        
        return left
    
    def parse_comparison(self) -> ASTNode:
        """Парсити порівняння (<, >, <=, >=)"""
        left = self.parse_term()
        
        while self.consume(TokenType.LESS, TokenType.LESS_EQUAL, TokenType.GREATER, TokenType.GREATER_EQUAL):
            op_token = self.tokens[self.current - 1]
            right = self.parse_term()
            left = ASTNode(
                NodeType.BINARY_EXPRESSION,
                op_token.value,
                [left, right],
                op_token.line,
                op_token.column
            )
        
        return left
    
    def parse_term(self) -> ASTNode:
        """Парсити терм (+, -)"""
        left = self.parse_factor()
        
        while self.consume(TokenType.PLUS, TokenType.MINUS):
            op_token = self.tokens[self.current - 1]
            right = self.parse_factor()
            left = ASTNode(
                NodeType.BINARY_EXPRESSION,
                op_token.value,
                [left, right],
                op_token.line,
                op_token.column
            )
        
        return left
    
    def parse_factor(self) -> ASTNode:
        """Парсити фактор (*, /, %)"""
        left = self.parse_power()
        
        while self.consume(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            op_token = self.tokens[self.current - 1]
            right = self.parse_power()
            left = ASTNode(
                NodeType.BINARY_EXPRESSION,
                op_token.value,
                [left, right],
                op_token.line,
                op_token.column
            )
        
        return left
    
    def parse_power(self) -> ASTNode:
        """Парсити ступінь (^)"""
        left = self.parse_unary()
        
        if self.consume(TokenType.POWER):
            op_token = self.tokens[self.current - 1]
            right = self.parse_power()  # право-асоціативний
            left = ASTNode(
                NodeType.BINARY_EXPRESSION,
                op_token.value,
                [left, right],
                op_token.line,
                op_token.column
            )
        
        return left
    
    def parse_unary(self) -> ASTNode:
        """Парсити унарний вираз"""
        if self.consume(TokenType.NOT, TokenType.MINUS):
            op_token = self.tokens[self.current - 1]
            operand = self.parse_unary()
            return ASTNode(
                NodeType.UNARY_EXPRESSION,
                op_token.value,
                [operand],
                op_token.line,
                op_token.column
            )
        
        return self.parse_call()
    
    def parse_call(self) -> ASTNode:
        """Парсити виклик функції"""
        expr = self.parse_primary()
        
        while True:
            if self.consume(TokenType.LEFT_PAREN):
                # Виклик функції
                args = []
                while not self.consume(TokenType.RIGHT_PAREN):
                    if self.current_token.type == TokenType.EOF:
                        raise ParserError("Unclosed function call", self.current_token)
                    
                    arg = self.parse_expression()
                    args.append(arg)
                    
                    self.consume(TokenType.COMMA)
                    self.skip_newlines()
                
                expr = ASTNode(
                    NodeType.CALL_EXPRESSION,
                    None,
                    [expr] + args,
                    expr.line,
                    expr.column
                )
            elif self.consume(TokenType.LEFT_BRACKET):
                # Доступ до елемента масиву
                index = self.parse_expression()
                self.expect(TokenType.RIGHT_BRACKET)
                
                expr = ASTNode(
                    NodeType.MEMBER_EXPRESSION,
                    "[]",
                    [expr, index],
                    expr.line,
                    expr.column
                )
            elif self.consume(TokenType.DOT):
                # Доступ до поля об'єкта
                member_token = self.expect(TokenType.IDENTIFIER)
                member = ASTNode(
                    NodeType.IDENTIFIER,
                    member_token.value,
                    line=member_token.line,
                    column=member_token.column
                )
                
                expr = ASTNode(
                    NodeType.MEMBER_EXPRESSION,
                    ".",
                    [expr, member],
                    expr.line,
                    expr.column
                )
            else:
                break
        
        return expr
    
    def parse_primary(self) -> ASTNode:
        """Парсити первинний вираз"""
        if self.consume(TokenType.NUMBER):
            token = self.tokens[self.current - 1]
            return ASTNode(
                NodeType.LITERAL,
                token.value,
                line=token.line,
                column=token.column
            )
        elif self.consume(TokenType.STRING):
            token = self.tokens[self.current - 1]
            return ASTNode(
                NodeType.LITERAL,
                token.value,
                line=token.line,
                column=token.column
            )
        elif self.consume(TokenType.BOOLEAN):
            token = self.tokens[self.current - 1]
            return ASTNode(
                NodeType.LITERAL,
                token.value == "true",
                line=token.line,
                column=token.column
            )
        elif self.consume(TokenType.LEFT_BRACKET):
            # Масив
            elements = []
            while not self.consume(TokenType.RIGHT_BRACKET):
                if self.current_token.type == TokenType.EOF:
                    raise ParserError("Unclosed array", self.current_token)
                
                element = self.parse_expression()
                elements.append(element)
                
                self.consume(TokenType.COMMA)
                self.skip_newlines()
            
            return ASTNode(
                NodeType.ARRAY_LITERAL,
                None,
                elements,
                self.tokens[self.current - 1].line,
                self.tokens[self.current - 1].column
            )
        elif self.consume(TokenType.LEFT_BRACE):
            # Об'єкт
            properties = []
            while not self.consume(TokenType.RIGHT_BRACE):
                if self.current_token.type == TokenType.EOF:
                    raise ParserError("Unclosed object", self.current_token)
                
                key = self.expect(TokenType.IDENTIFIER)
                self.expect(TokenType.COLON)
                value = self.parse_expression()
                
                prop = ASTNode(
                    NodeType.PROPERTY,
                    key.value,
                    [value],
                    key.line,
                    key.column
                )
                properties.append(prop)
                
                self.consume(TokenType.COMMA)
                self.skip_newlines()
            
            return ASTNode(
                NodeType.OBJECT_LITERAL,
                None,
                properties,
                self.tokens[self.current - 1].line,
                self.tokens[self.current - 1].column
            )
        elif self.consume(TokenType.LEFT_PAREN):
            # Дужки для групування
            expr = self.parse_expression()
            self.expect(TokenType.RIGHT_PAREN)
            return expr
        elif self.consume(TokenType.IDENTIFIER):
            token = self.tokens[self.current - 1]
            return ASTNode(
                NodeType.IDENTIFIER,
                token.value,
                line=token.line,
                column=token.column
            )
        else:
            raise ParserError(f"Unexpected token: {self.current_token}", self.current_token)
    
    def print_ast(self, node: ASTNode, indent: int = 0):
        """Друкувати AST для відладки"""
        print("  " * indent + str(node))
        for child in node.children:
            self.print_ast(child, indent + 1)


# Тестування
if __name__ == "__main__":
    # Простий тест
    test_code = """
    energy: 1.5
    particles: 1000
    
    FUNCTION test_func(x) -> float {
        return x * 2
    }
    
    result = test_func(5)
    log("Result: " + result)
    """
    
    print("=== LCARS Script Parser Test ===")
    
    # Токенізація
    lexer = Lexer(test_code)
    tokens = lexer.tokenize()
    
    print(f"Tokens: {len(tokens)}")
    
    # Парсинг
    parser = Parser(tokens)
    if True:
        ast = parser.parse()
        
        print("\nAST:")
        parser.print_ast(ast)
        
    if False: # Removed except block
        print(f"Parser error: {e}")
