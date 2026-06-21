import logging

from bot.misc.VPN.Xui.Vless import Vless
from bot.misc.util import CONFIG

log = logging.getLogger(__name__)


class ServerManager:
    VPN_TYPES = {
        1: Vless,
    }

    def __init__(self, server):
        try:
            self.client = self.VPN_TYPES.get(server.type_vpn)(server)
        except Exception as e:
            log.error('Error initializing ServerManager: ', exc_info=e)

    async def login(self):
        await self.client.login()

    async def get_all_user(self):
        try:
            return await self.client.get_all_user_server()
        except Exception as e:
            log.error('Error get all user server', exc_info=e)
            return None

    async def get_user(self, name, key_id):
        try:
            name_str = f'{name}.{key_id}.{self.client.POST_FIX}'
            return await self.client.get_client(str(name_str))
        except Exception as e:
            log.error('Error get user server', exc_info=e)

    async def get_client_traffic(self, name, key_id):
        try:
            name_str = f'{name}.{key_id}.{self.client.POST_FIX}'
            return await self.client.get_client_traffic(str(name_str))
        except Exception as e:
            log.error('Error get user server', exc_info=e)

    async def add_client(
            self,
            name,
            key_id,
            limit_ip=CONFIG.limit_ip,
            limit_gb=CONFIG.limit_GB
    ):
        try:
            name_str = f'{name}.{key_id}.{self.client.POST_FIX}'
            return await self.client.add_client(str(name_str), limit_ip, limit_gb)
        except Exception as e:
            log.error('Error add client server', exc_info=e)

    async def delete_client(self, name, key_id):
        try:
            name_str = f'{name}.{key_id}.{self.client.POST_FIX}'
            await self.client.delete_client(str(name_str))
            return True
        except Exception as e:
            log.error('Error delete client server', exc_info=e)
            return False

    async def get_key(self, name, name_key, key_id):
        try:
            name_str = f'{name}.{key_id}.{self.client.POST_FIX}'
            name_key = CONFIG.name + ' | ' + name_key
            result = await self.client.get_key_user(str(name_str), str(name_key))
            if isinstance(result, tuple):
                return result  # (key, sub_url)
            return result, None  # обратная совместимость
        except Exception as e:
            log.error('Error get key server', exc_info=e)
            return None, None
