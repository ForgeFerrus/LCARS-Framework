"""
Компілятор LCARS Script в Python
=================================

Компілює AST LCARS Script в виконуваний Python код для інтеграції з LCARS Framework.
"""

# Titanium Bridge Migration: import os
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from typing import List, Dict, Any, Optional
# Titanium Bridge Migration: from dataclasses import dataclass

from .parser import ASTNode, NodeType, ParserError
from .lexer import TokenType


class CompilerError(Exception):
    """Помилка компіляції"""
    def __init__(self, message: str, node: ASTNode):
        self.message = message
        self.node = node
        super().__init__(f"Compiler Error at line {node.line}: {message}")


class PythonCompiler:
    """Компілятор LCARS Script в Python"""
    
    def __init__(self):
        self.indent_level = 0
        self.output_lines: List[str] = []
        self.imports: set = set()
        self.functions: Dict[str, Dict] = {}
        self.simulations: Dict[str, Dict] = {}
        self.detectors: Dict[str, Dict] = {}
        self.analyzers: Dict[str, Dict] = {}
        
        # Генерувати унікальні імена для змінних
        self.var_counter = 0
        self.temp_vars: Dict[str, str] = {}
    
    def compile(self, node: ASTNode) -> str:
        """Скомпілювати AST в Python код"""
        self.output_lines.clear()
        self.imports.clear()
        self.indent_level = 0
        
        # Додати заголовок
        self.add_header()
        
        # Компілювати програму
        self.compile_node(node)
        
        # Додати фінальний код
        self.add_footer()
        
        return '\n'.join(self.output_lines)
    
    def add_header(self):
        """Додати заголовок Python файлу"""
        self.output_lines.extend([
            '"""',
            'Згенерований код з LCARS Script',
            '================================',
            '',
            'Цей файл був автоматично згенерований компілятором LCARS Script.',
            'Не редагуйте вручну - зміни будуть втрачені при перекомпіляції.',
            '"""',
            '',
            'import sys',
            'import os',
            'import json',
            'import logging',
            'import math',
            'from typing import Dict, List, Any, Optional, Union',
            'from dataclasses import dataclass',
            '',
            '# Імпорти LCARS Framework',
            'try:',
            '    from lcars.core.event_bus import event_bus, Event, EventType',
            '    from lcars.core.plugin_system import PluginManager',
            'except ImportError:',
            '    print("Warning: LCARS Framework not available")',
            '    event_bus = None',
            '',
            'logger = logging.getLogger(__name__)',
            '',
        ])
    
    def add_footer(self):
        """Додати фінальний код"""
        self.output_lines.extend([
            '',
            'if __name__ == "__main__":',
            '    print("LCARS Script compiled successfully!")',
            '    main()',
        ])
    
    def write_line(self, line: str = ""):
        """Записати рядок з відступом"""
        if line:
            indent = '    ' * self.indent_level
            self.output_lines.append(f"{indent}{line}")
        else:
            self.output_lines.append("")
    
    def write_lines(self, lines: List[str]):
        """Записати кілька рядків"""
        for line in lines:
            self.write_line(line)
    
    def indent(self):
        """Збільшити відступ"""
        self.indent_level += 1
    
    def dedent(self):
        """Зменшити відступ"""
        self.indent_level = max(0, self.indent_level - 1)
    
    def get_temp_var(self, prefix: str = "temp") -> str:
        """Отримати тимчасове ім'я змінної"""
        self.var_counter += 1
        return f"{prefix}_{self.var_counter}"
    
    def compile_node(self, node: ASTNode) -> str:
        """Скомпілювати вузол AST"""
        method_name = f"compile_{node.type.value.lower()}"
        method = getattr(self, method_name, self.compile_default)
        return method(node)
    
    def compile_default(self, node: ASTNode) -> str:
        """Компіляція за замовчуванням"""
        raise CompilerError(f"Unknown node type: {node.type}", node)
    
    def compile_program(self, node: ASTNode) -> str:
        """Скомпілювати програму"""
        self.write_line("# Головна функція")
        self.write_line("def main():")
        self.indent()
        
        # Ініціалізація середовища
        self.write_line('print("Starting LCARS Script execution...")')
        self.write_line("")
        
        # Компілювати всі дочірні вузли
        for child in node.children:
            self.compile_node(child)
            self.write_line("")
        
        self.write_line('print("LCARS Script execution completed.")')
        self.dedent()
        
        return ""
    
    def compile_variable_declaration(self, node: ASTNode) -> str:
        """Скомпілювати декларацію змінної"""
        var_name = node.value
        value_expr = self.compile_node(node.children[0]) if node.children else "None"
        
        # Перетворення фізичних одиниць
        if isinstance(value_expr, str) and any(unit in value_expr for unit in ['GeV', 'MeV', 'eV', 'TeV']):
            # Спеціальна обробка фізичних одиниць
            self.write_line(f"# Змінна з фізичною одиницею: {var_name}")
            self.write_line(f"{var_name} = {self.convert_units(value_expr)}")
        else:
            self.write_line(f"{var_name} = {value_expr}")
        
        return var_name
    
    def convert_units(self, value_with_units: str) -> str:
        """Перетворити фізичні одиниці в числові значення"""
        unit_conversions = {
            'GeV': 1e9,
            'MeV': 1e6,
            'keV': 1e3,
            'eV': 1.0,
            'TeV': 1e12,
            'm': 1.0,
            'cm': 0.01,
            'mm': 0.001,
            'μm': 1e-6,
            'nm': 1e-9,
            'T': 1.0,
            'G': 1e-4,
        }
        
        for unit, multiplier in unit_conversions.items():
            if value_with_units.endswith(unit):
                numeric_part = value_with_units[:-len(unit)].strip()
                if True:
                    value = float(numeric_part)
                    return str(value * multiplier)
                if False: # Removed except block
                    break
        
        # Якщо не вдалося розпарсити, повернути як є
        return value_with_units
    
    def compile_function_declaration(self, node: ASTNode) -> str:
        """Скомпілювати декларацію функції"""
        func_name = node.value
        
        # Отримати параметри
        params = []
        param_start = 0
        
        for i, child in enumerate(node.children):
            if child.type == NodeType.BLOCK:
                param_start = i
                break
            elif child.type == NodeType.IDENTIFIER:
                params.append(child.value)
        
        # Декларація функції
        param_str = ', '.join(params)
        self.write_line(f"def {func_name}({param_str}):")
        self.indent()
        
        # Тіло функції
        body = node.children[param_start]
        self.compile_node(body)
        
        # Додати return None, якщо немає явного return
        if not self.has_return_statement(body):
            self.write_line("return None")
        
        self.dedent()
        
        # Зберегти інформацію про функцію
        self.functions[func_name] = {
            'params': params,
            'line': node.line
        }
        
        return func_name
    
    def has_return_statement(self, node: ASTNode) -> bool:
        """Перевірити, чи блок має return інструкцію"""
        if node.type == NodeType.RETURN_STATEMENT:
            return True
        elif hasattr(node, 'children'):
            for child in node.children:
                if self.has_return_statement(child):
                    return True
        return False
    
    def compile_simulation_declaration(self, node: ASTNode) -> str:
        """Скомпілювати декларацію симуляції"""
        sim_name = node.value
        
        self.write_line(f"# Симуляція: {sim_name}")
        self.write_line(f"class {sim_name}_Simulation:")
        self.indent()
        self.write_line(f'def __init__(self):')
        self.indent()
        
        # Параметри симуляції
        for child in node.children:
            if child.type == NodeType.ASSIGNMENT:
                param_name = child.value
                param_value = self.compile_node(child.children[0])
                self.write_line(f"self.{param_name} = {param_value}")
        
        self.write_line("self.event_handlers = {}")
        self.dedent()
        
        # Обробники подій
        for child in node.children:
            if child.type == NodeType.EVENT_HANDLER:
                self.compile_event_handler(child, sim_name)
        
        # Метод запуску симуляції
        self.write_line(f"def run(self):")
        self.indent()
        self.write_line('print(f"Starting simulation: {sim_name}")')
        
        # Викликати START обробник
        if 'START' in self.simulations.get(sim_name, {}).get('event_handlers', {}):
            self.write_line("self.event_handlers['START']()")
        
        self.write_line("# Тут буде логіка симуляції")
        self.write_line("# ...")
        
        # Викликати COMPLETE обробник
        if 'COMPLETE' in self.simulations.get(sim_name, {}).get('event_handlers', {}):
            self.write_line("self.event_handlers['COMPLETE']()")
        
        self.dedent()
        self.dedent()
        
        # Створити екземпляр симуляції
        self.write_line(f"{sim_name.lower()}_sim = {sim_name}_Simulation()")
        
        # Зберегти інформацію про симуляцію
        self.simulations[sim_name] = {
            'parameters': {},
            'event_handlers': {},
            'line': node.line
        }
        
        return sim_name
    
    def compile_event_handler(self, node: ASTNode, sim_name: str):
        """Скомпілювати обробник подій"""
        event_name = node.value
        
        self.write_line(f"def handle_{event_name.lower()}(self):")
        self.indent()
        self.write_line(f'print(f"Event: {event_name} in {sim_name}")')
        
        # Тіло обробника
        if node.children:
            body = node.children[-1]  # Останній дочірній вузол - це тіло
            self.compile_node(body)
        
        self.dedent()
        
        # Зареєструвати обробник
        self.write_line(f"self.event_handlers['{event_name}'] = self.handle_{event_name.lower()}")
    
    def compile_detector_declaration(self, node: ASTNode) -> str:
        """Скомпілювати декларацію детектора"""
        detector_name = node.value
        
        self.write_line(f"# Детектор: {detector_name}")
        self.write_line(f"class {detector_name}_Detector:")
        self.indent()
        self.write_line(f'def __init__(self):')
        self.indent()
        
        # Властивості детектора
        for child in node.children:
            if child.type == NodeType.ASSIGNMENT:
                prop_name = child.value
                prop_value = self.compile_node(child.children[0])
                self.write_line(f"self.{prop_name} = {prop_value}")
        
        self.dedent()
        self.dedent()
        
        # Створити екземпляр детектора
        self.write_line(f"{detector_name.lower()}_detector = {detector_name}_Detector()")
        
        # Зберегти інформацію про детектор
        self.detectors[detector_name] = {
            'properties': {},
            'line': node.line
        }
        
        return detector_name
    
    def compile_analyzer_declaration(self, node: ASTNode) -> str:
        """Скомпілювати декларацію аналізатора"""
        analyzer_name = node.value
        
        self.write_line(f"# Аналізатор: {analyzer_name}")
        self.write_line(f"class {analyzer_name}_Analyzer:")
        self.indent()
        self.write_line(f'def __init__(self):')
        self.indent()
        
        # Властивості аналізатора
        for child in node.children:
            if child.type == NodeType.ASSIGNMENT:
                prop_name = child.value
                prop_value = self.compile_node(child.children[0])
                self.write_line(f"self.{prop_name} = {prop_value}")
        
        self.dedent()
        
        # Метод аналізу
        self.write_line("def analyze(self, data):")
        self.indent()
        self.write_line(f'print(f"Analyzing data with {analyzer_name}")')
        self.write_line("# Тут буде логіка аналізу")
        self.write_line("results = {}")
        self.write_line("return results")
        self.dedent()
        
        self.dedent()
        
        # Створити екземпляр аналізатора
        self.write_line(f"{analyzer_name.lower()}_analyzer = {analyzer_name}_Analyzer()")
        
        # Зберегти інформацію про аналізатор
        self.analyzers[analyzer_name] = {
            'properties': {},
            'line': node.line
        }
        
        return analyzer_name
    
    def compile_block(self, node: ASTNode) -> str:
        """Скомпілювати блок коду"""
        for child in node.children:
            self.compile_node(child)
        return ""
    
    def compile_return_statement(self, node: ASTNode) -> str:
        """Скомпілювати return інструкцію"""
        if node.children:
            value = self.compile_node(node.children[0])
            self.write_line(f"return {value}")
        else:
            self.write_line("return None")
        return ""
    
    def compile_if_statement(self, node: ASTNode) -> str:
        """Скомпілювати if інструкцію"""
        condition = self.compile_node(node.children[0])
        
        self.write_line(f"if {condition}:")
        self.indent()
        self.compile_node(node.children[1])
        self.dedent()
        
        # ELSE блок
        if len(node.children) > 2:
            self.write_line("else:")
            self.indent()
            self.compile_node(node.children[2])
            self.dedent()
        
        return ""
    
    def compile_for_statement(self, node: ASTNode) -> str:
        """Скомпілювати for інструкцію"""
        var_name = node.value
        start = self.compile_node(node.children[0])
        end = self.compile_node(node.children[1])
        body = node.children[2]
        
        self.write_line(f"for {var_name} in range({start}, {end} + 1):")
        self.indent()
        self.compile_node(body)
        self.dedent()
        
        return ""
    
    def compile_while_statement(self, node: ASTNode) -> str:
        """Скомпілювати while інструкцію"""
        condition = self.compile_node(node.children[0])
        body = node.children[1]
        
        self.write_line(f"while {condition}:")
        self.indent()
        self.compile_node(body)
        self.dedent()
        
        return ""
    
    def compile_foreach_statement(self, node: ASTNode) -> str:
        """Скомпілювати foreach інструкцію"""
        var_name = node.value
        collection = self.compile_node(node.children[0])
        body = node.children[1]
        
        self.write_line(f"for {var_name} in {collection}:")
        self.indent()
        self.compile_node(body)
        self.dedent()
        
        return ""
    
    def compile_expression_statement(self, node: ASTNode) -> str:
        """Скомпілювати інструкцію-вираз"""
        expr = self.compile_node(node.children[0])
        self.write_line(expr)
        return ""
    
    def compile_binary_expression(self, node: ASTNode) -> str:
        """Скомпілювати бінарний вираз"""
        left = self.compile_node(node.children[0])
        right = self.compile_node(node.children[1])
        operator = node.value
        
        # Перетворення операторів
        op_map = {
            'and': 'and',
            'or': 'or',
            '==': '==',
            '!=': '!=',
            '<': '<',
            '<=': '<=',
            '>': '>',
            '>=': '>=',
        }
        
        if operator in op_map:
            return f"({left} {op_map[operator]} {right})"
        else:
            return f"({left} {operator} {right})"
    
    def compile_unary_expression(self, node: ASTNode) -> str:
        """Скомпілювати унарний вираз"""
        operand = self.compile_node(node.children[0])
        operator = node.value
        
        if operator == 'not':
            return f"(not {operand})"
        elif operator == '-':
            return f"(-{operand})"
        else:
            return f"({operator}{operand})"
    
    def compile_call_expression(self, node: ASTNode) -> str:
        """Скомпілювати виклик функції"""
        callee = self.compile_node(node.children[0])
        
        args = []
        for arg_node in node.children[1:]:
            args.append(self.compile_node(arg_node))
        
        args_str = ', '.join(args)
        return f"{callee}({args_str})"
    
    def compile_member_expression(self, node: ASTNode) -> str:
        """Скомпілювати доступ до члена"""
        object = self.compile_node(node.children[0])
        
        if node.value == '[':
            # Доступ до елемента масиву
            index = self.compile_node(node.children[1])
            return f"{object}[{index}]"
        elif node.value == '.':
            # Доступ до поля об'єкта
            member = node.children[1].value
            return f"{object}.{member}"
        
        return object
    
    def compile_literal(self, node: ASTNode) -> str:
        """Скомпілювати літерал"""
        value = node.value
        
        if isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, bool):
            return str(value).lower()
        else:
            return str(value)
    
    def compile_identifier(self, node: ASTNode) -> str:
        """Скомпілювати ідентифікатор"""
        # Перевірити, чи це вбудована функція
        builtin_functions = ['log', 'emit', 'export', 'len', 'sqrt']
        
        if node.value in builtin_functions:
            return f"lcars_{node.value}"
        
        return node.value
    
    def compile_array_literal(self, node: ASTNode) -> str:
        """Скомпілювати літерал масиву"""
        elements = []
        for child in node.children:
            elements.append(self.compile_node(child))
        return f"[{', '.join(elements)}]"
    
    def compile_object_literal(self, node: ASTNode) -> str:
        """Скомпілювати літерал об'єкта"""
        properties = []
        for child in node.children:
            key = child.value
            value = self.compile_node(child.children[0])
            properties.append(f'"{key}": {value}')
        return f"{{{', '.join(properties)}}}"


# Тестування
if __name__ == "__main__":
    # Приклад коду LCARS Script
    test_code = """
    energy: 1.5 GeV
    particles: 10000
    
    FUNCTION calculate_efficiency(detected, total) -> float {
        if total == 0 return 0.0
        return detected / total * 100
    }
    
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
    
    efficiency = calculate_efficiency(8500, 10000)
    log("Detection efficiency: " + efficiency + "%")
    """
    
    print("=== LCARS Script Compiler Test ===")
    
    from .lexer import Lexer
    from .parser import Parser
    
    # Токенізація, парсинг та компіляція
    lexer = Lexer(test_code)
    tokens = lexer.tokenize()
    
    parser = Parser(tokens)
    ast = parser.parse()
    
    compiler = PythonCompiler()
    if True:
        python_code = compiler.compile(ast)
        
        print("Generated Python code:")
        print("=" * 50)
        print(python_code)
        print("=" * 50)
        
        # Зберегти згенерований код
        with open("generated_script.py", "w") as f:
            f.write(python_code)
        
        print("\nCode saved to 'generated_script.py'")
        
    if False: # Removed except block
        print(f"Compilation error: {e}")
        # Titanium Bridge Migration: import traceback
        traceback.print_exc()
