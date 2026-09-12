# LCARS Framework :: Autobuild v1.0.0
# Система збірки нативних проєктів (C/C++, CMake)
# Автор: LCARS Development Team
# Ліцензія: MIT

import subprocess
import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# Проста версія без getVersion
version = "1.0.0"
# print(f"LCARS Autobuild v{version}")  # Вимкнено для UI


@dataclass
class BuildDiagnostics:
    # Діагностика збірки
    success: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]
    build_time: float = 0.0
    artifacts: List[str] = None
    
    def __post_init__(self):
        if self.artifacts is None:
            self.artifacts = []


class CompilerDetector:
    # Детектор компіляторів
    def __init__(self):
        self.compilers = {
            'gcc': ['gcc', '--version'],
            'clang': ['clang', '--version'],
            'msvc': ['cl'],
            'g++': ['g++', '--version'],
            'clang++': ['clang++', '--version']
        }
    
    def detect_compilers(self) -> Dict[str, bool]:
        # Виявити доступні компілятори
        available = {}
        
        for name, cmd in self.compilers.items():
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                available[name] = result.returncode == 0
            except:
                available[name] = False
        
        return available
    
    def get_default_compiler(self) -> str:
        # Отримати компілятор за замовчуванням
        compilers = self.detect_compilers()
        
        if compilers.get('gcc'):
            return 'gcc'
        elif compilers.get('clang'):
            return 'clang'
        elif compilers.get('msvc'):
            return 'msvc'
        elif compilers.get('g++'):
            return 'g++'
        elif compilers.get('clang++'):
            return 'clang++'
        else:
            return 'unknown'


