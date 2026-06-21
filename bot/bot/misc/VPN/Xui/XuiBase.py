import re
from abc import ABC
from typing import Optional

from bot.misc.VPN.Xui.XuiApiClient import XuiClient
from bot.misc.VPN.BaseVpn import BaseVpn


class XuiBase(BaseVpn, ABC):

    NAME_VPN: str
    POST_FIX: str

    def __init__(self, server):
        if server.connection_method:
            self.type_con = 'https://'
        else:
            self.type_con = 'http://'

        full_address = f'{self.type_con}{server.ip}'
        self.adress = get_domain(server.ip)
        self.server_ip = server.ip  # полный IP (может содержать порт, напр. 1.2.3.4:2053)

        # Путь подписки Happ (None если не задан — ссылка не выдаётся)
        self.sub_path: Optional[str] = getattr(server, 'sub_path', None)

        # Создаём клиент: с токеном или с логином/паролем
        if server.api_token:
            self.xui = XuiClient(
                host=full_address,
                token=server.api_token,
                verify_ssl=False,
            )
        else:
            self.xui = XuiClient(
                host=full_address,
                username=server.login or '',
                password=server.password or '',
                verify_ssl=False,
            )

        self.inbound_id = int(server.inbound_id)
        self.free_server = server.free_server

    async def login(self):
        """Аутентификация: при токене автоматически, при логине/пароле — через cookie."""
        await self.xui.login()

    async def get_inbound_server(self):
        try:
            return await self.xui.get_inbound(self.inbound_id)
        except Exception:
            return None

    async def get_all_user_server(self):
        try:
            return await self.xui.get_all_clients(self.inbound_id)
        except Exception:
            return None

    async def get_client_traffic(self, name):
        try:
            return await self.xui.get_client_traffic(name)
        except Exception:
            return None

    def _build_sub_url(self, client: dict) -> Optional[str]:
        """
        Строит ссылку подписки Happ для клиента.

        Формат: {protocol}{server_ip}/{sub_path}/{subId}
        Порт берётся из server_ip если задан (например, '1.2.3.4:2053').

        Returns:
            str если sub_path задан и у клиента есть subId, иначе None.
        """
        if not self.sub_path:
            return None

        sub_id = (
            client.get('subId')
            or client.get('sub_id')
            or ''
        )
        if not sub_id:
            return None

        return f'{self.type_con}{self.server_ip}/{self.sub_path.strip("/")}/{sub_id}'


def get_domain(url: str) -> str:
    """
    Извлекает домен или IP-адрес из переданной строки.
    Не включает порт — порт остаётся в server_ip для построения subscription URL.

    :param url: Строка с URL или адресом (может быть ip:port).
    :return: Домен или IP-адрес без порта.
    """
    pattern = r"^(?:https?://)?([a-zA-Z0-9.-]+)(?::\d+)?(?:/.*)?$"
    match = re.match(pattern, url)
    if match:
        return match.group(1)
    raise ValueError("Invalid URL server")
