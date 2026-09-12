# LCARS SubspaceBridge Documentation

## Опис
SubspaceBridge — універсальний комунікаційний порт для зовнішніх систем, протоколів та інтеграцій. Використовується для передачі даних, обробки команд, синхронізації з WebBridge та ProtocolHub.

---

## Класи

### ProtocolHub
- CORE: Python, C++, C
- WEB: HTML, CSS, JS, WebAssembly, TypeScript
- NATIVE: C#, F#, Java, Rust, Go, Swift, Kotlin
- SCRIPT: Ruby, Julia, Lua, Bash, PowerShell, Perl
- LOW_LEVEL: Assembly, VHDL, Verilog, HDL
- GRAPHICS: HLSL, GLSL, CUDA, OpenCL
- SCIENCE: MATLAB, R, Fortran, LabVIEW, Mathematica
- DATA: SQL, XML, JSON, YAML, HDF5, CSV
- SIMULATION: Geant4, CERN-ROOT, G4Py
- QUANTUM: Qiskit, Cirq, Q#, PennyLane, Quil

### SubspaceBridge
- data_transmitted: Signal — передає дані у зовнішні системи.
- request_received: Signal — приймає команди від зовнішніх протоколів.
- broadcast(channel, message): передає пакет даних.
- process_external_command(cmd_id, params): обробляє зовнішню команду.

### WebBridge
- invoke_from_js(json_data): приймає дані з JavaScript/WebChannel.

---

## Використання

1. Створіть SubspaceBridge:
   ```python
   bridge = SubspaceBridge()
   bridge.data_transmitted.connect(my_handler)
   bridge.broadcast('channel', {'msg': 'data'})
   ```

2. Реєстрація мостів:
   ```python
   registry.register("Bridge.Subspace", SubspaceBridge)
   registry.register("Bridge.Web", WebBridge)
   ```

3. WebBridge для інтеграції з JS:
   ```python
   web_bridge = WebBridge()
   web_bridge.invoke_from_js('{"cmd": "test"}')
   ```

---

## Розширення
- Додавайте нові протоколи у ProtocolHub.
- Реєструйте додаткові обробники через connect.
- Розширюйте WebBridge для специфічних web-інтеграцій.

---

## Примітки
- Signal/Slot — mock-класи для внутрішньої логіки.
- Для реальної Qt-функціональності використовуйте PyQt6.
- Міст готовий для розширення, тестування, інтеграції.

---

## Актуальний стан
- Архітектура завершена.
- Підтримка основних протоколів.
- Готовий для розширення та інтеграції.

---

## Автор: GitHub Copilot
Дата: 20.03.2026
