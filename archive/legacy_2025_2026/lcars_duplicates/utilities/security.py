# LCARS Framework :: Security Utils v1.0.0
# Прості утиліти безпеки
# Автор: LCARS Development Team
# Ліцензія: MIT

import hashlib
import secrets
import time
import base64
import hmac
import json
import string
import re
from pathlib import Path
from typing import Dict, Optional, Any

# Проста версія без getVersion
version = "1.0.0"
# print(f"LCARS Security Utils v{version}")  # Вимкнено для UI

def hash_password(password: str, salt: str = None) -> Dict[str, str]:
    # Хешування паролю
    if salt is None:
        salt = secrets.token_hex(16)
    
    # Простий SHA256 з сіллю
    hash_obj = hashlib.sha256()
    hash_obj.update((salt + password).encode())
    password_hash = hash_obj.hexdigest()
    
    return {
        'hash': password_hash,
        'salt': salt,
        'algorithm': 'sha256'
    }

def verify_password(password: str, hash_data: Dict[str, str]) -> bool:
    # Перевірка паролю
    new_hash = hash_password(password, hash_data['salt'])
    return new_hash['hash'] == hash_data['hash']

def generate_password(length: int = 16) -> str:
    # Генерація паролю
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def check_password_strength(password: str) -> Dict[str, Any]:
    # Перевірка складності паролю
    score = 0
    issues = []
    
    # Довжина
    if len(password) >= 12:
        score += 2
    elif len(password) >= 8:
        score += 1
    else:
        issues.append("Пароль занадто короткий")
    
    # Складність
    if re.search(r'[a-z]', password):
        score += 1
    else:
        issues.append("Відсутні малі літери")
    
    if re.search(r'[A-Z]', password):
        score += 1
    else:
        issues.append("Відсутні великі літери")
    
    if re.search(r'\d', password):
        score += 1
    else:
        issues.append("Відсутні цифри")
    
    if re.search(r'[!@#$%^&*]', password):
        score += 1
    else:
        issues.append("Відсутні спеціальні символи")
    
    # Сила паролю
    if score >= 5:
        strength = "Дуже сильний"
    elif score >= 4:
        strength = "Сильний"
    elif score >= 3:
        strength = "Середній"
    elif score >= 2:
        strength = "Слабкий"
    else:
        strength = "Дуже слабкий"
    
    return {
        'score': score,
        'max_score': 5,
        'strength': strength,
        'issues': issues,
        'length': len(password)
    }

def generate_token(length: int = 32) -> str:
    # Генерація токену
    return secrets.token_urlsafe(length)

def hash_data(data: str, algorithm: str = 'sha256') -> str:
    # Хешування даних
    if algorithm == 'sha256':
        return hashlib.sha256(data.encode()).hexdigest()
    elif algorithm == 'sha512':
        return hashlib.sha512(data.encode()).hexdigest()
    elif algorithm == 'md5':
        return hashlib.md5(data.encode()).hexdigest()
    else:
        raise ValueError(f"Непідтримуваний алгоритм: {algorithm}")

def generate_api_key(length: int = 32) -> str:
    # Генерація API ключа
    return secrets.token_urlsafe(length)

def verify_signature(data: str, signature: str, secret: str) -> bool:
    # Перевірка підпису
    expected = hmac.new(secret.encode(), data.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

def create_session_token() -> str:
    # Токен сесії
    return secrets.token_urlsafe(32)

def simple_encrypt(data: str, key: str) -> str:
    # Просте шифрування
    key_bytes = key.encode()[:32].ljust(32, b'0')
    data_bytes = data.encode()
    
    # XOR шифрування
    encrypted = bytes(a ^ b for a, b in zip(data_bytes, key_bytes))
    return base64.b64encode(encrypted).decode()

def simple_decrypt(encrypted_data: str, key: str) -> str:
    # Просте розшифрування
    key_bytes = key.encode()[:32].ljust(32, b'0')
    encrypted_bytes = base64.b64decode(encrypted_data.encode())
    
    # XOR розшифрування
    decrypted = bytes(a ^ b for a, b in zip(encrypted_bytes, key_bytes))
    return decrypted.decode()

# Швидкі функції
def secure_random(length: int = 32) -> str:
    return secrets.token_hex(length)

def generate_uuid() -> str:
    import uuid
    return str(uuid.uuid4())

def create_file_hash(file_path: str) -> str:
    # Хеш файлу
    path = Path(file_path)
    with open(file_path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

# Приклади використання
if __name__ == "__main__":
    # Тестування функцій
    password = "TestPassword123!"
    hashed = hash_password(password)
    print(f"Hashed password: {hashed}")
    
    is_valid = verify_password(password, hashed)
    print(f"Password valid: {is_valid}")
    
    strength = check_password_strength(password)
    print(f"Password strength: {strength}")
    
    token = generate_token()
    print(f"Generated token: {token}")
