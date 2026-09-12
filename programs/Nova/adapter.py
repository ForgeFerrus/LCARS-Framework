import json
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from lcars.base.register import REGISTRY
from lcars.base.type import LCARS
from lcars.modules.sound_manager import get_sound_manager
from lcars.service.onboard import Computer
from lcars.system.environment import Runtime

# Адаптер Nova для локального QVAC-host.
# Тут є тільки зв'язок з моделлю, коротка пам'ять діалогу та безпечні дії системи.
# Перевіряє, чи потрібний порт уже відкритий.
def PortOpen(host: str, port: int) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.25)
    try:
        return sock.connect_ex((host, port)) == 0
    finally:
        sock.close()
# Готує локальні параметри, пам'ять і місток до QVAC-host.
class NovaAdapter:
    def __init__(self) -> None:
        host_value = Runtime.get("QVAC_HOST", "127.0.0.1") or "127.0.0.1"
        port_value = Runtime.get("GATEWAY_PORT", Runtime.get("QVAC_PORT", "3688")) or "3688"
        self.Host: str = str(host_value)
        self.Port: int = int(port_value)
        self.BaseUrl: str = f"http://{self.Host}:{self.Port}"
        self.Model: str = str(Runtime.get("QVAC_MODEL", "local-model") or "local-model")
        self.process: subprocess.Popen | None = None
        self.ready: bool = False
        self.ServerScript: str = self.ResolveServerScript()
        self.CliScript: str = self.ResolveCliScript()
        self.NodeExecutable: str = shutil.which("node") or "node"
        self.Memory: list[dict[str, str]] = []
        self.MemoryLimit: int = 24
        self.EnsureHost()

    # Знаходить локальний скрипт сервера QVAC поруч із цим адаптером.
    def ResolveServerScript(self) -> str:
        script = Path(__file__).resolve().parents[2] / "lcars" / "service" / "network.py"
        return str(script) if script.exists() else ""

    # Знаходить локальний CLI-скрипт QVAC для запасного шляху.
    def ResolveCliScript(self) -> str:
        here = Path(__file__).resolve().parent
        script = here / "sdk" / "cli.mjs"
        return str(script) if script.exists() else ""

    # Запускає host, якщо порт ще не відкритий.
    def EnsureHost(self) -> None:
        NetworkModule = LCARS.Import("lcars.service.network")
        NetworkService = NetworkModule.NetworkSubsystem.GetInstance() if NetworkModule else None
        self.ready = bool(NetworkService and NetworkService.StartGateway())

    # Перевіряє, чи host зараз доступний.
    def IsReady(self) -> bool:
        NetworkModule = LCARS.Import("lcars.service.network")
        NetworkService = NetworkModule.NetworkSubsystem.GetInstance() if NetworkModule else None
        self.ready = bool(NetworkService and NetworkService.IsGatewayActive())
        return self.ready

    # Надсилає один JSON-запит і повертає розібрану відповідь або помилку.
    def PostJson(self, path: str, payload: Dict[str, Any], timeout: int = 120) -> Dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        request = Request(
            f"{self.BaseUrl}{path}",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(request, timeout=timeout) as response:
                raw = response.read().decode("utf-8")
        except HTTPError as error:
            raw = error.read().decode("utf-8", "ignore") if error.fp else ""
            if raw:
                return {"error": raw}
            return {"error": str(error)}
        except URLError as error:
            return {"error": str(error)}

        if not raw:
            return {}

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            return {"error": raw}

        if isinstance(parsed, dict):
            return parsed
        return {"result": parsed}

    # Складає список повідомлень для генерації.
    def BuildMessages(self, prompt: str, system_prompt: str = "", context: str = "") -> list[dict[str, str]]:
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if context:
            messages.append({"role": "system", "content": f"Context:\n{context}"})
        messages.extend(self.Memory)
        messages.append({"role": "user", "content": prompt})
        return messages

    # Оновлює коротку пам'ять і тримає її в межах ліміту.
    def StoreMemory(self, role: str, content: str) -> None:
        if not content:
            return
        self.Memory.append({"role": role, "content": content})
        if len(self.Memory) > self.MemoryLimit:
            self.Memory = self.Memory[-self.MemoryLimit :]

    # Надсилає повідомлення до QVAC-ендпоінта генерації.
    def Generate(self, messages: list[dict[str, str]]) -> Dict[str, Any]:
        payload = {"messages": messages}
        return self.PostJson("/generate", payload)

    # Надсилає повідомлення через CLI-запасний шлях, коли host недоступний.
    def GenerateViaCli(self, messages: list[dict[str, str]]) -> str:
        if not self.CliScript:
            return "NOVA QVAC ERROR: CLI script not found"

        command = [
            self.NodeExecutable,
            self.CliScript,
            "--messages-json",
            json.dumps(messages, ensure_ascii=False),
        ]
        startup = {
            "cwd": str(Path(self.CliScript).parent),
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "text": True,
        }
        result = subprocess.run(command, **startup)
        text = (result.stdout or "").strip()
        if text:
            return text
        error = (result.stderr or "").strip()
        if error:
            return f"NOVA QVAC ERROR: {error}"
        return "NOVA QVAC ERROR: empty CLI response"

    # Повертає тільки текст відповіді або короткий рядок помилки.
    def GenerateText(self, messages: list[dict[str, str]]) -> str:
        if self.IsReady():
            reply = self.Generate(messages)
        else:
            reply = {}

        if isinstance(reply, dict):
            text = reply.get("result", "")
            if isinstance(text, str) and text.strip():
                return text
            error = reply.get("error", "")
            if isinstance(error, str) and error:
                if self.CliScript:
                    cli_text = self.GenerateViaCli(messages)
                    if cli_text and not cli_text.startswith("NOVA QVAC ERROR:"):
                        return cli_text
                return f"NOVA QVAC ERROR: {error}"

        if self.CliScript:
            cli_text = self.GenerateViaCli(messages)
            if cli_text:
                return cli_text

        return "NOVA QVAC ERROR: empty response"

    # Повертає короткий технічний стан.
    def HealthCheck(self) -> Dict[str, Any]:
        return {
            "name": "nova",
            "ready": self.IsReady(),
            "host": self.Host,
            "port": self.Port,
            "api": self.BaseUrl,
            "endpoint": "/generate",
            "model": self.Model,
            "server": self.ServerScript,
            "transport": "http",
            "process": self.process is not None and self.process.poll() is None,
            "memory": len(self.Memory),
        }

    # Зупиняє запущений host-процес.
    def Shutdown(self) -> None:
        NetworkModule = LCARS.Import("lcars.service.network")
        NetworkService = NetworkModule.NetworkSubsystem.GetInstance() if NetworkModule else None
        if NetworkService:
            NetworkService.StopGateway()
        self.ready = False

    # Читає JSON-план, якщо Nova повернула команду для інструмента.
    def ParseToolPlan(self, text: str) -> Dict[str, Any]:
        raw = text.strip()
        if not raw.startswith("{") or not raw.endswith("}"):
            return {}
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            return {}
        if isinstance(parsed, dict):
            return parsed
        return {}

    # Виконує тільки безпечні системні дії, які Nova може запросити.
    def ExecuteTool(self, tool_name: str, args: Dict[str, Any]) -> str:
        if tool_name == "GetSystemStatus":
            status = Computer().GetCoreDiagnostics()
            return json.dumps(status, ensure_ascii=False)

        if tool_name == "PlaySound":
            sound_name = args.get("SoundName", "")
            if sound_name:
                get_sound_manager().play(sound_name)
                return f"Playing sound: {sound_name}."
            return "Sound name missing."

        return "Action failed."

    # Запускає Nova у звичайному текстовому або інструментальному режимі.
    def ToolDriver(self, prompt: str) -> Dict[str, Any]:
        system_prompt = (
            "You are Nova, the onboard LCARS AI.\n"
            "Return plain text for normal answers.\n"
            "If a ship action is needed, return a single JSON object only.\n"
            "Valid tool names are GetSystemStatus and PlaySound.\n"
            "Schema:\n"
            '{"reply":"short text","tool":"Name or empty","args":{}}\n'
        )
        messages = self.BuildMessages(prompt, system_prompt=system_prompt)
        first_pass = self.GenerateText(messages)
        if not first_pass:
            return {"status": "FAIL: empty response"}

        self.StoreMemory("user", prompt)
        self.StoreMemory("assistant", first_pass)

        plan = self.ParseToolPlan(first_pass)
        tool_name = str(plan.get("tool", "")).strip()
        if not tool_name:
            return {"status": first_pass}

        args = plan.get("args", {})
        if not isinstance(args, dict):
            args = {}

        tool_result = self.ExecuteTool(tool_name, args)
        followup = messages + [
            {"role": "assistant", "content": first_pass},
            {"role": "system", "content": f"Tool result: {tool_result}"},
            {"role": "user", "content": "Reply with the final user-facing text only."},
        ]
        final_text = self.GenerateText(followup)
        self.StoreMemory("assistant", final_text or tool_result)
        return {"status": final_text or tool_result}

    # Єдина точка входу для текстових запитів і названих дій.
    def ExecuteAction(self, ActionOrPrompt: str, Params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        if ActionOrPrompt == "health":
            return {"result": self.HealthCheck()}

        if ActionOrPrompt == "forget":
            self.Memory.clear()
            return {"result": "Memory cleared"}

        if not self.IsReady():
            self.EnsureHost()

        if not self.IsReady():
            if Params is None:
                return {"status": "FAIL: Nova host is not ready"}
            return {"result": "NOVA QVAC ERROR: host not ready"}

        if Params is None:
            return self.ToolDriver(ActionOrPrompt)

        if ActionOrPrompt in ("generate", "chat"):
            messages = Params.get("messages")
            if not messages:
                prompt = Params.get("prompt", "")
                system_prompt = Params.get("systemPrompt", "")
                context = Params.get("context", "")
                messages = self.BuildMessages(prompt, system_prompt, context)

            reply = self.GenerateText(messages)
            self.StoreMemory("user", Params.get("prompt", ActionOrPrompt))
            self.StoreMemory("assistant", reply)
            self.ready = True
            return {"result": reply}

        if ActionOrPrompt == "status":
            return {"result": self.HealthCheck()}

        return {"result": f"Unknown action: {ActionOrPrompt}"}


# Створює адаптер Nova для системного реєстру.
def SetupAdapter() -> NovaAdapter:
    return NovaAdapter()


REGISTRY.Register("Technical.Engineering.NovaAdapter", NovaAdapter)
