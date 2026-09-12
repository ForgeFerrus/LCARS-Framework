# ◤ LCARS COMLINK SERVICE // SUBSPACE VOICE & DEVICE GATEWAY 🖖
# =============================================================================
# ФАЙЛ: lcars/service/comlink.py
# ОПИС: Служба підключення та зв'язку (Comlink Service Layer).
#       Забезпечує мережевий шлюз для зв'язку зовнішніх пристроїв (Motorola LCARS 25th)
#       із комунікаційною підсистемою зорельота (Subsystem.Communication / SubspaceLink).
# СТАНДАРТ: Titanium LCARS (Zero-Except, Zero-Underscores, Strict PascalCase, Pure Classes).
# =============================================================================

from __future__ import annotations

from lcars.service.communicator import SubspaceVoiceGateway, CommunicatorAccess

ComlinkGateway = SubspaceVoiceGateway
ComlinkService = SubspaceVoiceGateway
