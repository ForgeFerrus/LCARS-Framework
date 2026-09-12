# LCARS Framework :: Browser Utility v1.0.0
# Простий функціонал веб-браузера без інтерфейсу
# Автор: LCARS Development Team
# Ліцензія: MIT

__version__ = "1.0.0"
__author__ = "LCARS Development Team"
__license__ = "MIT"

import requests
from typing import Optional, Dict, List
from urllib.parse import urlparse, urljoin
from lcars.base.version import getVersion

version = getVersion()
# print(f"LCARS Browser v{version}")  # Вимкнено для UI

class Browser:
    # Простий веб-браузер
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'LCARS-Browser/1.0'
        })
        self.history: List[str] = []
        self.current_url: Optional[str] = None
    
    def get(self, url: str, timeout: int = 10) -> Optional[str]:
        # Завантажити сторінку
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        response = self.session.get(url, timeout=timeout)
        if response.status_code == 200:
            self.current_url = url
            if url not in self.history:
                self.history.append(url)
            return response.text
        return None
    
    def post(self, url: str, data: Optional[Dict] = None, timeout: int = 10) -> Optional[str]:
        # POST запит
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        response = self.session.post(url, data=data, timeout=timeout)
        if response.status_code == 200:
            return response.text
        return None
    
    def download(self, url: str, filename: str) -> bool:
        # Завантажити файл
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        response = self.session.get(url, stream=True)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        return False
    
    def search(self, query: str) -> Optional[str]:
        # Пошук через Google
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        return self.get(search_url)
    
    def get_links(self, html: str) -> List[str]:
        # Витягти посилання з HTML
        import re
        pattern = r'href=[\'"]?([^\'" >]+)'
        links = re.findall(pattern, html)
        
        # Фільтрувати тільки HTTP посилання
        valid_links = []
        for link in links:
            if link.startswith(('http://', 'https://')):
                valid_links.append(link)
            elif self.current_url:
                valid_links.append(urljoin(self.current_url, link))
        
        return valid_links
    
    def get_title(self, html: str) -> Optional[str]:
        # Витягти заголовок сторінки
        import re
        match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
        return match.group(1) if match else None
    
    def back(self) -> Optional[str]:
        # Повернутися назад
        if len(self.history) > 1:
            self.history.pop()  # Поточна сторінка
            if self.history:
                prev_url = self.history[-1]
                return self.get(prev_url)
        return None
    
    def clear_history(self):
        # Очистити історію
        self.history.clear()
    
    def get_status(self, url: str) -> Optional[int]:
        # Перевірити статус код
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        response = self.session.head(url, timeout=5)
        return response.status_code
    
    def get_headers(self, url: str) -> Optional[Dict]:
        # Отримати заголовки
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        response = self.session.head(url, timeout=5)
        if response.status_code < 400:
            return dict(response.headers)
        return None
    
    def get_json(self, url: str) -> Optional[Dict]:
        # Отримати JSON
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        response = self.session.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    
    def set_cookie(self, name: str, value: str):
        # Встановити cookie
        self.session.cookies[name] = value
    
    def get_cookies(self) -> Dict:
        # Отримати всі cookies
        return dict(self.session.cookies)
    
    def set_proxy(self, proxy: str):
        # Встановити проксі
        self.session.proxies.update({
            'http': proxy,
            'https': proxy
        })
    
    def set_header(self, name: str, value: str):
        # Встановити заголовок
        self.session.headers[name] = value

# Простий інтерфейс для швидкого використання
def browse(url: str) -> Optional[str]:
    # Швидке завантаження сторінки
    browser = Browser()
    return browser.get(url)

def search_google(query: str) -> Optional[str]:
    # Швидкий пошук
    browser = Browser()
    return browser.search(query)

def download_file(url: str, filename: str) -> bool:
    # Швидке завантаження файлу
    browser = Browser()
    return browser.download(url, filename)

def get_json(url: str) -> Optional[Dict]:
    # Швидке отримання JSON
    browser = Browser()
    return browser.get_json(url)

def check_site(url: str) -> bool:
    # Перевірити чи сайт доступний
    browser = Browser()
    status = browser.get_status(url)
    return status is not None and status < 400

def extract_links(html: str) -> List[str]:
    # Швидке витягування посилань
    browser = Browser()
    return browser.get_links(html)
