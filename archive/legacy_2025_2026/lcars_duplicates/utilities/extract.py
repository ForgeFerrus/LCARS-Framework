# LCARS Framework :: Extract Palettes v1.0.0
# Утиліта витягування палітр з зображень
# Автор: LCARS Development Team
# Ліцензія: MIT

from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
import json
from lcars.base.version import getVersion

version = getVersion()
print(f"LCARS Extract Palettes v{version}")


# Імпортувати PIL якщо доступно
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None

# Імпортувати numpy якщо доступно
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    # Конвертувати RGB в hex
    return '#%02X%02X%02X' % rgb


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    # Конвертувати hex в RGB
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def load_image(image_path: str) -> Optional[Any]:
    # Завантажити зображення
    if not PIL_AVAILABLE:
        return None
    
    try:
        image = Image.open(image_path).convert('RGB')
        return image
    except:
        return None


def get_image_size(image_path: str) -> Tuple[int, int]:
    # Отримати розмір зображення
    image = load_image(image_path)
    if image:
        return image.size
    return (0, 0)


def extract_dominant_colors(image_path: str, num_colors: int = 5) -> List[str]:
    # Витягнути домінуючі кольори
    if not PIL_AVAILABLE or not NUMPY_AVAILABLE:
        return []
    
    image = load_image(image_path)
    if not image:
        return []
    
    # Змінити розмір для швидкості
    image = image.resize((150, 150))
    
    # Конвертувати в numpy array
    img_array = np.array(image)
    pixels = img_array.reshape(-1, 3)
    
    # Простий k-means clustering
    from sklearn.cluster import KMeans
    try:
        kmeans = KMeans(n_clusters=num_colors, random_state=42)
        kmeans.fit(pixels)
        
        colors = []
        for center in kmeans.cluster_centers_:
            rgb = tuple(map(int, center))
            hex_color = rgb_to_hex(rgb)
            colors.append(hex_color)
        
        return colors
    except:
        # Fallback до простого вибору
        unique_colors = []
        step = max(1, len(pixels) // 1000)
        for i in range(0, len(pixels), step):
            rgb = tuple(pixels[i])
            hex_color = rgb_to_hex(rgb)
            if hex_color not in unique_colors:
                unique_colors.append(hex_color)
            if len(unique_colors) >= num_colors:
                break
        
        return unique_colors[:num_colors]


def extract_color_palette(image_path: str, num_colors: int = 8) -> Dict[str, Any]:
    # Витягнути повну палітру
    colors = extract_dominant_colors(image_path, num_colors)
    
    if not colors:
        return {
            'success': False,
            'colors': [],
            'message': 'Failed to extract colors'
        }
    
    return {
        'success': True,
        'colors': colors,
        'count': len(colors),
        'image_path': str(Path(image_path).absolute())
    }


def analyze_color_distribution(image_path: str) -> Dict[str, Any]:
    # Аналізувати розподіл кольорів
    if not PIL_AVAILABLE or not NUMPY_AVAILABLE:
        return {}
    
    image = load_image(image_path)
    if not image:
        return {}
    
    img_array = np.array(image)
    
    # Розподіл по каналах
    red_channel = img_array[:, :, 0].flatten()
    green_channel = img_array[:, :, 1].flatten()
    blue_channel = img_array[:, :, 2].flatten()
    
    return {
        'red_mean': float(red_channel.mean()),
        'green_mean': float(green_channel.mean()),
        'blue_mean': float(blue_channel.mean()),
        'red_std': float(red_channel.std()),
        'green_std': float(green_channel.std()),
        'blue_std': float(blue_channel.std()),
        'brightness': float(img_array.mean()),
        'contrast': float(img_array.std())
    }


def extract_lcars_colors(image_path: str) -> List[str]:
    # Витягнути LCARS сумісні кольори
    colors = extract_dominant_colors(image_path, 10)
    
    # Фільтрувати по яскравості та насиченості
    lcars_colors = []
    
    for color in colors:
        rgb = hex_to_rgb(color)
        r, g, b = rgb
        
        # Мінімальна яскравість для LCARS
        brightness = (r + g + b) / 3
        if brightness < 30:
            continue
        
        # Перевірити чи не це сірий колір
        if abs(r - g) < 10 and abs(g - b) < 10:
            continue
        
        lcars_colors.append(color)
    
    return lcars_colors[:6]  # Повернути до 6 кольорів


def create_palette_from_image(image_path: str, palette_name: str = None) -> Dict[str, Any]:
    # Створити палітру з зображення
    if palette_name is None:
        palette_name = Path(image_path).stem
    
    palette = extract_color_palette(image_path)
    
    if not palette['success']:
        return palette
    
    # Додати додаткову інформацію
    analysis = analyze_color_distribution(image_path)
    
    palette.update({
        'name': palette_name,
        'analysis': analysis,
        'lcars_colors': extract_lcars_colors(image_path)
    })
    
    return palette


def save_palette(palette: Dict[str, Any], output_path: str) -> bool:
    # Зберегти палітру в файл
    try:
        with open(output_path, 'w') as f:
            json.dump(palette, f, indent=2)
        return True
    except:
        return False


def load_palette(palette_path: str) -> Dict[str, Any]:
    # Завантажити палітру з файлу
    try:
        with open(palette_path, 'r') as f:
            return json.load(f)
    except:
        return {}


def compare_palettes(palette1: Dict[str, Any], palette2: Dict[str, Any]) -> Dict[str, Any]:
    # Порівняти дві палітри
    colors1 = palette1.get('colors', [])
    colors2 = palette2.get('colors', [])
    
    # Знайти спільні кольори
    common_colors = set(colors1) & set(colors2)
    
    # Обчислити схожість
    total_colors = len(set(colors1) | set(colors2))
    similarity = len(common_colors) / total_colors if total_colors > 0 else 0
    
    return {
        'common_colors': list(common_colors),
        'common_count': len(common_colors),
        'similarity': similarity,
        'unique_to_palette1': list(set(colors1) - set(colors2)),
        'unique_to_palette2': list(set(colors2) - set(colors1))
    }


def extract_bands(image_path: str, bg_threshold: int = 30) -> List[Tuple[int, int]]:
    # Витягнути горизонтальні смуги
    if not PIL_AVAILABLE or not NUMPY_AVAILABLE:
        return []
    
    image = load_image(image_path)
    if not image:
        return []
    
    img_array = np.array(image)
    h, w, _ = img_array.shape
    
    # Створити маску яскравості
    brightness = img_array.max(axis=2)
    mask = brightness > bg_threshold
    
    # Побудувати гістограму по Y
    y_hist = mask.sum(axis=1)
    threshold = max(3, int(w * 0.01))
    
    bands = []
    in_band = False
    start = 0
    
    for y, value in enumerate(y_hist):
        if not in_band and value >= threshold:
            in_band = True
            start = y
        elif in_band and value < threshold:
            in_band = False
            bands.append((start, y))
    
    if in_band:
        bands.append((start, h))
    
    return bands


def extract_colors_from_bands(image_path: str, bg_threshold: int = 30) -> List[str]:
    # Витягнути кольори зі смуг
    bands = extract_bands(image_path, bg_threshold)
    
    if not bands:
        return []
    
    image = load_image(image_path)
    if not image:
        return []
    
    img_array = np.array(image)
    all_colors = []
    
    for start_y, end_y in bands:
        band_pixels = img_array[start_y:end_y, :, :]
        unique_colors = np.unique(band_pixels.reshape(-1, 3), axis=0)
        
        for rgb in unique_colors:
            hex_color = rgb_to_hex(tuple(rgb))
            all_colors.append(hex_color)
    
    # Повернути унікальні кольори
    return list(set(all_colors))


def generate_lcars_theme_from_image(image_path: str, theme_name: str = None) -> Dict[str, Any]:
    # Згенерувати LCARS тему з зображення
    if theme_name is None:
        theme_name = Path(image_path).stem
    
    colors = extract_lcars_colors(image_path)
    
    if len(colors) < 3:
        return {
            'success': False,
            'message': 'Not enough suitable colors found'
        }
    
    # Створити тему
    theme = {
        'name': theme_name,
        'success': True,
        'colors': colors,
        'primary': colors[0] if len(colors) > 0 else '#000000',
        'secondary': colors[1] if len(colors) > 1 else '#000000',
        'accent': colors[2] if len(colors) > 2 else '#000000',
        'background': '#000000',
        'text': '#FFFFFF',
        'warning': colors[-1] if len(colors) > 3 else '#FF0000',
        'error': '#FF0000',
        'success': '#00FF00'
    }
    
    return theme


# Швидкі функції
def extract_colors(image_path: str, num_colors: int = 5) -> List[str]:
    return extract_dominant_colors(image_path, num_colors)

def get_palette(image_path: str) -> Dict[str, Any]:
    return extract_color_palette(image_path)

def analyze_image(image_path: str) -> Dict[str, Any]:
    return analyze_color_distribution(image_path)

def create_theme(image_path: str, name: str = None) -> Dict[str, Any]:
    return generate_lcars_theme_from_image(image_path, name)


# Перевірка доступності
def is_available() -> bool:
    return PIL_AVAILABLE and NUMPY_AVAILABLE

def get_dependencies() -> List[str]:
    deps = []
    if not PIL_AVAILABLE:
        deps.append('Pillow')
    if not NUMPY_AVAILABLE:
        deps.append('numpy')
    return deps


# Константи
DEFAULT_NUM_COLORS = 5
DEFAULT_BG_THRESHOLD = 30
LCARS_MAX_COLORS = 6

# Популярні LCARS кольори для порівняння
LCARS_REFERENCE_COLORS = [
    '#3366CC',  # Classic blue
    '#FF9966',  # Orange
    '#99FF99',  # Green
    '#FF6666',  # Red
    '#FFCC99',  # Gold
    '#00CCCC',  # Cyan
]
