from abc import ABC, abstractmethod
from typing import Optional, Tuple


class BaseVpn(ABC):

    NAME_VPN: str
    POST_FIX: str

    @abstractmethod
    async def get_all_user_server(self):
        pass

    @abstractmethod
    async def get_client(self, name):
        pass

    @abstractmethod
    async def add_client(self, name, limit_ip, limit_gb):
        pass

    @abstractmethod
    async def delete_client(self, telegram_id):
        pass

    @abstractmethod
    async def get_key_user(self, name, name_key) -> Tuple[Optional[str], Optional[str]]:
        """
        Возвращает кортеж (vpn_key, subscription_url).
        subscription_url может быть None если подписка не настроена.
        """
        pass
