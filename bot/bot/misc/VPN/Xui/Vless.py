import json
import uuid
from typing import Optional, Tuple

from bot.misc.VPN.Xui.XuiBase import XuiBase
from bot.misc.util import CONFIG


class Vless(XuiBase):
    NAME_VPN = 'Vless 🐊'
    POST_FIX = 'vl'

    def __init__(self, server):
        super().__init__(server)

    async def get_client(self, name):
        client = await self.xui.get_client_by_email(name)
        if client is None:
            return 'User not found'
        return client

    async def add_client(self, name, limit_ip, limit_gb) -> bool:
        try:
            new_uuid = str(uuid.uuid4())
            success, _ = await self.xui.add_client(
                inbound_id=self.inbound_id,
                client_uuid=new_uuid,
                email=str(name),
                flow='xtls-rprx-vision',
                limit_ip=limit_ip,
                total_gb=limit_gb * 1073741824,
                enable=True,
            )
            return success
        except Exception:
            return False

    async def delete_client(self, telegram_id) -> bool:
        try:
            client = await self.xui.get_client_by_email(telegram_id)
            if client is None:
                return True
            client_uuid = client.get('id') or client.get('uuid', '')
            if not client_uuid:
                return True
            return await self.xui.delete_client(
                inbound_id=self.inbound_id,
                client_uuid=client_uuid,
            )
        except Exception:
            return True

    async def get_key_user(self, name, name_key) -> Tuple[Optional[str], Optional[str]]:
        """
        Возвращает (vless_ключ, ссылка_подписки).
        Ссылка подписки будет None если sub_path не задан или панель не поддерживает subId.
        """
        inbound = await self.get_inbound_server()
        client = await self.get_client(name)

        if client == 'User not found' or client is None:
            if self.free_server:
                await self.add_client(name, CONFIG.limit_ip, CONFIG.limit_gb_free)
            else:
                await self.add_client(name, CONFIG.limit_ip, CONFIG.limit_GB)
            client = await self.get_client(name)

        if inbound is None or client is None or client == 'User not found':
            return None, None

        stream_settings = json.loads(inbound.get('streamSettings', '{}'))
        reality_settings = stream_settings.get('realitySettings', {})
        settings = reality_settings.get('settings', {})

        fp = settings.get('fingerprint', '')
        pbk = settings.get('publicKey', '')

        client_flow = client.get('flow', '') or ''
        flow = f'&flow={client_flow}' if client_flow else ''

        client_uuid = client.get('id') or client.get('uuid', '')
        port = inbound.get('port', '')

        key = (
            f'vless://{client_uuid}@'
            f'{self.adress}:{port}?'
            f'type={stream_settings.get("network", "tcp")}&'
            f'security={stream_settings.get("security", "reality")}&'
            f'pbk={pbk}&'
            f'fp={fp}&'
            f'sni={reality_settings.get("serverNames", [""])[0]}&'
            f'sid={reality_settings.get("shortIds", [""])[0]}&'
            f'spx=%2F'
            f'{flow}'
            f'#{name_key}'
        )

        # Строим ссылку подписки если задан путь подписки
        sub_url = self._build_sub_url(client)

        return key, sub_url
