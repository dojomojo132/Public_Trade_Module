"""
rdbg_client.py — HTTP/XML-клиент протокола RDBG для 1С:Предприятие 8.3.27.

Протокол: POST http://<host>:<port>/<endpoint>
          Content-Type: application/xml; charset=utf-8
          Тело: XML-пакет команды

Основные эндпоинты dbgs.exe:
  /e1crdbg/dbg/rdbgController/...
"""

import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from typing import Any


NS_DBGUI = "http://v8.1c.ru/8.3/debugger/debugBaseData"
NS_DBGCMD = "http://v8.1c.ru/8.3/debugger"

_BASE_HEADERS = {
    "Content-Type": "application/xml; charset=utf-8",
    "Accept": "application/xml",
}

_STEP_KINDS = {
    "over": "StepOver",
    "into": "StepIn",
    "out": "StepOut",
}


class RdbgError(Exception):
    """Ошибка коммуникации с dbgs.exe."""


class RdbgClient:
    """
    Низкоуровневый HTTP-клиент RDBG.

    Параметры
    ----------
    host : str
        Хост dbgs.exe (обычно 'localhost').
    port : int
        Порт, на котором слушает dbgs.exe.
    timeout : int
        Таймаут HTTP-запроса в секундах.
    """

    def __init__(self, host: str = "localhost", port: int = 1550, timeout: int = 10) -> None:
        self.base_url = f"http://{host}:{port}/e1crdbg/dbg/rdbgController"
        self.timeout = timeout

    # ------------------------------------------------------------------
    # Вспомогательные методы
    # ------------------------------------------------------------------

    def _post(self, endpoint: str, body: str) -> ET.Element:
        url = f"{self.base_url}/{endpoint}"
        data = body.encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=_BASE_HEADERS, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read()
        except urllib.error.URLError as exc:
            raise RdbgError(f"HTTP error [{url}]: {exc}") from exc

        if not raw:
            return ET.Element("empty")
        try:
            return ET.fromstring(raw.decode("utf-8"))
        except ET.ParseError as exc:
            raise RdbgError(f"XML parse error: {exc}  raw={raw[:200]}") from exc

    @staticmethod
    def _to_str(elem: ET.Element | None) -> str:
        if elem is None:
            return ""
        return ET.tostring(elem, encoding="unicode")

    # ------------------------------------------------------------------
    # Управление сессией
    # ------------------------------------------------------------------

    def attach(self, ib_alias: str = "ptm") -> None:
        """Присоединить отладчик к ИБ."""
        body = (
            f'<attachDebugUI xmlns="{NS_DBGCMD}">'
            f'  <infoBaseAlias>{ib_alias}</infoBaseAlias>'
            f"</attachDebugUI>"
        )
        self._post("attachDebugUI", body)

    def detach(self) -> None:
        """Отсоединить отладчик от всех ИБ."""
        body = f'<detachDebugUI xmlns="{NS_DBGCMD}"/>'
        self._post("detachDebugUI", body)

    # ------------------------------------------------------------------
    # Точки останова
    # ------------------------------------------------------------------

    def set_breakpoints(self, module_id: str, lines: list[int]) -> None:
        """
        Установить точки останова.

        Параметры
        ----------
        module_id : str
            UUID модуля в формате 'ObjectUUID:ModuleUUID'.
        lines : list[int]
            Список номеров строк (1-based).
        """
        bps_xml = "".join(
            f'<breakpoint><line>{ln}</line></breakpoint>' for ln in lines
        )
        body = (
            f'<setBreakpoints xmlns="{NS_DBGCMD}">'
            f"  <moduleId>{module_id}</moduleId>"
            f"  <breakpoints>{bps_xml}</breakpoints>"
            f"</setBreakpoints>"
        )
        self._post("setBreakpoints", body)

    def clear_breakpoints(self, module_id: str | None = None) -> None:
        """Сбросить точки останова (все или для конкретного модуля)."""
        inner = f"<moduleId>{module_id}</moduleId>" if module_id else ""
        body = (
            f'<clearBreakpoints xmlns="{NS_DBGCMD}">'
            f"  {inner}"
            f"</clearBreakpoints>"
        )
        self._post("clearBreakpoints", body)

    # ------------------------------------------------------------------
    # Управление выполнением
    # ------------------------------------------------------------------

    def _send_step(self, kind: str) -> None:
        tag = _STEP_KINDS[kind]
        body = f'<{tag} xmlns="{NS_DBGCMD}"/>'
        self._post(tag[0].lower() + tag[1:], body)

    def step_over(self) -> None:
        self._send_step("over")

    def step_into(self) -> None:
        self._send_step("into")

    def step_out(self) -> None:
        self._send_step("out")

    def continue_execution(self) -> None:
        body = f'<continueExecution xmlns="{NS_DBGCMD}"/>'
        self._post("continueExecution", body)

    # ------------------------------------------------------------------
    # Инспекция состояния
    # ------------------------------------------------------------------

    def get_call_stack(self) -> list[dict[str, Any]]:
        """
        Вернуть стек вызовов текущего потока.

        Возвращает
        ----------
        list[dict]
            Каждый элемент: {'module': str, 'line': int, 'name': str}.
        """
        body = f'<getCallStack xmlns="{NS_DBGCMD}"/>'
        root = self._post("getCallStack", body)

        frames = []
        for frame in root.findall(".//{%s}frame" % NS_DBGUI):
            module = (frame.findtext(".//{%s}moduleId" % NS_DBGUI) or "").strip()
            line_text = (frame.findtext(".//{%s}lineNo" % NS_DBGUI) or "0").strip()
            name = (frame.findtext(".//{%s}name" % NS_DBGUI) or "").strip()
            frames.append({"module": module, "line": int(line_text), "name": name})
        return frames

    def get_local_variables(self) -> list[dict[str, Any]]:
        """
        Вернуть локальные переменные текущего фрейма.

        Возвращает
        ----------
        list[dict]
            Каждый элемент: {'name': str, 'value': str, 'type': str}.
        """
        body = f'<getLocalVariables xmlns="{NS_DBGCMD}"/>'
        root = self._post("getLocalVariables", body)

        variables = []
        for var in root.findall(".//{%s}variable" % NS_DBGUI):
            name = (var.findtext(".//{%s}name" % NS_DBGUI) or "").strip()
            value = (var.findtext(".//{%s}value" % NS_DBGUI) or "").strip()
            vtype = (var.findtext(".//{%s}type" % NS_DBGUI) or "").strip()
            variables.append({"name": name, "value": value, "type": vtype})
        return variables

    def evaluate(self, expression: str) -> str:
        """
        Вычислить BSL-выражение (работает только при остановке на breakpoint).

        Параметры
        ----------
        expression : str
            Произвольное BSL-выражение.

        Возвращает
        ----------
        str
            Строковое представление результата.
        """
        body = (
            f'<evaluate xmlns="{NS_DBGCMD}">'
            f"  <expression><![CDATA[{expression}]]></expression>"
            f"</evaluate>"
        )
        root = self._post("evaluate", body)
        value_elem = root.find(".//{%s}value" % NS_DBGUI)
        if value_elem is not None and value_elem.text:
            return value_elem.text.strip()
        return self._to_str(root)

    # ------------------------------------------------------------------
    # Статус сессии
    # ------------------------------------------------------------------

    def get_status(self) -> dict[str, Any]:
        """Вернуть статус отладчика (подключён / остановлен / работает)."""
        body = f'<getDebuggerStatus xmlns="{NS_DBGCMD}"/>'
        try:
            root = self._post("getDebuggerStatus", body)
            state = (root.findtext(".//{%s}state" % NS_DBGUI) or "unknown").strip()
            return {"connected": True, "state": state}
        except RdbgError:
            return {"connected": False, "state": "disconnected"}
