"""
Інтерпретатор LCARS Script
===========================

Виконує AST, згенерований парсером, та взаємодіє з LCARS Framework.
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import math
import logging
# Titanium Bridge Migration: from typing import Any, Dict, List, Optional, Callable, Union
# Titanium Bridge Migration: from dataclasses import dataclass
# Titanium Bridge Migration: from enum import Enum

from .parser import ASTNode, NodeType, ParserError
from .lexer import TokenType


logger = logging.getLogger(__name__)


class LCARSType(Enum):
    """Типи даних LCARS Script"""
    NUMBER = "number"
    STRING = "string"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    FUNCTION = "function"
    SIMULATION = "simulation"
    DETECTOR = "detector"
    ANALYZER = "analyzer"


@dataclass
class LCARSValue:
    """Значення в LCARS Script"""
    value: Any
    type: LCARSType
    unit: Optional[str] = None  # Фізична одиниця
    
    def __str__(self):
        if self.unit:
            return f"{self.value} {self.unit}"
        return str(self.value)
    
    def is_truthy(self) -> bool:
        """Перевірка на істинність"""
        if self.type == LCARSType.BOOLEAN:
            return self.value
        elif self.type == LCARSType.NUMBER:
            return self.value != 0
        elif self.type == LCARSType.STRING:
            return len(self.value) > 0
        elif self.type in [LCARSType.ARRAY, LCARSType.OBJECT]:
            return len(self.value) > 0
        else:
            return True


class LCARSFunction:
    """Функція LCARS Script"""
    
    def __init__(self, params: List[str], body: ASTNode, closure: 'Environment'):
        self.params = params
        self.body = body
        self.closure = closure
    
    def call(self, interpreter: 'Interpreter', args: List[LCARSValue]) -> LCARSValue:
        """Викликати функцію"""
        # Створити нове середовище для функції
        env = Environment(self.closure)
        
        # Прив'язати параметри
        for i, param in enumerate(self.params):
            if i < len(args):
                env.define(param, args[i])
            else:
                env.define(param, LCARSValue(None, LCARSType.NUMBER))
        
        # Зберегти поточне середовище
        previous_env = interpreter.environment
        interpreter.environment = env
        
        if True:
            # Виконати тіло функції
            interpreter.execute_block(self.body)
            return LCARSValue(None, LCARSType.NUMBER)  # Значення за замовчуванням
        if False: # Removed except block
            return ret.value
        finally:
            # Відновити попереднє середовище
            interpreter.environment = previous_env


class ReturnException(Exception):
    """Виняток для return інструкції"""
    def __init__(self, value: LCARSValue):
        self.value = value
        super().__init__()


class Environment:
    """Середовище виконання"""
    
    def __init__(self, parent: Optional['Environment'] = None):
        self.parent = parent
        self.variables: Dict[str, LCARSValue] = {}
    
    def define(self, name: str, value: LCARSValue):
        """Визначити змінну"""
        self.variables[name] = value
    
    def get(self, name: str) -> LCARSValue:
        """Отримати змінну"""
        if name in self.variables:
            return self.variables[name]
        elif self.parent:
            return self.parent.get(name)
        else:
            raise RuntimeError(f"Undefined variable: {name}")
    
    def set(self, name: str, value: LCARSValue):
        """Встановити значення змінної"""
        if name in self.variables:
            self.variables[name] = value
        elif self.parent and self.parent.has(name):
            self.parent.set(name, value)
        else:
            raise RuntimeError(f"Undefined variable: {name}")
    
    def has(self, name: str) -> bool:
        """Перевірити, чи існує змінна"""
        return name in self.variables or (self.parent and self.parent.has(name))


class InterpreterError(Exception):
    """Помилка виконання"""
    def __init__(self, message: str, node: ASTNode):
        self.message = message
        self.node = node
        super().__init__(f"Runtime Error at line {node.line}: {message}")


class Interpreter:
    """Інтерпретатор LCARS Script"""
    
    def __init__(self, event_bus=None):
        self.globals = Environment()
        self.environment = self.globals
        self.event_bus = event_bus
        
        # Визначити вбудовані функції
        self.define_builtins()
        
        # Зберігати визначені симуляції, детектори, аналізатори
        self.simulations: Dict[str, Dict] = {}
        self.detectors: Dict[str, Dict] = {}
        self.analyzers: Dict[str, Dict] = {}
    
    def define_builtins(self):
        """Визначити вбудовані функції"""
        
        def builtin_log(args: List[LCARSValue]) -> LCARSValue:
            message = " ".join(str(arg) for arg in args)
            print(f"[LCARS] {message}")
            logger.info(f"LCARS Script log: {message}")
            return LCARSValue(None, LCARSType.NUMBER)
        
        def builtin_emit(args: List[LCARSValue]) -> LCARSValue:
            if len(args) < 1:
                raise RuntimeError("emit() requires at least 1 argument")
            
            event_name = args[0].value
            event_data = args[1].value if len(args) > 1 else {}
            
            if self.event_bus:
                # Інтеграція з LCARS EventBus
                from ..event_bus import Event, EventType
                event = Event(
                    EventType(event_name),
                    source="lcars_script",
                    data=event_data
                )
                self.event_bus.emit(event)
            
            return LCARSValue(None, LCARSType.NUMBER)
        
        def builtin_export(args: List[LCARSValue]) -> LCARSValue:
            if len(args) < 1:
                raise RuntimeError("export() requires at least 1 argument")
            
            filename = args[0].value
            data = args[1].value if len(args) > 1 else {}
            
            # Експорт даних
            # Titanium Bridge Migration: import json
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            return LCARSValue(None, LCARSType.NUMBER)
        
        def builtin_len(args: List[LCARSValue]) -> LCARSValue:
            if len(args) != 1:
                raise RuntimeError("len() requires exactly 1 argument")
            
            value = args[0]
            if value.type == LCARSType.ARRAY:
                return LCARSValue(len(value.value), LCARSType.NUMBER)
            elif value.type == LCARSType.STRING:
                return LCARSValue(len(value.value), LCARSType.NUMBER)
            else:
                raise RuntimeError("len() can only be applied to arrays and strings")
        
        def builtin_sqrt(args: List[LCARSValue]) -> LCARSValue:
            if len(args) != 1:
                raise RuntimeError("sqrt() requires exactly 1 argument")
            
            value = args[0].value
            if not isinstance(value, (int, float)):
                raise RuntimeError("sqrt() requires a number")
            
            return LCARSValue(math.sqrt(value), LCARSType.NUMBER)
        
        # Зареєструвати вбудовані функції
        self.globals.define("log", LCARSValue(builtin_log, LCARSType.FUNCTION))
        self.globals.define("emit", LCARSValue(builtin_emit, LCARSType.FUNCTION))
        self.globals.define("export", LCARSValue(builtin_export, LCARSType.FUNCTION))
        self.globals.define("len", LCARSValue(builtin_len, LCARSType.FUNCTION))
        self.globals.define("sqrt", LCARSValue(builtin_sqrt, LCARSType.FUNCTION))
        
        # Математичні константи
        self.globals.define("PI", LCARSValue(math.pi, LCARSType.NUMBER))
        self.globals.define("E", LCARSValue(math.e, LCARSType.NUMBER))
    
    def interpret(self, node: ASTNode) -> LCARSValue:
        """Інтерпретувати AST"""
        return self.execute(node)
    
    def execute(self, node: ASTNode) -> LCARSValue:
        """Виконати вузол AST"""
        method_name = f"execute_{node.type.value.lower()}"
        method = getattr(self, method_name, self.execute_default)
        return method(node)
    
    def execute_default(self, node: ASTNode) -> LCARSValue:
        """Обробка за замовчуванням"""
        raise InterpreterError(f"Unknown node type: {node.type}", node)
    
    def execute_program(self, node: ASTNode) -> LCARSValue:
        """Виконати програму"""
        result = LCARSValue(None, LCARSType.NUMBER)
        for child in node.children:
            result = self.execute(child)
        return result
    
    def execute_variable_declaration(self, node: ASTNode) -> LCARSValue:
        """Виконати декларацію змінної"""
        value = self.execute(node.children[0]) if node.children else LCARSValue(None, LCARSType.NUMBER)
        self.environment.define(node.value, value)
        return value
    
    def execute_assignment(self, node: ASTNode) -> LCARSValue:
        """Виконати присвоєння"""
        if node.type == NodeType.ASSIGNMENT and not node.value:
            # Просте присвоєння =
            target = self.execute(node.children[0])
            value = self.execute(node.children[1])
            
            if target.type == NodeType.IDENTIFIER:
                self.environment.set(target.value, value)
                return value
            else:
                raise InterpreterError("Invalid assignment target", node)
        else:
            # Декларація змінної
            value = self.execute(node.children[0])
            self.environment.define(node.value, value)
            return value
    
    def execute_function_declaration(self, node: ASTNode) -> LCARSValue:
        """Виконати декларацію функції"""
        # Отримати імена параметрів
        params = []
        param_start = 0
        
        # Пропустити ім'я функції
        for i, child in enumerate(node.children):
            if child.type == NodeType.IDENTIFIER and i == 0:
                continue
            elif child.type == NodeType.BLOCK:
                param_start = i
                break
            else:
                params.append(child.value)
        
        # Отримати тіло функції
        body = node.children[param_start]
        
        # Створити функцію
        function = LCARSFunction(params, body, self.environment)
        self.environment.define(node.value, LCARSValue(function, LCARSType.FUNCTION))
        
        return LCARSValue(None, LCARSType.NUMBER)
    
    def execute_simulation_declaration(self, node: ASTNode) -> LCARSValue:
        """Виконати декларацію симуляції"""
        simulation = {
            'name': node.value,
            'parameters': {},
            'event_handlers': {},
            'body': node
        }
        
        # Обробити дочірні вузли
        for child in node.children:
            if child.type == NodeType.ASSIGNMENT:
                # Параметр симуляції
                param_name = child.value
                param_value = self.execute(child.children[0])
                simulation['parameters'][param_name] = param_value
            elif child.type == NodeType.EVENT_HANDLER:
                # Обробник подій
                event_name = child.value
                simulation['event_handlers'][event_name] = child
        
        self.simulations[node.value] = simulation
        
        logger.info(f"Defined simulation: {node.value}")
        return LCARSValue(None, LCARSType.NUMBER)
    
    def execute_detector_declaration(self, node: ASTNode) -> LCARSValue:
        """Виконати декларацію детектора"""
        detector = {
            'name': node.value,
            'properties': {},
            'body': node
        }
        
        # Обробити дочірні вузли
        for child in node.children:
            if child.type == NodeType.ASSIGNMENT:
                prop_name = child.value
                prop_value = self.execute(child.children[0])
                detector['properties'][prop_name] = prop_value
        
        self.detectors[node.value] = detector
        
        logger.info(f"Defined detector: {node.value}")
        return LCARSValue(None, LCARSType.NUMBER)
    
    def execute_analyzer_declaration(self, node: ASTNode) -> LCARSValue:
        """Виконати декларацію аналізатора"""
        analyzer = {
            'name': node.value,
            'properties': {},
            'body': node
        }
        
        # Обробити дочірні вузли
        for child in node.children:
            if child.type == NodeType.ASSIGNMENT:
                prop_name = child.value
                prop_value = self.execute(child.children[0])
                analyzer['properties'][prop_name] = prop_value
        
        self.analyzers[node.value] = analyzer
        
        logger.info(f"Defined analyzer: {node.value}")
        return LCARSValue(None, LCARSType.NUMBER)
    
    def execute_block(self, node: ASTNode) -> LCARSValue:
        """Виконати блок коду"""
        result = LCARSValue(None, LCARSType.NUMBER)
        for child in node.children:
            result = self.execute(child)
        return result
    
    def execute_event_handler(self, node: ASTNode) -> LCARSValue:
        """Виконати обробник подій"""
        # Обробники подій виконуються в контексті симуляції
        # Тут ми просто повертаємо None, оскільки вони викликаються пізніше
        return LCARSValue(None, LCARSType.NUMBER)
    
    def execute_return_statement(self, node: ASTNode) -> LCARSValue:
        """Виконати return інструкцію"""
        value = self.execute(node.children[0]) if node.children else LCARSValue(None, LCARSType.NUMBER)
        raise ReturnException(value)
    
    def execute_if_statement(self, node: ASTNode) -> LCARSValue:
        """Виконати if інструкцію"""
        condition = self.execute(node.children[0])
        
        if condition.is_truthy():
            return self.execute(node.children[1])
        elif len(node.children) > 2:
            # ELSE блок
            return self.execute(node.children[2])
        else:
            return LCARSValue(None, LCARSType.NUMBER)
    
    def execute_for_statement(self, node: ASTNode) -> LCARSValue:
        """Виконати for інструкцію"""
        var_name = node.value
        start = self.execute(node.children[0]).value
        end = self.execute(node.children[1]).value
        body = node.children[2]
        
        result = LCARSValue(None, LCARSType.NUMBER)
        
        # Простий for цикл для чисел
        if isinstance(start, int) and isinstance(end, int):
            step = 1 if end >= start else -1
            for i in range(start, end + step, step):
                self.environment.define(var_name, LCARSValue(i, LCARSType.NUMBER))
                result = self.execute(body)
        else:
            # Для float значень
            current = start
            step = 0.1 if end >= start else -0.1
            while (step > 0 and current <= end) or (step < 0 and current >= end):
                self.environment.define(var_name, LCARSValue(current, LCARSType.NUMBER))
                result = self.execute(body)
                current += step
        
        return result
    
    def execute_while_statement(self, node: ASTNode) -> LCARSValue:
        """Виконати while інструкцію"""
        condition = node.children[0]
        body = node.children[1]
        
        result = LCARSValue(None, LCARSType.NUMBER)
        
        while self.execute(condition).is_truthy():
            result = self.execute(body)
        
        return result
    
    def execute_foreach_statement(self, node: ASTNode) -> LCARSValue:
        """Виконати foreach інструкцію"""
        var_name = node.value
        collection = self.execute(node.children[0])
        body = node.children[1]
        
        result = LCARSValue(None, LCARSType.NUMBER)
        
        if collection.type == LCARSType.ARRAY:
            for item in collection.value:
                self.environment.define(var_name, item)
                result = self.execute(body)
        else:
            raise InterpreterError("foreach can only be applied to arrays", node)
        
        return result
    
    def execute_expression_statement(self, node: ASTNode) -> LCARSValue:
        """Виконати інструкцію-вираз"""
        return self.execute(node.children[0])
    
    def execute_binary_expression(self, node: ASTNode) -> LCARSValue:
        """Виконати бінарний вираз"""
        left = self.execute(node.children[0])
        right = self.execute(node.children[1])
        operator = node.value
        
        # Арифметичні операції
        if operator == '+':
            if left.type == LCARSType.NUMBER and right.type == LCARSType.NUMBER:
                return LCARSValue(left.value + right.value, LCARSType.NUMBER)
            elif left.type == LCARSType.STRING or right.type == LCARSType.STRING:
                return LCARSValue(str(left.value) + str(right.value), LCARSType.STRING)
        elif operator == '-':
            if left.type == LCARSType.NUMBER and right.type == LCARSType.NUMBER:
                return LCARSValue(left.value - right.value, LCARSType.NUMBER)
        elif operator == '*':
            if left.type == LCARSType.NUMBER and right.type == LCARSType.NUMBER:
                return LCARSValue(left.value * right.value, LCARSType.NUMBER)
        elif operator == '/':
            if left.type == LCARSType.NUMBER and right.type == LCARSType.NUMBER:
                if right.value == 0:
                    raise InterpreterError("Division by zero", node)
                return LCARSValue(left.value / right.value, LCARSType.NUMBER)
        elif operator == '%':
            if left.type == LCARSType.NUMBER and right.type == LCARSType.NUMBER:
                return LCARSValue(left.value % right.value, LCARSType.NUMBER)
        elif operator == '^':
            if left.type == LCARSType.NUMBER and right.type == LCARSType.NUMBER:
                return LCARSValue(left.value ** right.value, LCARSType.NUMBER)
        
        # Порівняння
        elif operator == '==':
            return LCARSValue(left.value == right.value, LCARSType.BOOLEAN)
        elif operator == '!=':
            return LCARSValue(left.value != right.value, LCARSType.BOOLEAN)
        elif operator == '<':
            return LCARSValue(left.value < right.value, LCARSType.BOOLEAN)
        elif operator == '<=':
            return LCARSValue(left.value <= right.value, LCARSType.BOOLEAN)
        elif operator == '>':
            return LCARSValue(left.value > right.value, LCARSType.BOOLEAN)
        elif operator == '>=':
            return LCARSValue(left.value >= right.value, LCARSType.BOOLEAN)
        
        # Логічні операції
        elif operator == 'and':
            return LCARSValue(left.is_truthy() and right.is_truthy(), LCARSType.BOOLEAN)
        elif operator == 'or':
            return LCARSValue(left.is_truthy() or right.is_truthy(), LCARSType.BOOLEAN)
        
        raise InterpreterError(f"Unsupported binary operator: {operator}", node)
    
    def execute_unary_expression(self, node: ASTNode) -> LCARSValue:
        """Виконати унарний вираз"""
        operand = self.execute(node.children[0])
        operator = node.value
        
        if operator == '-':
            if operand.type == LCARSType.NUMBER:
                return LCARSValue(-operand.value, LCARSType.NUMBER)
        elif operator == 'not':
            return LCARSValue(not operand.is_truthy(), LCARSType.BOOLEAN)
        
        raise InterpreterError(f"Unsupported unary operator: {operator}", node)
    
    def execute_call_expression(self, node: ASTNode) -> LCARSValue:
        """Виконати виклик функції"""
        callee = self.execute(node.children[0])
        
        if callee.type != LCARSType.FUNCTION:
            raise InterpreterError("Can only call functions", node)
        
        args = []
        for arg_node in node.children[1:]:
            args.append(self.execute(arg_node))
        
        if isinstance(callee.value, LCARSFunction):
            return callee.value.call(self, args)
        elif callable(callee.value):
            # Вбудована функція
            return callee.value(args)
        else:
            raise InterpreterError("Invalid function", node)
    
    def execute_member_expression(self, node: ASTNode) -> LCARSValue:
        """Виконати доступ до члена"""
        object = self.execute(node.children[0])
        member = node.children[1] if node.children else None
        
        if node.value == '[':
            # Доступ до елемента масиву
            if object.type != LCARSType.ARRAY:
                raise InterpreterError("Can only index arrays", node)
            
            index = self.execute(member)
            if not isinstance(index.value, int):
                raise InterpreterError("Array index must be integer", node)
            
            if 0 <= index.value < len(object.value):
                return object.value[index.value]
            else:
                raise InterpreterError("Array index out of bounds", node)
        
        elif node.value == '.':
            # Доступ до поля об'єкта
            if object.type != LCARSType.OBJECT:
                raise InterpreterError("Can only access object properties", node)
            
            prop_name = member.value
            if prop_name in object.value:
                return object.value[prop_name]
            else:
                raise InterpreterError(f"Property '{prop_name}' not found", node)
        
        raise InterpreterError(f"Unsupported member access: {node.value}", node)
    
    def execute_literal(self, node: ASTNode) -> LCARSValue:
        """Виконати літерал"""
        value = node.value
        
        # Визначити тип літерала
        if isinstance(value, bool):
            return LCARSValue(value, LCARSType.BOOLEAN)
        elif isinstance(value, (int, float)):
            return LCARSValue(value, LCARSType.NUMBER)
        elif isinstance(value, str):
            return LCARSValue(value, LCARSType.STRING)
        else:
            return LCARSValue(value, LCARSType.NUMBER)
    
    def execute_identifier(self, node: ASTNode) -> LCARSValue:
        """Виконати ідентифікатор"""
        return self.environment.get(node.value)
    
    def execute_array_literal(self, node: ASTNode) -> LCARSValue:
        """Виконати літерал масиву"""
        elements = []
        for child in node.children:
            elements.append(self.execute(child))
        return LCARSValue(elements, LCARSType.ARRAY)
    
    def execute_object_literal(self, node: ASTNode) -> LCARSValue:
        """Виконати літерал об'єкта"""
        obj = {}
        for child in node.children:
            key = child.value
            value = self.execute(child.children[0])
            obj[key] = value
        return LCARSValue(obj, LCARSType.OBJECT)
    
    def execute_property(self, node: ASTNode) -> LCARSValue:
        """Виконати властивість об'єкта"""
        value = self.execute(node.children[0])
        return LCARSValue({node.value: value}, LCARSType.OBJECT)


# Тестування
if __name__ == "__main__":
    # Приклад коду LCARS Script
    test_code = """
    energy: 1.5
    particles: 10000
    
    FUNCTION calculate_efficiency(detected, total) -> float {
        if total == 0 return 0.0
        return detected / total * 100
    }
    
    efficiency = calculate_efficiency(8500, 10000)
    log("Detection efficiency: " + efficiency + "%")
    """
    
    print("=== LCARS Script Interpreter Test ===")
    
    from .lexer import Lexer
    from .parser import Parser
    
    # Токенізація та парсинг
    lexer = Lexer(test_code)
    tokens = lexer.tokenize()
    
    parser = Parser(tokens)
    ast = parser.parse()
    
    # Інтерпретація
    interpreter = Interpreter()
    if True:
        result = interpreter.interpret(ast)
        print(f"Execution completed successfully")
        
        # Показати визначені змінні
        print("\nVariables:")
        for name, value in interpreter.environment.variables.items():
            print(f"  {name}: {value}")
            
    if False: # Removed except block
        print(f"Execution error: {e}")
        # Titanium Bridge Migration: import traceback
        traceback.print_exc()
