"""
File analyzer for LCARS Framework - handles file operations and analysis
"""
import os
from pathlib import Path
import markdown
import re

class FileAnalyzer:
    """Analyzes project files and provides file management functionality"""
    
    def __init__(self, project_path: Path):
        self.project_path = Path(project_path)
        
    def get_readme_content(self) -> str:
        """Read and parse README file"""
        readme_files = ['README.md', 'README.txt', 'README']
        
        for readme in readme_files:
            readme_path = self.project_path / readme
            if readme_path.exists():
                with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if readme.endswith('.md'):
                        return markdown.markdown(content)
                    return content
        return "No README file found"
        
    def get_source_files(self) -> list:
        """Get all source files in the project"""
        source_files = []
        for ext in ['.cc', '.cpp', '.h', '.hpp', '.py', '.mac']:
            source_files.extend(self.project_path.glob(f'**/*{ext}'))
        return source_files
        
    def get_data_files(self) -> list:
        """Get all data files in the project"""
        data_files = []
        data_dir = self.project_path / 'data'
        if data_dir.exists():
            for file in data_dir.rglob('*'):
                if file.is_file():
                    data_files.append(file)
        return data_files
        
    def get_macro_files(self) -> list:
        """Get all Geant4 macro files"""
        return list(self.project_path.glob('**/*.mac'))
        
    def get_file_content(self, file_path: Path) -> str:
        """Get content of a file with syntax highlighting hints"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        ext = file_path.suffix.lower()
        if ext in ['.cc', '.cpp', '.h', '.hpp']:
            lang = 'cpp'
        elif ext == '.py':
            lang = 'python'
        elif ext == '.mac':
            lang = 'shell'
        else:
            lang = 'text'
            
        return f'```{lang}\n{content}\n```'
        
    def get_build_info(self) -> dict:
        """Get build system information"""
        info = {
            'cmake': None,
            'make': None,
            'vs': None
        }
        
        if (self.project_path / 'CMakeLists.txt').exists():
            info['cmake'] = str(self.project_path / 'CMakeLists.txt')
            
        if (self.project_path / 'Makefile').exists():
            info['make'] = str(self.project_path / 'Makefile')
            
        vs_files = list(self.project_path.glob('*.sln'))
        if vs_files:
            info['vs'] = str(vs_files[0])
            
        return info
        
    def get_visualization_settings(self) -> dict:
        """Extract visualization settings from macro files"""
        vis_settings = {
            'driver': None,
            'style': None,
            'commands': []
        }
        
        for macro in self.get_macro_files():
            with open(macro, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Look for visualization settings
            if '/vis/' in content:
                vis_settings['commands'].extend(
                    [line.strip() for line in content.split('\n') 
                     if line.strip().startswith('/vis/')]
                )
                
                # Try to determine visualization driver
                if '/vis/open' in content:
                    driver_match = re.search(r'/vis/open\s+(\w+)', content)
                    if driver_match:
                        vis_settings['driver'] = driver_match.group(1)
                        
        return vis_settings
        
    def get_analysis_configuration(self) -> dict:
        """Determine analysis configuration from project files"""
        config = {
            'histograms': [],
            'ntuples': [],
            'output_format': None
        }
        
        # Search through source files for analysis patterns
        for src_file in self.get_source_files():
            with open(src_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Look for histogram definitions
            hist_patterns = [
                r'CreateH1\((.*?)\)',
                r'CreateH2\((.*?)\)',
                r'CreateH3\((.*?)\)'
            ]
            
            for pattern in hist_patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    config['histograms'].append(match.group(1))
                    
            # Look for ntuple definitions
            if 'CreateNtuple' in content:
                ntuple_matches = re.finditer(r'CreateNtuple\((.*?)\)', content)
                for match in ntuple_matches:
                    config['ntuples'].append(match.group(1))
                    
            # Determine output format
            if 'root' in content.lower():
                config['output_format'] = 'root'
            elif 'csv' in content.lower():
                config['output_format'] = 'csv'
                
        return config