class CMakeProject:
    # CMake проєкт
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.cmake_file = project_path / 'CMakeLists.txt'
        self.build_dir = project_path / 'build'
        self.install_dir = project_path / 'install'
    
    def is_valid(self) -> bool:
        # Перевірити чи це CMake проєкт
        return self.cmake_file.exists()
    
    def parse_cmake_file(self) -> Dict[str, any]:
        # Розпарсити CMakeLists.txt
        if not self.cmake_file.exists():
            return {}
        
        content = self.cmake_file.read_text(encoding='utf-8')
        
        project_info = {
            'project_name': None,
            'version': None,
            'languages': [],
            'dependencies': [],
            'targets': []
        }
        
        # Знайти назву проєкту
        project_match = re.search(r'project\s*\(\s*([^)\s]+)', content, re.IGNORECASE)
        if project_match:
            project_info['project_name'] = project_match.group(1)
        
        # Знайти версію
        version_match = re.search(r'version\s*\(\s*([^)\s]+)', content, re.IGNORECASE)
        if version_match:
            project_info['version'] = version_match.group(1)
        
        # Знайти мови
        lang_matches = re.findall(r'([a-zA-Z]+)\s*\)', content)
        project_info['languages'] = [lang for lang in lang_matches if lang.upper() in ['C', 'CXX', 'CUDA']]
        
        # Знайти залежності
        dep_matches = re.findall(r'find_package\s*\(\s*([^)\s]+)', content, re.IGNORECASE)
        project_info['dependencies'] = [dep.upper() for dep in dep_matches]
        
        # Знайти цілі
        target_matches = re.findall(r'add_executable\s*\(\s*([^)\s]+)', content, re.IGNORECASE)
        lib_matches = re.findall(r'add_library\s*\(\s*([^)\s]+)', content, re.IGNORECASE)
        project_info['targets'] = target_matches + lib_matches
        
        return project_info
    
    def configure(self, generator: str = None, build_type: str = 'Release') -> bool:
        # Конфігурувати CMake
        self.build_dir.mkdir(exist_ok=True)
        
        cmake_cmd = ['cmake']
        
        if generator:
            cmake_cmd.extend(['-G', generator])
        
        cmake_cmd.extend(['-DCMAKE_BUILD_TYPE=' + build_type])
        cmake_cmd.extend(['-DCMAKE_INSTALL_PREFIX=' + str(self.install_dir)])
        cmake_cmd.append(str(self.project_path))
        
        try:
            result = subprocess.run(
                cmake_cmd,
                cwd=self.build_dir,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return result.returncode == 0
        except:
            return False
    
    def build(self, target: str = None, parallel: int = None) -> bool:
        # Зібрати проєкт
        if not self.build_dir.exists():
            return False
        
        build_cmd = ['cmake', '--build', str(self.build_dir), '--config', 'Release']
        
        if target:
            build_cmd.extend(['--target', target])
        
        if parallel:
            build_cmd.extend(['--parallel', str(parallel)])
        
        try:
            result = subprocess.run(
                build_cmd,
                cwd=self.build_dir,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            return result.returncode == 0
        except:
            return False
    
    def install(self) -> bool:
        # Встановити проєкт
        if not self.build_dir.exists():
            return False
        
        install_cmd = ['cmake', '--install', str(self.build_dir)]
        
        try:
            result = subprocess.run(
                install_cmd,
                cwd=self.build_dir,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return result.returncode == 0
        except:
            return False
    
    def clean(self) -> bool:
        # Очистити збірку
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        
        if self.install_dir.exists():
            shutil.rmtree(self.install_dir)
        
        return True


class MakefileProject:
    # Makefile проєкт
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.makefile = project_path / 'Makefile'
    
    def is_valid(self) -> bool:
        # Перевірити чи це Makefile проєкт
        return self.makefile.exists()
    
    def build(self, target: str = None, parallel: int = None) -> bool:
        # Зібрати проєкт
        make_cmd = ['make']
        
        if target:
            make_cmd.append(target)
        
        if parallel:
            make_cmd.extend(['-j', str(parallel)])
        
        try:
            result = subprocess.run(
                make_cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            return result.returncode == 0
        except:
            return False
    
    def clean(self) -> bool:
        # Очистити збірку
        clean_cmd = ['make', 'clean']
        
        try:
            subprocess.run(
                clean_cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            return True
        except:
            return False


class BuildAnalyzer:
    # Аналізатор помилок збірки
    def __init__(self):
        self.error_patterns = {
            'undefined_reference': r'undefined reference to [`\']([^`\']+)[`\'\"]',
            'cannot_find': r'cannot find ([^\\s]+)',
            'no_such_file': r'no such file or directory: ([^\\s]+)',
            'permission_denied': r'permission denied: ([^\\s]+)',
            'syntax_error': r'syntax error ([^\\s]+)',
            'redefinition': r'redefinition of [`\']([^`\']+)[`\'\"]',
            'missing_semicolon': r'expected [`\'];[`\'] at end of input',
            'missing_bracket': r'expected [`\']([{}])[`\'\"]',
            'type_mismatch': r'cannot convert [`\']([^`\']+)[`\'\"] to [`\']([^`\']+)[`\'\"]'
        }
        
        self.warning_patterns = {
            'unused_variable': r'unused variable [`\']([^`\']+)[`\'\"]',
            'deprecated': r'[\[]deprecated[\]]',
            'implicit_declaration': r'implicit declaration of function [`\']([^`\']+)[`\'\"]',
            'comparison_always_true': r'comparison is always [^\\s]+',
            'unused_function': r'[\[]unused function[\]]'
        }
    
    def analyze_output(self, output: str) -> BuildDiagnostics:
        # Проаналізувати вивід збірки
        diagnostics = BuildDiagnostics(
            success=True,
            errors=[],
            warnings=[],
            suggestions=[]
        )
        
        lines = output.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            
            # Перевірити на помилки
            for error_type, pattern in self.error_patterns.items():
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    diagnostics.errors.append(line.strip())
                    diagnostics.success = False
                    
                    # Додати пропозиції
                    suggestion = self._get_suggestion(error_type, match)
                    if suggestion:
                        diagnostics.suggestions.append(suggestion)
            
            # Перевірити на попередження
            for warning_type, pattern in self.warning_patterns.items():
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    diagnostics.warnings.append(line.strip())
                    
                    # Додати пропозиції
                    suggestion = self._get_warning_suggestion(warning_type, match)
                    if suggestion:
                        diagnostics.suggestions.append(suggestion)
        
        return diagnostics
    
    def _get_suggestion(self, error_type: str, match) -> str:
        # Отримати пропозицію для помилки
        suggestions = {
            'undefined_reference': f"Check if function '{match.group(1)}' is declared or linked",
            'cannot_find': f"Install missing file/library: {match.group(1)}",
            'no_such_file': f"Create missing file: {match.group(1)}",
            'permission_denied': f"Check permissions for: {match.group(1)}",
            'syntax_error': f"Fix syntax error near: {match.group(1)}",
            'redefinition': f"Remove duplicate definition of: {match.group(1)}",
            'missing_semicolon': "Add missing semicolon ';' at end of statement",
            'missing_bracket': f"Add missing bracket: {match.group(1)}",
            'type_mismatch': f"Fix type conversion between {match.group(1)} and {match.group(2)}"
        }
        
        return suggestions.get(error_type, "")
    
    def _get_warning_suggestion(self, warning_type: str, match) -> str:
        # Отримати пропозицію для попередження
        suggestions = {
            'unused_variable': f"Remove or use variable: {match.group(1)}",
            'deprecated': "Replace deprecated function with modern alternative",
            'implicit_declaration': f"Add proper declaration for function: {match.group(1)}",
            'comparison_always_true': "Fix always-true comparison",
            'unused_function': "Remove or use unused function"
        }
        
        return suggestions.get(warning_type, "")


class Orchestrator:
    # Основний оркестратор збірки
    def __init__(self, project_path: Path):
        self.project_path = Path(project_path)
        self.compiler_detector = CompilerDetector()
        self.build_analyzer = BuildAnalyzer()
        self.diagnostics = BuildDiagnostics(
            success=False,
            errors=[],
            warnings=[],
            suggestions=[]
        )
    
    def detect_project_type(self) -> str:
        # Виявити тип проєкту
        cmake_project = CMakeProject(self.project_path)
        makefile_project = MakefileProject(self.project_path)
        
        if cmake_project.is_valid():
            return 'cmake'
        elif makefile_project.is_valid():
            return 'makefile'
        else:
            return 'unknown'
    
    def build_project(self, clean: bool = False, parallel: int = None) -> BuildDiagnostics:
        # Зібрати проєкт
        start_time = datetime.now()
        
        project_type = self.detect_project_type()
        
        if project_type == 'cmake':
            self.diagnostics = self._build_cmake_project(clean, parallel)
        elif project_type == 'makefile':
            self.diagnostics = self._build_makefile_project(clean, parallel)
        else:
            self.diagnostics.success = False
            self.diagnostics.errors.append("No supported build system found")
            self.diagnostics.suggestions.append("Create CMakeLists.txt or Makefile")
        
        # Обчислити час збірки
        end_time = datetime.now()
        self.diagnostics.build_time = (end_time - start_time).total_seconds()
        
        return self.diagnostics
    
    def _build_cmake_project(self, clean: bool, parallel: int) -> BuildDiagnostics:
        # Зібрати CMake проєкт
        cmake_project = CMakeProject(self.project_path)
        
        if clean:
            cmake_project.clean()
        
        # Конфігурувати
        if not cmake_project.configure():
            return self._create_error_diagnostics("CMake configuration failed")
        
        # Зібрати
        if not cmake_project.build(parallel=parallel):
            return self._create_error_diagnostics("CMake build failed")
        
        # Встановити
        cmake_project.install()
        
        # Зібрати артефакти
        artifacts = self._collect_artifacts(cmake_project.install_dir)
        
        return BuildDiagnostics(
            success=True,
            errors=[],
            warnings=[],
            suggestions=[],
            build_time=0,
            artifacts=artifacts
        )
    
    def _build_makefile_project(self, clean: bool, parallel: int) -> BuildDiagnostics:
        # Зібрати Makefile проєкт
        makefile_project = MakefileProject(self.project_path)
        
        if clean:
            makefile_project.clean()
        
        if not makefile_project.build(parallel=parallel):
            return self._create_error_diagnostics("Make build failed")
        
        # Зібрати артефакти
        artifacts = self._collect_makefile_artifacts()
        
        return BuildDiagnostics(
            success=True,
            errors=[],
            warnings=[],
            suggestions=[],
            build_time=0,
            artifacts=artifacts
        )
    
    def _collect_artifacts(self, install_dir: Path) -> List[str]:
        # Зібрати артефакти з install директорії
        artifacts = []
        
        if install_dir.exists():
            for item in install_dir.rglob('*'):
                if item.is_file():
                    artifacts.append(str(item))
        
        return artifacts
    
    def _collect_makefile_artifacts(self) -> List[str]:
        # Зібрати артефакти з Makefile проєкту
        artifacts = []
        
        # Шукати виконувані файли
        for item in self.project_path.rglob('*'):
            if item.is_file() and not item.name.startswith('.'):
                # Перевірити чи це виконуваний файл
                if item.suffix in ['.exe', '', '.out'] or os.access(item, os.X_OK):
                    artifacts.append(str(item))
        
        return artifacts
    
    def _create_error_diagnostics(self, message: str) -> BuildDiagnostics:
        # Створити діагностику з помилкою
        return BuildDiagnostics(
            success=False,
            errors=[message],
            warnings=[],
            suggestions=["Check build configuration and dependencies"]
        )
    
    def get_project_info(self) -> Dict[str, any]:
        # Отримати інформацію про проєкт
        project_type = self.detect_project_type()
        info = {
            'type': project_type,
            'path': str(self.project_path),
            'compilers': self.compiler_detector.detect_compilers(),
            'default_compiler': self.compiler_detector.get_default_compiler()
        }
        
        if project_type == 'cmake':
            cmake_project = CMakeProject(self.project_path)
            info.update(cmake_project.parse_cmake_file())
        
        return info


# Швидкі функції
def detect_project(project_path: str) -> str:
    orchestrator = Orchestrator(Path(project_path))
    return orchestrator.detect_project_type()

def build_project(project_path: str, clean: bool = False, parallel: int = None) -> BuildDiagnostics:
    orchestrator = Orchestrator(Path(project_path))
    return orchestrator.build_project(clean, parallel)

def get_project_info(project_path: str) -> Dict[str, any]:
    orchestrator = Orchestrator(Path(project_path))
    return orchestrator.get_project_info()

def detect_compilers() -> Dict[str, bool]:
    detector = CompilerDetector()
    return detector.detect_compilers()

def get_default_compiler() -> str:
    detector = CompilerDetector()
    return detector.get_default_compiler()


# Константи
BUILD_TYPES = ['Debug', 'Release', 'RelWithDebInfo', 'MinSizeRel']
SUPPORTED_PROJECTS = ['cmake', 'makefile']
COMMON_COMPILERS = ['gcc', 'clang', 'msvc', 'g++', 'clang++']
BUILD_ARTIFACTS = ['.exe', '.out', '.dll', '.so', '.dylib', '.a', '.lib']

# Псевдонім для сумісності
AutobuildManager = Orchestrator
