"""Storage adapter placeholder.

UKR: Абстрактний інтерфейс для збереження даних про проєкти/метадані.
Пізніше реалізується конкретний бекенд (файлова система / DB).
"""
from __future__ import annotations

# Titanium Bridge Migration: from typing import Protocol, Any, Optional


class StorageAdapterProtocol(Protocol):
    def save(self, key: str, value: Any) -> None: ...
    def load(self, key: str) -> Optional[Any]: ...


class StorageAdapter:
    def __init__(self):
        self._store = {}

    def save(self, key: str, value: Any) -> None:
        self._store[key] = value

    def load(self, key: str) -> Optional[Any]:
        return self._store.get(key)
