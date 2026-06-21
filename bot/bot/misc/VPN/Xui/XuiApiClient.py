"""
Async клиент для работы с API x-ui (3x-ui) панелей.
Поддерживает аутентификацию через API токен (Bearer) и через логин/пароль.
Совместим со старыми (alireza/xui) и новыми (sanaei/3x-ui) версиями панели.
"""
import json
import logging
import random
import string
from typing import Optional, List, Any, Dict, Tuple

import httpx

log = logging.getLogger(__name__)

# API пути для разных версий панели
NEW_API_PREFIX = '/panel/api/inbounds'   # sanaei / 3x-ui v2+
OLD_API_PREFIX = '/xui/API/inbounds'    # alireza / старые версии


class XuiClient:
    """
    Async HTTP клиент для x-ui / 3x-ui.

    Поддерживает:
    - Два режима аутентификации: Bearer токен или cookie-сессия (логин/пароль)
    - Автоматическое определение версии панели (новая / старая)
    - Парсинг клиентов из обоих форматов (settings JSON и clientStats)
    """

    def __init__(
        self,
        host: str,
        token: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        verify_ssl: bool = False,
    ):
        self.host = host.rstrip('/')
        self.token = token
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self._session_cookie: Optional[str] = None
        self._api_prefix: Optional[str] = None  # авто-определяется при первом вызове

        self._base_headers: Dict[str, str] = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        if self.token:
            self._base_headers['Authorization'] = f'Bearer {self.token}'

    async def login(self) -> None:
        """Выполняет вход через логин/пароль и сохраняет сессионную cookie."""
        if self.token:
            return
        if not self.username or not self.password:
            raise ValueError("Необходимо указать token или username/password")

        url = f'{self.host}/login'
        data = {'username': self.username, 'password': self.password}

        async with httpx.AsyncClient(verify=self.verify_ssl) as client:
            resp = await client.post(url, json=data, headers=self._base_headers)
            resp.raise_for_status()
            result = resp.json()
            if not result.get('success'):
                raise PermissionError(
                    f"Ошибка входа в x-ui: {result.get('msg', 'Unknown error')}"
                )
            self._session_cookie = resp.headers.get('set-cookie', '')
            log.info("Успешный вход в x-ui панель")

    def _get_headers(self) -> Dict[str, str]:
        headers = dict(self._base_headers)
        if self._session_cookie:
            headers['Cookie'] = self._session_cookie
        return headers

    async def _get(self, endpoint: str) -> Any:
        url = f'{self.host}/{endpoint.lstrip("/")}'
        async with httpx.AsyncClient(verify=self.verify_ssl) as client:
            resp = await client.get(url, headers=self._get_headers())
            resp.raise_for_status()
            return resp.json()

    async def _post(self, endpoint: str, data: Any = None) -> Any:
        url = f'{self.host}/{endpoint.lstrip("/")}'
        async with httpx.AsyncClient(verify=self.verify_ssl) as client:
            resp = await client.post(
                url,
                content=json.dumps(data) if data else None,
                headers=self._get_headers()
            )
            resp.raise_for_status()
            return resp.json()

    # ───────────────── Авто-определение версии панели ─────────────────

    async def _detect_api_prefix(self) -> str:
        """
        Определяет версию API панели: пробует новый путь, при ошибке — старый.
        Результат кэшируется на весь жизненный цикл объекта.
        """
        if self._api_prefix:
            return self._api_prefix

        # Пробуем новый API (sanaei / 3x-ui v2+)
        try:
            result = await self._get(f'{NEW_API_PREFIX}/list')
            if isinstance(result, dict) and 'success' in result:
                self._api_prefix = NEW_API_PREFIX
                log.info("Определена новая версия API панели (sanaei/3x-ui): %s", NEW_API_PREFIX)
                return self._api_prefix
        except Exception:
            pass

        # Пробуем старый API (alireza / xui)
        try:
            result = await self._get(f'{OLD_API_PREFIX}/list')
            if isinstance(result, dict) and 'success' in result:
                self._api_prefix = OLD_API_PREFIX
                log.info("Определена старая версия API панели (alireza/xui): %s", OLD_API_PREFIX)
                return self._api_prefix
        except Exception:
            pass

        # По умолчанию используем новый
        self._api_prefix = NEW_API_PREFIX
        log.warning("Не удалось определить версию панели, используем %s", NEW_API_PREFIX)
        return self._api_prefix

    # ───────────────── Парсинг клиентов (мультиверсионный) ─────────────────

    @staticmethod
    def _parse_clients_from_inbound(inbound: Dict) -> List[Dict]:
        """
        Извлекает список клиентов из inbound с поддержкой обоих форматов:
        - Новые версии: поле clientStats (трафик) + settings (config)
        - Старые версии: clients внутри settings JSON строки

        Объединяет config-данные (uuid, subId, flow) со статистикой (трафик).
        """
        client_stats = inbound.get('clientStats') or []

        # Парсим конфиг-данные клиентов из поля settings
        settings_clients: List[Dict] = []
        raw_settings = inbound.get('settings', '{}')
        try:
            if isinstance(raw_settings, str):
                settings_clients = json.loads(raw_settings).get('clients', [])
            elif isinstance(raw_settings, dict):
                settings_clients = raw_settings.get('clients', [])
        except (json.JSONDecodeError, AttributeError):
            pass

        if not settings_clients and not client_stats:
            return []

        # Если нет settings_clients — используем только статистику
        if not settings_clients:
            return list(client_stats)

        # Объединяем config + статистику по email
        stats_by_email: Dict[str, Dict] = {
            c.get('email'): c for c in client_stats if c.get('email')
        }
        result = []
        for c in settings_clients:
            email = c.get('email', '')
            merged = dict(c)
            if email in stats_by_email:
                # Статистика дополняет, но не перезаписывает config-поля (uuid, subId, flow)
                stat = dict(stats_by_email[email])
                stat.update(merged)  # config-поля имеют приоритет
                merged = stat
            result.append(merged)

        return result

    @staticmethod
    def _generate_sub_id(length: int = 16) -> str:
        """Генерирует уникальный subId для ссылки подписки клиента."""
        return ''.join(
            random.choices(string.ascii_lowercase + string.digits, k=length)
        )

    # ───────────────── Inbound API ─────────────────

    async def get_inbounds(self) -> List[Dict]:
        """Возвращает список всех inbound-подключений."""
        prefix = await self._detect_api_prefix()
        result = await self._get(f'{prefix}/list')
        if result.get('success'):
            return result.get('obj', [])
        raise RuntimeError(f"Ошибка получения inbounds: {result.get('msg')}")

    async def get_inbound(self, inbound_id: int) -> Optional[Dict]:
        """Возвращает конкретный inbound по ID."""
        inbounds = await self.get_inbounds()
        for inbound in inbounds:
            if inbound.get('id') == inbound_id:
                return inbound
        return None

    # ───────────────── Client API ─────────────────

    async def get_client_by_email(self, email: str) -> Optional[Dict]:
        """
        Получает данные клиента по email.
        Пробует API endpoint, при неудаче ищет напрямую в settings inbound.
        """
        prefix = await self._detect_api_prefix()
        try:
            result = await self._get(f'{prefix}/getClientTraffics/{email}')
            if result.get('success') and result.get('obj'):
                traffic_data = result['obj']
                # Дополняем config-полями (subId, uuid, flow) из settings inbound
                try:
                    inbounds = await self.get_inbounds()
                    for inbound in inbounds:
                        clients = self._parse_clients_from_inbound(inbound)
                        for c in clients:
                            if c.get('email') == email:
                                # Config-поля дополняют статистику
                                merged = dict(traffic_data)
                                merged.update({
                                    k: v for k, v in c.items()
                                    if k not in merged or not merged[k]
                                })
                                return merged
                except Exception:
                    pass
                return traffic_data
        except Exception as e:
            log.debug("getClientTraffics не доступен для %s: %s", email, e)

        # Fallback: поиск напрямую в settings всех inbound (совместимость со старыми версиями)
        try:
            inbounds = await self.get_inbounds()
            for inbound in inbounds:
                clients = self._parse_clients_from_inbound(inbound)
                for c in clients:
                    if c.get('email') == email:
                        return c
        except Exception as e:
            log.warning("Fallback поиск клиента %s не удался: %s", email, e)

        return None

    async def add_client(
        self,
        inbound_id: int,
        client_uuid: str,
        email: str,
        flow: str = 'xtls-rprx-vision',
        limit_ip: int = 0,
        total_gb: int = 0,
        enable: bool = True,
        sub_id: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """
        Добавляет нового клиента в inbound.

        Returns:
            Tuple[bool, str]: (успех операции, sub_id клиента)
        """
        if sub_id is None:
            sub_id = self._generate_sub_id()

        client_data = {
            'id': client_uuid,
            'flow': flow,
            'email': email,
            'limitIp': limit_ip,
            'totalGB': total_gb,
            'expiryTime': 0,
            'enable': enable,
            'tgId': '',
            'subId': sub_id,
            'reset': 0,
        }
        payload = {
            'id': inbound_id,
            'settings': json.dumps({'clients': [client_data]}),
        }
        prefix = await self._detect_api_prefix()
        try:
            result = await self._post(f'{prefix}/addClient', payload)
            return result.get('success', False), sub_id
        except Exception as e:
            log.error("Ошибка добавления клиента: %s", e)
            return False, sub_id

    async def delete_client(self, inbound_id: int, client_uuid: str) -> bool:
        """Удаляет клиента из inbound по UUID."""
        prefix = await self._detect_api_prefix()
        try:
            result = await self._post(
                f'{prefix}/{inbound_id}/delClient/{client_uuid}'
            )
            return result.get('success', False)
        except Exception as e:
            log.error("Ошибка удаления клиента: %s", e)
            return False

    async def get_client_traffic(self, email: str) -> Optional[float]:
        """Возвращает использованный трафик клиента в ГБ."""
        client = await self.get_client_by_email(email)
        if client is None:
            return None
        bytes_size = (client.get('up') or 0) + (client.get('down') or 0)
        return round(bytes_size / (1024 ** 3), 2)

    async def get_all_clients(self, inbound_id: int) -> Optional[List[Dict]]:
        """Возвращает список всех клиентов inbound-подключения."""
        inbound = await self.get_inbound(inbound_id)
        if inbound is None:
            return None
        clients = self._parse_clients_from_inbound(inbound)
        if not clients:
            # Последний fallback на clientStats
            return inbound.get('clientStats', [])
        return clients
