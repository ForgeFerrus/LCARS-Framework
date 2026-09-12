"""
LCARS Layout Validator - DevTools Module

Валідатор макетів та перевірка сумісності компонентів.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Tuple

class LCARSLayoutValidator:
    """Validator for LCARS layout files and components"""
    
    def __init__(self):
        self.required_fields = {
            'component': ['type', 'name', 'x', 'y', 'width', 'height'],
            'layout': ['version', 'era', 'components'],
            'theme': ['name', 'colors', 'era']
        }
        
        self.valid_component_types = [
            'LCARSButton', 'LCARSPanel', 'LCARSLabel', 'LCARSElbow',
            'QPushButton', 'QLabel', 'QLineEdit', 'QTextEdit'
        ]
        
        self.valid_eras = [
            'PCARS_22ND', 'PCARS_23RD', 'LCARS_24TH', 
            'LCARS_25TH', 'TCARS_29TH', 'ROMULAN', 'KLINGON'
        ]
    
    def validate_layout_file(self, file_path: Path) -> Tuple[bool, List[str]]:
        """Validate a layout JSON file"""
        errors = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            return False, [f"Invalid JSON: {e}"]
        except FileNotFoundError:
            return False, [f"File not found: {file_path}"]
        
        # Check required fields
        for field in self.required_fields['layout']:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # Validate era
        if 'era' in data and data['era'] not in self.valid_eras:
            errors.append(f"Invalid era: {data['era']}. Valid: {self.valid_eras}")
        
        # Validate components
        if 'components' in data:
            for i, component in enumerate(data['components']):
                comp_errors = self.validate_component(component, i)
                errors.extend(comp_errors)
        
        return len(errors) == 0, errors
    
    def validate_component(self, component: Dict[str, Any], index: int) -> List[str]:
        """Validate a single component"""
        errors = []
        prefix = f"Component {index}"
        
        # Check required fields
        for field in self.required_fields['component']:
            if field not in component:
                errors.append(f"{prefix}: Missing field '{field}'")
        
        # Validate component type
        if 'type' in component and component['type'] not in self.valid_component_types:
            errors.append(f"{prefix}: Invalid type '{component['type']}'")
        
        # Validate coordinates and dimensions
        for field in ['x', 'y', 'width', 'height']:
            if field in component:
                try:
                    value = int(component[field])
                    if value < 0:
                        errors.append(f"{prefix}: {field} cannot be negative")
                    if field in ['width', 'height'] and value == 0:
                        errors.append(f"{prefix}: {field} cannot be zero")
                except (ValueError, TypeError):
                    errors.append(f"{prefix}: {field} must be a number")
        
        # Check for overlapping components (basic)
        if all(k in component for k in ['x', 'y', 'width', 'height']):
            # TODO: Implement overlap detection
            pass
        
        return errors
    
    def validate_theme(self, theme_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate theme data"""
        errors = []
        
        # Check required fields
        for field in self.required_fields['theme']:
            if field not in theme_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate colors
        if 'colors' in theme_data:
            colors = theme_data['colors']
            required_colors = ['background', 'text', 'primary', 'secondary']
            
            for color in required_colors:
                if color not in colors:
                    errors.append(f"Missing required color: {color}")
                elif not self.is_valid_hex_color(colors[color]):
                    errors.append(f"Invalid hex color for {color}: {colors[color]}")
        
        return len(errors) == 0, errors
    
    def is_valid_hex_color(self, color: str) -> bool:
        """Check if string is valid hex color"""
        if not isinstance(color, str):
            return False
        
        if not color.startswith('#'):
            return False
            
        if len(color) not in [4, 7]:  # #RGB or #RRGGBB
            return False
            
        try:
            int(color[1:], 16)
            return True
        except ValueError:
            return False
    
    def check_accessibility(self, layout_data: Dict[str, Any]) -> List[str]:
        """Check layout for accessibility issues"""
        warnings = []
        
        if 'components' in layout_data:
            buttons = [c for c in layout_data['components'] if 'Button' in c.get('type', '')]
            
            # Check button sizes
            for i, button in enumerate(buttons):
                if 'width' in button and 'height' in button:
                    if button['width'] < 44 or button['height'] < 44:
                        warnings.append(f"Button {i}: Size too small for accessibility (min 44x44px)")
        
        return warnings
    
    def generate_report(self, file_path: Path) -> str:
        """Generate validation report"""
        is_valid, errors = self.validate_layout_file(file_path)
        
        report = [f"Layout Validation Report: {file_path.name}"]
        report.append("=" * 50)
        
        if is_valid:
            report.append("✅ Layout is valid!")
        else:
            report.append("❌ Layout has errors:")
            for error in errors:
                report.append(f"  - {error}")
        
        # Load and check accessibility if valid JSON
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            warnings = self.check_accessibility(data)
            if warnings:
                report.append("\n⚠️  Accessibility warnings:")
                for warning in warnings:
                    report.append(f"  - {warning}")
        except:
            pass
        
        return "\n".join(report)

def validate_samples():
    """Validate all sample layouts"""
    samples_dir = Path(__file__).parent / "samples"
    validator = LCARSLayoutValidator()
    
    print("🔍 Validating LCARS layout samples...")
    
    for json_file in samples_dir.glob("*.json"):
        print(f"\n📄 {json_file.name}")
        report = validator.generate_report(json_file)
        print(report)

if __name__ == '__main__':
    validate_samples()